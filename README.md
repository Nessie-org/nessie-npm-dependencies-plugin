# nessie-npm-dependencies-plugin

A [Nessie Graph Explorer](https://github.com/Nessie-org) datasource plugin that generates interactive dependency graphs for any npm package, crawling the full transitive dependency tree via the npm registry.

## Overview

This plugin integrates with Nessie Graph Explorer to let you visualise npm package dependency trees as directed graphs. Provide a package name, and the plugin fetches its dependencies — and their dependencies — concurrently from the npm registry, building a complete directed graph with node metadata such as version, description, and license.

**Key features:**

- Full transitive dependency resolution (up to 500 packages by default)
- Concurrent fetching with up to 30 parallel workers for fast traversal
- Node attributes populated from live npm registry data (version, description, license)
- Directed graph output compatible with Nessie Graph Explorer
- Simple string-based setup — just enter a package name

## Requirements

- Python 3.9+
- A working installation of [Nessie Graph Explorer](https://github.com/Nessie-org) with `nessie-api >= 0.1.0`

## Installation

Install the plugin from PyPI:

```bash
pip install nessie-npm-dependencies-plugin
```

Or install directly from source:

```bash
git clone https://github.com/Nessie-org/nessie-npm-dependencies-plugin.git
cd nessie-npm-dependencies-plugin
pip install .
```

Once installed, the plugin is automatically discovered by Nessie Graph Explorer via its entry point (`nessie_plugins`). No manual registration is required.

## Usage

After installation, the **NPM Package Dependencies** datasource will appear in Nessie Graph Explorer.

1. Open Nessie Graph Explorer and create a new graph.
2. Select **NPM Package Dependencies** as the datasource.
3. Enter a **Package Name** (e.g. `express`, `react`, `lodash`).
4. Click **Load Graph**.

The plugin will fetch the package's dependency tree from the npm registry and render it as a directed graph. Each node represents an npm package and carries the following attributes where available:

| Attribute     | Description                          |
|---------------|--------------------------------------|
| `version`     | Latest published version             |
| `description` | Package description from npm         |
| `license`     | SPDX license identifier              |

Edges are directed from a package to each of its declared dependencies.

## How It Works

The plugin uses an async worker pool to crawl the npm registry concurrently:

1. The root package is enqueued.
2. Up to 30 async workers fetch each package's metadata from `https://registry.npmjs.org/<package>`.
3. Each package's latest-version dependencies are extracted and enqueued (if not yet visited).
4. Workers populate a shared `Graph` with `Node` and `Edge` objects, adding metadata attributes to each node.
5. Crawling stops when the queue is empty or 500 packages have been visited.

The result is a fully connected directed graph representing the transitive dependency tree.

## Configuration

The following constants in `fetch.py` can be adjusted for your environment:

| Constant          | Default | Description                                  |
|-------------------|---------|----------------------------------------------|
| `MAX_CONCURRENCY` | `30`    | Number of concurrent async HTTP workers      |
| `max_packages`    | `500`   | Maximum number of packages to traverse       |
| `NPM_REGISTRY`    | `https://registry.npmjs.org` | npm registry base URL  |

## Project Structure

```
nessie-npm-dependencies-plugin/
├── src/
│   └── nessie_npm_dependencies_plugin/
│       ├── __init__.py      # Package entry point; exports npm_dependencies_plugin
│       ├── plugin.py        # Nessie plugin definition and action handler
│       └── fetch.py         # Async dependency graph crawler
├── pyproject.toml
├── LICENSE
└── README.md
```

## Development

Clone the repository and install in editable mode:

```bash
git clone https://github.com/Nessie-org/nessie-npm-dependencies-plugin.git
cd nessie-npm-dependencies-plugin
pip install -e .
```

This project uses [Hatchling](https://hatch.pypa.io/) as its build backend, [Black](https://black.readthedocs.io/) for formatting, [Ruff](https://docs.astral.sh/ruff/) for linting, and [mypy](https://mypy.readthedocs.io/) for type checking.

Format and lint:

```bash
black src/
ruff check src/
mypy src/
```

You can also run the crawler standalone to produce a JSON graph file:

```bash
python src/nessie_npm_dependencies_plugin/fetch.py
# Outputs npm_graph.json for the 'express' package
```

## Contributing

Contributions are welcome. Please open an issue to discuss significant changes before submitting a pull request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes
4. Open a pull request against `master`

## License

MIT © [Nessie-org](https://github.com/Nessie-org). See [LICENSE](LICENSE) for details.