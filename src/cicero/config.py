import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class Config:
    discord_token: str
    discord_guild_id: int
    kubeconfig_path: str | None

    @classmethod
    def from_env(cls) -> "Config":
        load_dotenv()

        discord_token = os.getenv("DISCORD_TOKEN")
        if not discord_token:
            raise RuntimeError("Environment variable 'DISCORD_TOKEN' is not set")

        raw_guild_id = os.getenv("DISCORD_GUILD_ID")
        if not raw_guild_id:
            raise RuntimeError("Environment variable 'DISCORD_GUILD_ID' is not set")
        discord_guild_id = int(raw_guild_id)

        kubeconfig_path = os.getenv("KUBECONFIG_PATH") or None

        return cls(
            discord_token=discord_token,
            discord_guild_id=discord_guild_id,
            kubeconfig_path=kubeconfig_path,
        )
