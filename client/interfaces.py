from abc import ABC, abstractmethod
from typing import Optional, Callable
from client.models import SaveDataV2

class ISaveStorage(ABC):
    """
    Interface Segregation Principle (ISP):
    Abstract contract for local storage (disk, encrypted, memory).
    """
    @abstractmethod
    def load(self) -> Optional[SaveDataV2]:
        pass

    @abstractmethod
    def save(self, data: SaveDataV2) -> None:
        pass

    @abstractmethod
    def exists(self) -> bool:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass

class IConflictResolver(ABC):
    """
    Liskov Substitution Principle (LSP):
    Encapsulates conflict resolution strategy conforming to the invariant:
    'No player may lose progress, or anything that they paid for.'
    """
    @abstractmethod
    def resolve(self, local: SaveDataV2, incoming: SaveDataV2) -> SaveDataV2:
        pass

class ICloudSyncClient(ABC):
    """
    Interface Segregation Principle (ISP):
    Abstract contract for cloud network transmission and offline queueing.
    """
    @abstractmethod
    def upload(self, data: SaveDataV2, on_success: Callable[[SaveDataV2], None], on_failure: Callable[[str], None]) -> None:
        pass

    @abstractmethod
    def fetch_latest(self, player_id: str, on_success: Callable[[Optional[SaveDataV2]], None], on_failure: Callable[[str], None]) -> None:
        pass

class ITimeProvider(ABC):
    """
    Dependency Inversion Principle (DIP):
    Decouples logic from untrusted local system clocks.
    """
    @abstractmethod
    def get_current_unix_time(self) -> int:
        pass

