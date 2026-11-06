from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class InventoryData:
    hammer: int = 0
    shuffle: int = 0

    def to_dict(self) -> Dict[str, int]:
        return {"hammer": self.hammer, "shuffle": self.shuffle}

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "InventoryData":
        if not data:
            return cls(0, 0)
        return cls(
            hammer=int(data.get("hammer", 0)),
            shuffle=int(data.get("shuffle", 0))
        )

@dataclass
class WalletData:
    coins: int = 0  # Soft currency: earned by gameplay only
    gems: int = 0   # Hard currency: bought with real money only

    def to_dict(self) -> Dict[str, int]:
        return {"coins": self.coins, "gems": self.gems}

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "WalletData":
        if not data:
            return cls(0, 0)
        return cls(
            coins=int(data.get("coins", 0)),
            gems=int(data.get("gems", 0))
        )

@dataclass
class EntitlementsData:
    no_ads: bool = False

    def to_dict(self) -> Dict[str, bool]:
        return {"no_ads": self.no_ads}

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "EntitlementsData":
        if not data:
            return cls(False)
        return cls(no_ads=bool(data.get("no_ads", False)))

@dataclass
class SaveDataV2:
    """
    Version 2.5 Client Save Data Model.
    Open/Closed Principle (OCP): Versioned schema supporting backward-compatibility mirrors.
    """
    player_id: str
    schema_version: int = 2
    revision: int = 0
    client_saved_at: int = 0
    device_id: str = "device_client"
    level: int = 1
    wallet: WalletData = field(default_factory=WalletData)
    inventory: InventoryData = field(default_factory=InventoryData)
    entitlements: EntitlementsData = field(default_factory=EntitlementsData)

    @property
    def coins(self) -> int:
        return self.wallet.coins

    @coins.setter
    def coins(self, val: int):
        self.wallet.coins = int(val)

    @property
    def no_ads(self) -> bool:
        return self.entitlements.no_ads

    @no_ads.setter
    def no_ads(self, val: bool):
        self.entitlements.no_ads = bool(val)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "player_id": self.player_id,
            "device_id": self.device_id,
            "revision": self.revision,
            "client_saved_at": self.client_saved_at,
            "level": self.level,
            "wallet": self.wallet.to_dict(),
            "inventory": self.inventory.to_dict(),
            "entitlements": self.entitlements.to_dict(),
            # Legacy mirror fields for backward compatibility
            "coins": self.wallet.coins,
            "no_ads": self.entitlements.no_ads
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "SaveDataV2":
        wallet_dict = d.get("wallet")
        coins_fallback = d.get("coins", 0)
        wallet = WalletData.from_dict(wallet_dict) if wallet_dict else WalletData(coins=int(coins_fallback), gems=0)
        if wallet.coins == 0 and coins_fallback > 0:
            wallet.coins = int(coins_fallback)

        entitlements_dict = d.get("entitlements")
        no_ads_fallback = d.get("no_ads", False)
        entitlements = EntitlementsData.from_dict(entitlements_dict) if entitlements_dict else EntitlementsData(no_ads=bool(no_ads_fallback))
        if not entitlements.no_ads and no_ads_fallback:
            entitlements.no_ads = True

        return cls(
            player_id=d["player_id"],
            schema_version=int(d.get("schema_version", 2)),
            revision=int(d.get("revision", 0)),
            client_saved_at=int(d.get("client_saved_at", 0)),
            device_id=d.get("device_id", "device_client"),
            level=int(d.get("level", 1)),
            wallet=wallet,
            inventory=InventoryData.from_dict(d.get("inventory")),
            entitlements=entitlements
        )

