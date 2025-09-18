class DomainError(Exception):
    """Base class for domain errors."""


class UnknownService(DomainError):
    def __init__(self, name: str) -> None:
        super().__init__(f"Unknown service: {name}")
        self.name = name


class CircularDependency(DomainError):
    def __init__(self, service: str) -> None:
        super().__init__(f"Circular dependency detected involving '{service}'")
        self.service = service
