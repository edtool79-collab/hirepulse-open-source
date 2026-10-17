"""Render directory metadata locally; never publish or access the network."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_URL = "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json"


def render(root: Path = ROOT) -> dict[str, str]:
    """Use one editable identity source; directory formats need literal copies."""
    identity = json.loads((root / "publishing.json").read_text(encoding="utf-8"))
    owner, repo = identity["github_owner"], identity["github_repo"]
    if not re.fullmatch(r"[A-Za-z0-9-]+", owner) or not re.fullmatch(r"[A-Za-z0-9._-]+", repo):
        raise ValueError("Use a GitHub username and repository name, not URLs")
    # Read only literal release fields without requiring tomllib (Python 3.10).
    project = (root / "pyproject.toml").read_text(encoding="utf-8")
    package = re.search(r'^name = "([^"]+)"$', project, re.MULTILINE).group(1)
    version = re.search(r'^version = "([^"]+)"$', project, re.MULTILINE).group(1)
    catalog = root / "src/hirepulse_tools/_catalog.py"
    # Parse literals rather than importing the package (no SDK or credentials).
    import ast
    mapping = ast.literal_eval(ast.parse(catalog.read_text(encoding="utf-8")).body[1].value)
    hosted = "https://mcp.apify.com?tools=" + ",".join(f"hirepulse/{slug}" for slug in mapping.values())
    name = f"io.github.{owner}/{repo}"
    server = {
        "$schema": SCHEMA_URL,
        "name": name,
        "title": "HirePulse tools",
        "description": "Apify tools for products, Google ads, company signals, jobs, keywords, SEO and YouTube transcripts.",
        "version": version,
        "repository": {"url": f"https://github.com/{owner}/{repo}", "source": "github"},
        "remotes": [{
            "type": "streamable-http", "url": hosted,
            "headers": [{"name": "Authorization", "description": "Apify authentication: Bearer followed by your Apify token.", "isRequired": True, "isSecret": True}],
        }],
        "packages": [{
            "registryType": "pypi", "registryBaseUrl": "https://pypi.org",
            "identifier": package, "version": version, "runtimeHint": "uvx",
            "runtimeArguments": [
                {"type": "named", "name": "--from", "value": f"{package}[mcp]=={version}"},
            ],
            "packageArguments": [{"type": "positional", "value": "hirepulse-mcp"}],
            "transport": {"type": "stdio"},
            "environmentVariables": [{"name": "APIFY_TOKEN", "description": "Apify token provided through the process environment only.", "isRequired": True, "isSecret": True}],
        }],
    }
    glama = {"$schema": "https://glama.ai/mcp/schemas/server.json", "maintainers": [owner]}
    readme = (root / "README.md").read_text(encoding="utf-8")
    readme = re.sub(r"\n<!-- mcp-name: .*? -->\n", "", readme)
    readme = readme.replace("# HirePulse tools\n", f"# HirePulse tools\n\n<!-- mcp-name: {name} -->\n", 1)
    return {"server.json": json.dumps(server, indent=2) + "\n", "glama.json": json.dumps(glama, indent=2) + "\n", "README.md": readme}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check generated metadata without changing files")
    args = parser.parse_args()
    for name, content in render().items():
        path = ROOT / name
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                raise SystemExit(f"Stale generated metadata: {name}; run python scripts/render_metadata.py")
        else:
            path.write_text(content, encoding="utf-8")
    print("Directory metadata is current." if args.check else "Rendered directory metadata locally.")


if __name__ == "__main__":
    main()
