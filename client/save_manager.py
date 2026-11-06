import time
from typing import Optional, Callable
from client.interfaces import ISaveStorage, IConflictResolver, ICloudSyncClient, ITimeProvider
from client.models import SaveDataV2, WalletData, InventoryData, EntitlementsData

class SystemTimeProvider(ITimeProvider):
    def get_current_unix_time(self) -> int:
        return int(time.time())

class SaveManager:
    """
    Dependency Inversion Principle (DIP):
    High-level lifecycle coordinator for game saves. Depends only on abstractions.
    Replaces legacy static SaveSystem.
    """
    def __init__(
        self,
        storage: ISaveStorage,
        conflict_resolver: IConflictResolver,
        cloud_client: ICloudSyncClient,
        time_provider: Optional[ITimeProvider] = None
    ):
        self.storage = storage
        self.conflict_resolver = conflict_resolver
        self.cloud_client = cloud_client
        self.time_provider = time_provider or SystemTimeProvider()
        self.current: Optional[SaveDataV2] = None

    def initialize(self, default_player_id: str) -> SaveDataV2:
        self.current = self.storage.load()

        if self.current is None:
            self.current = SaveDataV2(
                player_id=default_player_id,
                schema_version=2,
                revision=0,
                client_saved_at=self.time_provider.get_current_unix_time(),
                level=1,
                wallet=WalletData(coins=100, gems=0),
                inventory=InventoryData(hammer=1, shuffle=1),
                entitlements=EntitlementsData(no_ads=False)
            )
            self.storage.save(self.current)

        return self.current

    def commit_save(self) -> None:
        if self.current is None:
            return

        self.current.client_saved_at = self.time_provider.get_current_unix_time()
        
        # 1. Local atomic write first (crash resilience)
        self.storage.save(self.current)

        # 2. Cloud dispatch
        def on_success(server_ack: SaveDataV2):
            if server_ack:
                self.current.revision = max(self.current.revision, server_ack.revision)
                self.storage.save(self.current)

        def on_failure(err: str):
            # Logged, queue handled internally
            pass

        self.cloud_client.upload(self.current, on_success, on_failure)

    def complete_level(self, completed_level: int) -> None:
        if self.current is None:
            return

        if completed_level > self.current.level:
            self.current.level = completed_level

        # Gameplay reward: 50 coins for clearing puzzle level
        self.current.wallet.coins += 50
        self.commit_save()

    def grant_entitlement(self, key: str) -> None:
        if self.current is None:
            return

        if key == "no_ads":
            self.current.entitlements.no_ads = True
            self.commit_save()

    def apply_cloud_save(self, incoming_save: SaveDataV2) -> SaveDataV2:
        """
        Invoked when an update arrives from the server.
        Uses DomainMonotonicConflictResolver to guarantee no loss of progress or purchases.
        """
        if incoming_save is None:
            return self.current

        self.current = self.conflict_resolver.resolve(self.current, incoming_save)
        self.storage.save(self.current)
        return self.current

