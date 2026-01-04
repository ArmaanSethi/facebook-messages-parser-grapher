from abc import ABC, abstractmethod
from typing import Generator, Dict, Any
from pathlib import Path

class BaseParser(ABC):
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)

    @abstractmethod
    def iter_conversations(self) -> Generator[Dict[str, Any], None, None]:
        """
        Yields conversation objects.
        Each object must have:
        - title: str
        - messages: List[Dict] (with 'sender_name', 'timestamp_ms', 'content', 'type')
        """
        pass
