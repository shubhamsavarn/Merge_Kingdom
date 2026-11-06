from client.interfaces import IConflictResolver, ITimeProvider
from client.models import SaveDataV2, WalletData, InventoryData, EntitlementsData

class DomainMonotonicConflictResolver(IConflictResolver):
    """
    Single Responsibility Principle (SRP):
    Pure conflict arbitration applying CRDT domain monotonicity.
    
    Invariants:
    1. Level progress is strictly non-decreasing: max(local, remote).
    2. Durable entitlements are sticky-true: once acquired, never reverted.
    3. Consumable inventory items are protected: max(local, remote).
    4. Client system clock is never trusted for conflict arbitration.
    """
    def __init__(self, time_provider: ITimeProvider):
        self.time_provider = time_provider

    def resolve(self, local: SaveDataV2, incoming: SaveDataV2) -> SaveDataV2:
        if incoming is None:
            return local
        if local is None:
            return incoming

        resolved_level = max(local.level, incoming.level)
        resolved_no_ads = local.entitlements.no_ads or incoming.entitlements.no_ads or local.no_ads or incoming.no_ads

        resolved_inventory = InventoryData(
            hammer=max(local.inventory.hammer, incoming.inventory.hammer),
            shuffle=max(local.inventory.shuffle, incoming.inventory.shuffle)
        )

        resolved_wallet = WalletData(
            coins=max(local.wallet.coins, incoming.wallet.coins),
            gems=max(local.wallet.gems, incoming.wallet.gems)
        )

        resolved_revision = max(local.revision, incoming.revision)
        now = self.time_provider.get_current_unix_time()

        return SaveDataV2(
            player_id=local.player_id or incoming.player_id,
            schema_version=2,
            revision=resolved_revision,
            client_saved_at=now,
            device_id=local.device_id or incoming.device_id,
            level=resolved_level,
            wallet=resolved_wallet,
            inventory=resolved_inventory,
            entitlements=EntitlementsData(no_ads=resolved_no_ads)
        )

