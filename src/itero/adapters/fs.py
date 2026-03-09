"""Adapter: real file system operations."""

from pathlib import Path

from itero.domain.ports import FileSystem


class RealFileSystem(FileSystem):
    """Concrete file system implementation."""

    def exists(self, path: Path) -> bool:
        return path.exists()

    def read_text(self, path: Path) -> str:
        return path.read_text()

    def write_text(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
