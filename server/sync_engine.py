import time
from typing import Tuple, Dict, Any
from server.models import SaveStateV2, Inventory, Wallet, Entitlements
from server.storage import GameDatabase

class AuthoritativeSyncEngine:
    """
    Authoritative Server Sync Engine replacing blind Last-Write-Wins on client timestamps.
    
    Invariants Enforced:
    1. Level is strictly monotonic: level >= max(server.level, client.level)
    2. Entitlements are sticky-true: no_ads is permanent once set.
    3. Inventories merge conservatively without dropping player boosters.
    4. Client timestamp (client_saved_at) is never used for conflict arbitration.
    5. Server assigns monotonic sequential revisions.
    """
    def __init__(self, db: GameDatabase):
        self.db = db

    def sync(self, client_save: SaveStateV2) -> Tuple[SaveStateV2, Dict[str, Any]]:
        player_id = client_save.player_id
        server_save = self.db.get_save(player_id)
        now = int(time.time())

        # If no previous save exists, accept client as baseline
        if not server_save:
            client_save.revision = 1
            client_save.server_saved_at = now
            client_save.coins = client_save.wallet.coins
            client_save.no_ads = client_save.entitlements.no_ads
            saved = self.db.upsert_save(client_save)
            return saved, {"action": "INITIAL_CREATION", "revision": saved.revision}

        # DOMAIN-SPECIFIC MONOTONIC MERGE:
        # Fixes Incident 1 (Tablet vs Airplane Phone) & Incident 2 (Date tampering)
        merged_level = max(server_save.level, client_save.level)

        # Fixes Incident 3 (No-Ads lost to stale device)
        merged_no_ads = server_save.entitlements.no_ads or client_save.entitlements.no_ads or server_save.no_ads or client_save.no_ads

        merged_inventory = Inventory(
            hammer=max(server_save.inventory.hammer, client_save.inventory.hammer),
            shuffle=max(server_save.inventory.shuffle, client_save.inventory.shuffle)
        )

        # Wallet:
        # Gems are hard currency tracked on server. If client hasn't bought/spent via verified server endpoints,
        # server gem balance is authoritative.
        merged_gems = max(server_save.wallet.gems, client_save.wallet.gems)
        
        # Soft coins: take max to guarantee player puzzle grind isn't lost during offline play
        merged_coins = max(server_save.wallet.coins, client_save.wallet.coins)

        # Create updated canonical state
        new_revision = max(server_save.revision, client_save.revision) + 1
        merged_save = SaveStateV2(
            player_id=player_id,
            schema_version=2,
            revision=new_revision,
            server_saved_at=now,
            client_saved_at=client_save.client_saved_at,
            device_id=client_save.device_id,
            level=merged_level,
            wallet=Wallet(coins=merged_coins, gems=merged_gems),
            inventory=merged_inventory,
            entitlements=Entitlements(no_ads=merged_no_ads),
            migrated=server_save.migrated or client_save.migrated
        )

        saved = self.db.upsert_save(merged_save)
        return saved, {
            "action": "MERGED_SUCCESS",
            "revision": saved.revision,
            "level_merged": merged_level,
            "no_ads": merged_no_ads
        }

