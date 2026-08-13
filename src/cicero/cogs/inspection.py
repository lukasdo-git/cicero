#########################
# Houses read-only commands for inspecting the cluster
# /nodes                            - returns a more detailed view of nodes in cluster with data like CPU and memory usage and capacity
# /pods [namespace]                 - returns a more detailed summary of pods in a specific namespace
# /describe <pod> <namespace>       - returns a detailed description of a specific pod in a specific namespace
# /logs <pod> <namespace> [lines]   - returns the logs of a specific pod in a specific namespace, with an optional number of lines to retrieve from the end of the logs (default is 100)

import asyncio

import discord
from discord import app_commands
from discord.ext import commands

from cicero import k8s
from cicero.bot import CiceroBot


class InspectionCog(commands.Cog):
    def __init__(self, bot: CiceroBot) -> None:
        self.bot = bot

    def is_healthy(self, pod: k8s.PodDetails) -> bool:
        return pod.ready or pod.phase == "Succeeded"

    @app_commands.command(
        name="nodes", description="Show detailed information about nodes in the cluster"
    )
    async def nodes(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        node_details = await asyncio.to_thread(k8s.get_node_details, self.bot.k8s_api)
        lines = [
            f"Node {node.name} ({'ready' if node.ready else 'not ready'})\n"
            f"  Kubelet: {node.kubelet_version} · CPU: {node.cpu_capacity} · Memory: {node.memory_capacity}"
            for node in node_details
        ]
        await interaction.followup.send(
            f"Cluster has {len(node_details)} nodes:\n\n" + "\n\n".join(lines)
        )

    @app_commands.command(
        name="pods", description="Show detailed information about pods in the cluster"
    )
    async def pods(
        self, interaction: discord.Interaction, namespace: str | None = None
    ) -> None:
        await interaction.response.defer()
        pod_details = await asyncio.to_thread(
            k8s.get_pod_details, self.bot.k8s_api, namespace
        )

        lines = []
        for pod in pod_details:
            indicator = "🟢" if self.is_healthy(pod) else "🔴"
            lines.append(
                f"{indicator} `{pod.namespace}/{pod.name}` "
                f"{pod.phase} · {pod.restarts} restarts · <t:{int(pod.creation_timestamp.timestamp())}:R>"
            )

        embed = discord.Embed(
            title=f"Pods in {namespace}" if namespace else "Pods (all namespaces)",
            description="\n".join(lines) or "No pods found.",
            color=discord.Color.green()
            if all(self.is_healthy(pod) for pod in pod_details)
            else discord.Color.orange(),
        )
        embed.set_footer(text=f"{len(pod_details)} pods")

        await interaction.followup.send(embed=embed)


async def setup(bot: CiceroBot) -> None:
    await bot.add_cog(InspectionCog(bot))
