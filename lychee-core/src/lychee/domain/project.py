from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from .errors import CircularDependency, UnknownService
from .service import Service


@dataclass
class Project:
    root: Path
    services: Dict[str, Service] = field(default_factory=dict)
    languages: List[str] = field(default_factory=list)

    def add_service(self, service: Service) -> None:
        self.services[service.name] = service

    def get_service(self, name: str) -> Service:
        try:
            return self.services[name]
        except KeyError:
            raise UnknownService(name)

    def list_services(self) -> List[str]:
        return list(self.services.keys())

    def dependencies_of(self, service_name: str) -> List[str]:
        svc = self.get_service(service_name)
        return list(svc.depends_on_services)

    def dependents_of(self, service_name: str) -> List[str]:
        dependents: List[str] = []
        for name, svc in self.services.items():
            if service_name in svc.depends_on_services:
                dependents.append(name)
        return dependents

    def topo_order(self) -> List[str]:
        visited: set[str] = set()
        temp: set[str] = set()
        result: List[str] = []

        def visit(n: str) -> None:
            if n in temp:
                raise CircularDependency(n)
            if n in visited:
                return
            temp.add(n)
            for dep in self.dependencies_of(n):
                if dep not in self.services:
                    raise UnknownService(dep)
                visit(dep)
            temp.remove(n)
            visited.add(n)
            result.append(n)

        for name in self.services:
            if name not in visited:
                visit(name)
        return result
