from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass(frozen=True)
class Runtime:
    port: Optional[int] = None
    entry_point: Optional[str] = None
    version_info: Dict[str, str] = field(default_factory=dict)


@dataclass
class Service:
    name: str
    path: Path
    language: str
    framework: Optional[str] = None
    runtime: Runtime = field(default_factory=Runtime)
    depends_on_services: List[str] = field(default_factory=list)
    depends_on_schemas: List[str] = field(default_factory=list)
    schemas_mount_dir: Optional[str] = None
    environment: Dict[str, str] = field(default_factory=dict)

    def id(self) -> str:
        return self.name
