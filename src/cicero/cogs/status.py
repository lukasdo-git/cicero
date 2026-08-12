import asyncio

import discord
from discord import app_commands
from discord.ext import commands

from cicero import k8s
from cicero.bot import CiceroBot


class StatusCog(commands.Cog):
    def __init__(self, bot: CiceroBot) -> None:
        self.bot = bot

    @app_commands.command(
        name="ping", description="Check whether the bot is responsive"
    )
    async def ping(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Pong!")

    @app_commands.command(name="status", description="Show k3s cluster health")
    async def status(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        node_statuses = await asyncio.to_thread(k8s.get_node_statuses, self.bot.k8s_api)
        pod_summary = await asyncio.to_thread(k8s.get_pod_summary, self.bot.k8s_api)
        lines_node = [
            f"Node {node.name} is {'ready' if node.ready else 'not ready'}"
            for node in node_statuses
        ]
        lines_pod = (
            [
                f"Total pods: {pod_summary.total}",
                "Pods by phase:",
            ]
            + [f"  {phase}: {count}" for phase, count in pod_summary.by_phase.items()]
            + ["Unhealthy pods:" if pod_summary.unhealthy else "All pods are healthy"]
            + [f"  {pod}" for pod in pod_summary.unhealthy]
        )
        await interaction.followup.send(
            f"Cluster has {len(node_statuses)} nodes:\n"
            + "\n".join(lines_node)
            + "\n\nPods:\n"
            + "\n".join(lines_pod)
        )


async def setup(bot: CiceroBot) -> None:
    await bot.add_cog(StatusCog(bot))
