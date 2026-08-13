import datetime
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


@dataclass
class PodDetails:
    name: str
    namespace: str
    phase: str
    ready: bool
    restarts: int
    creation_timestamp: datetime.datetime


def get_node_statuses(api: client.CoreV1Api) -> list[NodeStatus]:
    return [
        NodeStatus(name=node.name, ready=node.ready) for node in get_node_details(api)
    ]


def get_pod_summary(api: client.CoreV1Api, namespace: str | None = None) -> PodSummary:
    if namespace is None:
        pods = api.list_pod_for_all_namespaces().items
    else:
        pods = api.list_namespaced_pod(namespace).items
    total = len(pods)
    by_phase: dict[str, int] = {}
    unhealthy: list[str] = []
    for pod in pods:
        phase = pod.status.phase
        by_phase[phase] = by_phase.get(phase, 0) + 1
        if phase not in ("Running", "Succeeded"):
            unhealthy.append(f"{pod.metadata.namespace}/{pod.metadata.name}")
    return PodSummary(total=total, by_phase=by_phase, unhealthy=unhealthy)


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


def get_pod_details(
    api: client.CoreV1Api, namespace: str | None = None
) -> list[PodDetails]:
    if namespace is None:
        pods = api.list_pod_for_all_namespaces().items
    else:
        pods = api.list_namespaced_pod(namespace).items
    return [
        PodDetails(
            name=pod.metadata.name,
            namespace=pod.metadata.namespace,
            phase=pod.status.phase,
            ready=any(
                c.type == "Ready" and c.status == "True" for c in pod.status.conditions
            )
            if pod.status.conditions
            else False,
            restarts=sum(
                container.restart_count for container in pod.status.container_statuses
            )
            if pod.status.container_statuses
            else 0,
            creation_timestamp=pod.metadata.creation_timestamp,
        )
        for pod in pods
    ]
