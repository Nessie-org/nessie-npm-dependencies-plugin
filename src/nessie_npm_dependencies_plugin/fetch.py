import asyncio
import aiohttp

from nessie_api.models import Node, Attribute, Graph, Edge, GraphType


NPM_REGISTRY = "https://registry.npmjs.org"
MAX_CONCURRENCY = 30




async def fetch_package(session, package):
    url = f"{NPM_REGISTRY}/{package}"

    try:
        async with session.get(url) as resp:
            if resp.status != 200:
                return None

            data = await resp.json()

    except Exception:
        return None

    latest = data.get("dist-tags", {}).get("latest")
    if not latest:
        return None

    version_data = data["versions"].get(latest, {})

    deps = version_data.get("dependencies", {})

    metadata = {
        "version": latest,
        "description": data.get("description", ""),
        "license": version_data.get("license", "")
    }

    return deps, metadata


async def worker(queue: asyncio.Queue, graph: Graph, visited: set[str], session: aiohttp.ClientSession, lock: asyncio.Lock, edge_counter: list[int]):
    while True:
        package = await queue.get()

        if package is None:
            queue.task_done()
            break

        result = await fetch_package(session, package)

        if result is None:
            queue.task_done()
            continue

        deps, metadata = result

        async with lock:
            node = graph.get_node(package)

            if node is None:
                node = Node(package)
                graph.add_node(node)

            for k, v in metadata.items():
                if v:
                    node.add_attribute(Attribute(k, v))

        for dep in deps:

            async with lock:
                if graph.get_node(dep) is None:
                    graph.add_node(Node(dep))

                edge_id = f"e{edge_counter[0]}"
                edge_counter[0] += 1

                source = graph.get_node(package)
                destination = graph.get_node(dep)
                if source is not None and destination is not None:
                    edge = Edge(edge_id, source, destination)
                    graph.add_edge(edge)

                if dep not in visited:
                    visited.add(dep)
                    await queue.put(dep)

        queue.task_done()


async def build_dependency_graph(root_package: str, max_packages: int=500):

    graph = Graph(root_package, GraphType.DIRECTED)

    visited = set([root_package])

    queue = asyncio.Queue()

    await queue.put(root_package)

    lock = asyncio.Lock()

    edge_counter = [0]

    async with aiohttp.ClientSession() as session:

        workers = [
            asyncio.create_task(
                worker(queue, graph, visited, session, lock, edge_counter)
            )
            for _ in range(MAX_CONCURRENCY)
        ]

        await queue.join()

        for _ in workers:
            await queue.put(None)

        await asyncio.gather(*workers)

    return graph



async def main():

    graph = await build_dependency_graph("express")

    print(graph)

    import json

    with open("npm_graph.json", "w") as f:
        json.dump(graph.to_dict(), f, indent=2)


if __name__ == "__main__":
    asyncio.run(main())