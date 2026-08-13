from dataclasses import dataclass

from kubernetes import client, config


def load_config(kubeconfig_path: str | None) -> None:
    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config(config_file=kubeconfig_path)


@dataclass
class NodeStatus:
    name: str
    ready: bool


@dataclass
class PodSummary:
    total: int
    by_phase: dict[str, int]
    unhealthy: list[str]


@dataclass
class NodeDetails:
    name: str
    ready: bool
    kubelet_version: str
    cpu_capacity: str
    memory_capacity: str


def get_node_statuses(api: client.CoreV1Api) -> list[NodeStatus]:
    nodes = api.list_node().items
    return [
        NodeStatus(
            name=node.metadata.name,
            ready=any(
                condition.type == "Ready" and condition.status == "True"
                for condition in node.status.conditions
            ),
        )
        for node in nodes
    ]


def _summarize_pods(pods: list) -> PodSummary:
    total = len(pods)
    by_phase: dict[str, int] = {}
    unhealthy: list[str] = []
    for pod in pods:
        phase = pod.status.phase
        by_phase[phase] = by_phase.get(phase, 0) + 1
        if phase not in ("Running", "Succeeded"):
            unhealthy.append(f"{pod.metadata.namespace}/{pod.metadata.name}")
    return PodSummary(total=total, by_phase=by_phase, unhealthy=unhealthy)


def get_pod_summary(api: client.CoreV1Api) -> PodSummary:
    return _summarize_pods(api.list_pod_for_all_namespaces().items)


def get_node_details(api: client.CoreV1Api) -> list[NodeDetails]:
    nodes = api.list_node().items
    return [
        NodeDetails(
            name=node.metadata.name,
            ready=any(
                condition.type == "Ready" and condition.status == "True"
                for condition in node.status.conditions
            ),
            kubelet_version=node.status.node_info.kubelet_version,
            cpu_capacity=node.status.capacity.get("cpu", "unknown"),
            memory_capacity=node.status.capacity.get("memory", "unknown"),
        )
        for node in nodes
    ]
