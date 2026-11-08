"""Folder operations shared by interactive and direct commands."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class FolderPlan:
    kind: str
    start: str
    end: str
    destination: Path
    year: int

    def __post_init__(self):
        if self.kind not in {"export", "import"}:
            raise ValueError("Task must be export or import.")
        for label, value in (("Starting", self.start), ("Ending", self.end)):
            if not value or not value.isascii() or not value.isdecimal():
                raise ValueError(f"{label} number must contain digits 0-9 only.")
            if len(value) > 12:
                raise ValueError(f"{label} number must have at most 12 digits.")
        if int(self.end) < int(self.start):
            raise ValueError("Ending number must be greater than or equal to starting number.")
        if self.count > 100_000:
            raise ValueError("Create at most 100,000 folders per task.")
        if not 1000 <= self.year <= 9999:
            raise ValueError("Year must be a four-digit number.")
        if not self.destination.is_dir():
            raise ValueError(f"Destination must be an existing directory: {self.destination}")

    @property
    def count(self):
        return int(self.end) - int(self.start) + 1

    def name(self, number):
        padded = str(number).zfill(len(self.start))
        return f"RE-{padded}-{self.year}" if self.kind == "export" else f"IMP-{padded}"

    def paths(self):
        for number in range(int(self.start), int(self.end) + 1):
            yield self.destination / self.name(number)


@dataclass
class FolderResult:
    created: int = 0
    existing: int = 0
    failed: list[tuple[Path, str]] = field(default_factory=list)


def create_folders(plan: FolderPlan) -> FolderResult:
    result = FolderResult()
    for path in plan.paths():
        try:
            path.mkdir()
            result.created += 1
        except FileExistsError:
            if path.is_dir():
                result.existing += 1
            else:
                result.failed.append((path, "A file already uses this name."))
        except OSError as error:
            result.failed.append((path, str(error)))
    return result
