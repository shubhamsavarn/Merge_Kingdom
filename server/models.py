from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
import time

@dataclass
class Inventory:
    hammer: int = 0
    shuffle: int = 0

    def to_dict(self) -> Dict[str, int]:
        return {"hammer": self.hammer, "shuffle": self.shuffle}

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "Inventory":
        if not data:
            return cls(0, 0)
        return cls(
            hammer=int(data.get("hammer", 0)),
            shuffle=int(data.get("shuffle", 0))
        )

@dataclass
class Wallet:
    coins: int = 0  # Soft currency (earned only)
    gems: int = 0   # Hard currency (bought with real money only)

    def to_dict(self) -> Dict[str, int]:
        return {"coins": self.coins, "gems": self.gems}

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "Wallet":
        if not data:
            return cls(0, 0)
        return cls(
            coins=int(data.get("coins", 0)),
            gems=int(data.get("gems", 0))
        )

@dataclass
class Entitlements:
    no_ads: bool = False

    def to_dict(self) -> Dict[str, bool]:
        return {"no_ads": self.no_ads}

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "Entitlements":
        if not data:
            return cls(False)
        return cls(no_ads=bool(data.get("no_ads", False)))

@dataclass
class PurchaseRecord:
    player_id: str
    pack_id: str
    coins: int
    purchased_at: int
    price_cents: int = 0

@dataclass
class SaveStateV2:
    player_id: str
    schema_version: int = 2
    revision: int = 1
    server_saved_at: int = field(default_factory=lambda: int(time.time()))
    client_saved_at: int = 0
    device_id: str = "unknown"
    level: int = 1
    wallet: Wallet = field(default_factory=Wallet)
    inventory: Inventory = field(default_factory=Inventory)
    entitlements: Entitlements = field(default_factory=Entitlements)
    migrated: bool = False

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
            "server_saved_at": self.server_saved_at,
            "client_saved_at": self.client_saved_at,
            "level": self.level,
            "wallet": self.wallet.to_dict(),
            "inventory": self.inventory.to_dict(),
            "entitlements": self.entitlements.to_dict(),
            "migrated": self.migrated,
            # Legacy mirror keys for backward compatibility
            "coins": self.wallet.coins,
            "no_ads": self.entitlements.no_ads
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "SaveStateV2":
        wallet_data = d.get("wallet")
        coins_fallback = d.get("coins", 0)
        
        wallet = Wallet.from_dict(wallet_data) if wallet_data else Wallet(coins=int(coins_fallback), gems=0)
        if wallet.coins == 0 and coins_fallback > 0:
            wallet.coins = int(coins_fallback)

        entitlements_data = d.get("entitlements")
        no_ads_fallback = d.get("no_ads", False)
        entitlements = Entitlements.from_dict(entitlements_data) if entitlements_data else Entitlements(no_ads=bool(no_ads_fallback))
        if not entitlements.no_ads and no_ads_fallback:
            entitlements.no_ads = True

        return cls(
            player_id=d["player_id"],
            schema_version=int(d.get("schema_version", 2)),
            revision=int(d.get("revision", 1)),
            server_saved_at=int(d.get("server_saved_at", time.time())),
            client_saved_at=int(d.get("client_saved_at", 0)),
            device_id=d.get("device_id", "unknown"),
            level=int(d.get("level", 1)),
            wallet=wallet,
            inventory=Inventory.from_dict(d.get("inventory")),
            entitlements=entitlements,
            migrated=bool(d.get("migrated", False))
        )
