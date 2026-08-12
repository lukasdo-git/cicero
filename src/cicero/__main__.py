from kubernetes import client

from cicero import k8s
from cicero.bot import CiceroBot
from cicero.config import Config


def main() -> None:
    cfg = Config.from_env()
    k8s.load_config(cfg.kubeconfig_path)
    k8s_api = client.CoreV1Api()
    bot = CiceroBot(guild_id=cfg.discord_guild_id, k8s_api=k8s_api)
    bot.run(cfg.discord_token)


if __name__ == "__main__":
    main()
