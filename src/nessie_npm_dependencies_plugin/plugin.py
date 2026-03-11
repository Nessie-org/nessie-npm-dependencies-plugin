from nessie_api.models import Action, plugin
import asyncio
from .fetch import build_dependency_graph
from typing import Any
from nessie_api.models import Graph

def load_graph(action: Action) -> Graph:
    return asyncio.run(build_dependency_graph(action.payload["Package Name"]))


@plugin("NPM Package Dependencies")
def npm_dependencies_plugin():
    handlers = {
        "load": load_graph,
    }
    requires = []
    setup_requires = {
        "Package Name": str
    }

    ret_dict = {
        "handlers": handlers,
        "requires": requires,
        "setup_requires": setup_requires,
    }
    return ret_dict