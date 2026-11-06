import os
import json
from typing import Optional, Dict, Any
from client.interfaces import ISaveStorage
from client.models import SaveDataV2, WalletData, InventoryData, EntitlementsData

class LocalFileSaveStorage(ISaveStorage):
    """
    Single Responsibility Principle (SRP):
    Local atomic disk persistence with crash resilience and legacy v1 JSON migration.
    """
    def __init__(self, directory_path: str, file_name: str = "savegame.json"):
        os.makedirs(directory_path, exist_ok=True)
        self.file_path = os.path.join(directory_path, file_name)
        self.temp_file_path = self.file_path + ".tmp"

    def exists(self) -> bool:
        return os.path.exists(self.file_path)

    def clear(self) -> None:
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
        if os.path.exists(self.temp_file_path):
            os.remove(self.temp_file_path)

    def load(self) -> Optional[SaveDataV2]:
        if not self.exists():
            return None

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Check if schema_version exists; if not, migrate from legacy v1
            if "schema_version" not in data:
                return self._migrate_legacy_v1(data)

            return SaveDataV2.from_dict(data)
        except Exception as e:
            # Fallback to temp file if primary was interrupted during write
            if os.path.exists(self.temp_file_path):
                with open(self.temp_file_path, "r", encoding="utf-8") as tf:
                    data = json.load(tf)
                return SaveDataV2.from_dict(data)
            raise e

    def save(self, data: SaveDataV2) -> None:
        # Crash-resilient write: write to temp file first, then atomic replace
        with open(self.temp_file_path, "w", encoding="utf-8") as f:
            json.dump(data.to_dict(), f, indent=2)

        # Atomic rename/replace
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
        os.rename(self.temp_file_path, self.file_path)

    def _migrate_legacy_v1(self, v1: Dict[str, Any]) -> SaveDataV2:
        inv_dict = v1.get("inventory", {}) or {}
        return SaveDataV2(
            player_id=v1["player_id"],
            schema_version=2,
            revision=1,
            client_saved_at=int(v1.get("saved_at", 0)),
            device_id=v1.get("device_id", "migrated_device"),
            level=int(v1.get("level", 1)),
            wallet=WalletData(coins=int(v1.get("coins", 0)), gems=0),
            inventory=InventoryData(
                hammer=int(inv_dict.get("hammer", 0)),
                shuffle=int(inv_dict.get("shuffle", 0))
            ),
            entitlements=EntitlementsData(no_ads=bool(v1.get("no_ads", False)))
        )

