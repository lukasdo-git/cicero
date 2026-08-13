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


async def setup(bot: CiceroBot) -> None:
    await bot.add_cog(InspectionCog(bot))
