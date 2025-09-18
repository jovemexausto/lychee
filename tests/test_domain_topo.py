from pathlib import Path

from lychee.domain.project import Project
from lychee.domain.service import Service


def test_topo_order_simple():
    root = Path(".")
    project = Project(root=root)
    project.add_service(Service(name="bar", path=root / "bar", language="python"))
    project.add_service(
        Service(name="foo", path=root / "foo", language="python", depends_on_services=["bar"])  # noqa: E501
    )

    order = project.topo_order()
    assert order.index("bar") < order.index("foo")
