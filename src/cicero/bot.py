import discord
from discord.ext import commands
from kubernetes import client


class CiceroBot(commands.Bot):
    def __init__(self, guild_id: int, k8s_api: client.CoreV1Api) -> None:
        intents = discord.Intents.default()
        # required even when not used
        super().__init__(command_prefix="!", intents=intents)
        self.guild_id = guild_id
        self.k8s_api = k8s_api

    async def setup_hook(self) -> None:
        await self.load_extension("cicero.cogs.status")
        guild = discord.Object(id=self.guild_id)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

    async def on_ready(self) -> None:
        assert self.user is not None
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")
