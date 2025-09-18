from __future__ import annotations

import json
from pathlib import Path

from lychee.infrastructure.config.yaml_config_repository import YamlConfigRepository
from lychee.infrastructure.project.project_repository import ProjectRepository


def test_build_project_from_config_and_topo(tmp_path: Path):
    root = tmp_path
    (root / "services" / "bar").mkdir(parents=True)
    (root / "services" / "foo").mkdir(parents=True)

    lychee_yaml = {
        "version": 1.0,
        "project": {"languages": ["python"], "workspace": {"services_dir": "services"}},
        "schemas": {"dir": "schemas", "output_path": ".lychee", "format": "json_schema"},
        "services": {
            "bar": {
                "type": "python",
                "path": str(Path("services/bar")),
                "runtime": {"port": 8001, "entry_point": "main:app"},
                "schemas": {"mount_dir": "models"},
            },
            "foo": {
                "type": "python",
                "path": str(Path("services/foo")),
                "dependencies": {"services": ["bar"]},
                "runtime": {"port": 8002, "entry_point": "main:app"},
                "schemas": {"mount_dir": "models"},
            },
        },
    }
    (root / "lychee.yaml").write_text(json.dumps(lychee_yaml), encoding="utf-8")

    cfg = YamlConfigRepository().load(root)
    project = ProjectRepository().build(cfg, root)

    # Service paths should be resolved under root
    assert project.get_service("bar").path == (root / "services/bar").resolve()
    assert project.get_service("foo").path == (root / "services/foo").resolve()

    # Topological order should have bar before foo
    order = project.topo_order()
    assert order.index("bar") < order.index("foo")

    # Schema mount dir preserved
    assert project.get_service("foo").schemas_mount_dir == "models"
