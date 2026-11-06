import time
from typing import Dict, Any, Tuple
from server.models import SaveStateV2, Inventory, Wallet, Entitlements
from server.storage import GameDatabase
from server.sync_engine import AuthoritativeSyncEngine

class LegacyClientAdapter:
    """
    Handles backward-compatibility for legacy app versions (v2.0, v2.1, v2.2, v2.3, v2.4).
    Specifically protects the ~5% of total active daily players permanently on Android 7 who cannot update.
    
    Responsibilities:
    1. Translate incoming v1 JSON into canonical SaveStateV2.
    2. Prevent legacy clients from wiping Version 2.5 fields (Gems, SchemaVersion, Revisions).
    3. Project canonical SaveStateV2 into v1 JSON format consumable by legacy JsonUtility.
    """
    def __init__(self, db: GameDatabase, sync_engine: AuthoritativeSyncEngine):
        self.db = db
        self.sync_engine = sync_engine

    def parse_legacy_json(self, legacy_dict: Dict[str, Any]) -> SaveStateV2:
        """
        Converts v1 JSON payload into SaveStateV2.
        """
        player_id = legacy_dict["player_id"]
        
        # Check if existing server save exists to preserve non-v1 fields
        existing_server_save = self.db.get_save(player_id)
        existing_gems = existing_server_save.wallet.gems if existing_server_save else 0
        existing_migrated = existing_server_save.migrated if existing_server_save else False

        inv_raw = legacy_dict.get("inventory", {}) or {}
        inventory = Inventory(
            hammer=int(inv_raw.get("hammer", 0)),
            shuffle=int(inv_raw.get("shuffle", 0))
        )

        wallet = Wallet(
            coins=int(legacy_dict.get("coins", 0)),
            gems=existing_gems  # PRESERVE GEMS: legacy client cannot destroy hard currency
        )

        entitlements = Entitlements(
            no_ads=bool(legacy_dict.get("no_ads", False))
        )

        return SaveStateV2(
            player_id=player_id,
            schema_version=1,  # Flagged as legacy source
            revision=existing_server_save.revision if existing_server_save else 1,
            server_saved_at=int(time.time()),
            client_saved_at=int(legacy_dict.get("saved_at", 0)),
            device_id=legacy_dict.get("device_id", "legacy_device"),
            level=int(legacy_dict.get("level", 1)),
            wallet=wallet,
            inventory=inventory,
            entitlements=entitlements,
            migrated=existing_migrated
        )

    def handle_legacy_upload(self, legacy_json_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes an upload from a v2.0 - v2.4 client.
        Merges safely and returns legacy-compatible JSON string/dict.
        """
        client_save = self.parse_legacy_json(legacy_json_dict)
        merged_save, sync_meta = self.sync_engine.sync(client_save)
        return self.to_legacy_json(merged_save)

    def to_legacy_json(self, canonical_save: SaveStateV2) -> Dict[str, Any]:
        """
        Formats SaveStateV2 into exact Fact 1 / Fact 2 legacy JSON shape:
        {
          "player_id": "...",
          "saved_at": 1761700000,
          "level": 142,
          "coins": 5400,
          "inventory": { "hammer": 3, "shuffle": 1 },
          "no_ads": true
        }
        """
        return {
            "player_id": canonical_save.player_id,
            "saved_at": canonical_save.server_saved_at,
            "level": canonical_save.level,
            "coins": canonical_save.wallet.coins,
            "inventory": canonical_save.inventory.to_dict(),
            "no_ads": canonical_save.entitlements.no_ads
        }

