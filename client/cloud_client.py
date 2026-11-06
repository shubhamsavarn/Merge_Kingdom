from typing import Callable, Optional, List
from client.interfaces import ICloudSyncClient
from client.models import SaveDataV2

class CloudSyncClient(ICloudSyncClient):
    """
    Handles cloud synchronization and persistent offline queuing.
    Supports injecting an active backend callback or HTTP dispatcher.
    """
    def __init__(self, backend_sync_handler: Optional[Callable[[SaveDataV2], SaveDataV2]] = None):
        self.backend_sync_handler = backend_sync_handler
        self.offline: bool = False
        self._offline_queue: List[SaveDataV2] = []

    def upload(self, data: SaveDataV2, on_success: Callable[[SaveDataV2], None], on_failure: Callable[[str], None]) -> None:
        if self.offline:
            self._offline_queue.append(SaveDataV2.from_dict(data.to_dict()))
            on_failure("OFFLINE_BUFFERED")
            return

        try:
            if self.backend_sync_handler:
                ack_save = self.backend_sync_handler(data)
                on_success(ack_save)
            else:
                # Default optimistic acknowledgement
                data.revision += 1
                on_success(data)
        except Exception as e:
            self._offline_queue.append(SaveDataV2.from_dict(data.to_dict()))
            on_failure(str(e))

    def fetch_latest(self, player_id: str, on_success: Callable[[Optional[SaveDataV2]], None], on_failure: Callable[[str], None]) -> None:
        if self.offline:
            on_failure("OFFLINE_CANNOT_FETCH")
            return

        # Fetch implementation
        on_success(None)

    def flush_queue(self, on_ack: Callable[[SaveDataV2], None]) -> int:
        """
        Simulates reconnecting to internet and flushing queued uploads.
        """
        count = 0
        while self._offline_queue:
            item = self._offline_queue.pop(0)
            if self.backend_sync_handler:
                ack = self.backend_sync_handler(item)
                on_ack(ack)
            count += 1
        return count

