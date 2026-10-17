"""Validate directory drafts using fetched schemas, entirely offline."""

import json
import runpy
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft7Validator, FormatChecker, ValidationError

from hirepulse_tools._catalog import TOOL_SLUGS

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("filename,schema_name", [
    ("server.json", "mcp-server.schema.json"),
    ("glama.json", "glama-server.schema.json"),
])
def test_directory_json_against_official_schema(filename, schema_name):
    schema = json.loads((ROOT / "tests/fixtures" / schema_name).read_text(encoding="utf-8"))
    Draft7Validator.check_schema(schema)
    instance = json.loads((ROOT / filename).read_text(encoding="utf-8"))
    assert instance["$schema"] == schema["$id"]
    checker = FormatChecker()
    assert "uri" in checker.checkers
    Draft7Validator(schema, format_checker=checker).validate(instance)


def test_registry_transports_cover_exactly_eight_actors_and_mcp_extra():
    server = json.loads((ROOT / "server.json").read_text(encoding="utf-8"))
    remote = server["remotes"][0]
    url = "https://mcp.apify.com?tools=" + ",".join(f"hirepulse/{slug}" for slug in TOOL_SLUGS.values())
    assert remote["url"] == url
    assert url in (ROOT / "README.md").read_text(encoding="utf-8")
    assert remote["type"] == "streamable-http"
    assert remote["headers"][0]["isSecret"] and remote["headers"][0]["isRequired"]
    package = server["packages"][0]
    assert package["transport"]["type"] == "stdio"
    assert package["runtimeHint"] == "uvx"
    assert package["runtimeArguments"] == [{"type": "named", "name": "--from", "value": f"hirepulse-tools[mcp]=={server['version']}"}]
    assert package["packageArguments"] == [{"type": "positional", "value": "hirepulse-mcp"}]
    assert package["environmentVariables"][0]["name"] == "APIFY_TOKEN"
    assert package["environmentVariables"][0]["isSecret"]


def test_one_editable_identity_source_and_generated_files_are_current(tmp_path):
    render = runpy.run_path(str(ROOT / "scripts/render_metadata.py"))["render"]
    for name, expected in render().items():
        assert (ROOT / name).read_text(encoding="utf-8") == expected
    # Changing the single source updates every required literal copy together.
    for name in ("publishing.json", "pyproject.toml", "README.md", "src/hirepulse_tools/_catalog.py"):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text((ROOT / name).read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "publishing.json").write_text(json.dumps({"github_owner": "example-owner", "github_repo": "example-repo"}), encoding="utf-8")
    rendered = render(tmp_path)
    server = json.loads(rendered["server.json"])
    assert server["name"] == "io.github.example-owner/example-repo"
    assert server["repository"]["url"] == "https://github.com/example-owner/example-repo"
    assert json.loads(rendered["glama.json"])["maintainers"] == ["example-owner"]
    assert "mcp-name: io.github.example-owner/example-repo" in rendered["README.md"]


def test_smithery_requires_only_secret_token_and_maps_environment():
    start = yaml.safe_load((ROOT / "smithery.yaml").read_text(encoding="utf-8"))["startCommand"]
    assert start["type"] == "stdio"
    schema = start["configSchema"]
    Draft7Validator.check_schema(schema)
    assert schema["required"] == ["apifyToken"]
    assert set(schema["properties"]) == {"apifyToken"}
    assert schema["properties"]["apifyToken"]["writeOnly"]
    assert schema["properties"]["apifyToken"]["x-secret"]
    for invalid in ({}, {"apifyToken": ""}, {"apifyToken": 1}, {"apifyToken": "your_token_here", "extra": True}):
        with pytest.raises(ValidationError):
            Draft7Validator(schema).validate(invalid)
    Draft7Validator(schema).validate({"apifyToken": "your_token_here"})
    command = start["commandFunction"]
    assert "command: 'python'" in command
    assert "args: ['-m', 'hirepulse_tools.mcp_server']" in command
    assert "APIFY_TOKEN: config.apifyToken" in command


def test_skill_frontmatter_and_exact_actors():
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    metadata = yaml.safe_load(skill.split("---", 2)[1])
    assert metadata["name"] == "hirepulse-tools" and metadata["description"]
    assert skill.count("Use this when...") == 8
    assert skill.count("Do NOT use for...") == 8
    for name, slug in TOOL_SLUGS.items():
        assert f"`hirepulse/{slug}`" in skill
        assert f"`{name}`" in skill
    assert "Workday" in skill and "seller ratings" in skill
