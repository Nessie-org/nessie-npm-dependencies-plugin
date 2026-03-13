import asyncio

from nessie_api.models import Action, plugin, SetupRequirementType, Graph
from nessie_api.protocols import Context
from nessie_npm_dependencies_plugin.fetch import build_dependency_graph

def load_graph(action: Action, context: Context) -> Graph:
    return asyncio.run(build_dependency_graph(action.payload["Package Name"]))


@plugin("NPM Package Dependencies")
def npm_dependencies_plugin():
    handlers = {
        "load_graph": load_graph,
    }
    requires = []
    setup_requires = {
        "Package Name": SetupRequirementType.STRING
    }

    ret_dict = {
        "handlers": handlers,
        "requires": requires,
        "setup_requires": setup_requires,
    }
    return ret_dict