import threading
from typing import Dict, List, Optional
from server.models import SaveStateV2, PurchaseRecord

class GameDatabase:
    """
    In-memory thread-safe ACID datastore for Merge Kingdom.
    Maintains player canonical saves, purchase history, and gem transaction audit logs.
    """
    def __init__(self):
        self._lock = threading.RLock()
        self._saves: Dict[str, SaveStateV2] = {}
        self._purchases: Dict[str, List[PurchaseRecord]] = {}
        self._gem_ledger: List[Dict] = []

    def get_save(self, player_id: str) -> Optional[SaveStateV2]:
        with self._lock:
            save = self._saves.get(player_id)
            if save:
                # Return deep copy
                return SaveStateV2.from_dict(save.to_dict())
            return None

    def upsert_save(self, save: SaveStateV2) -> SaveStateV2:
        with self._lock:
            self._saves[save.player_id] = SaveStateV2.from_dict(save.to_dict())
            return self.get_save(save.player_id)

    def add_purchase(self, record: PurchaseRecord) -> None:
        with self._lock:
            if record.player_id not in self._purchases:
                self._purchases[record.player_id] = []
            self._purchases[record.player_id].append(record)

    def get_purchases(self, player_id: str) -> List[PurchaseRecord]:
        with self._lock:
            return list(self._purchases.get(player_id, []))

    def log_gem_transaction(self, player_id: str, delta: int, reason: str, balance_after: int) -> None:
        with self._lock:
            self._gem_ledger.append({
                "player_id": player_id,
                "delta": delta,
                "reason": reason,
                "balance_after": balance_after
            })

    def get_gem_ledger(self, player_id: str) -> List[Dict]:
        with self._lock:
            return [tx for tx in self._gem_ledger if tx["player_id"] == player_id]

    def reset(self):
        with self._lock:
            self._saves.clear()
            self._purchases.clear()
            self._gem_ledger.clear()

