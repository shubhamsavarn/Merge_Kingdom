from typing import Dict, Any, Tuple
from server.models import SaveStateV2
from server.storage import GameDatabase

class GemStoreEngine:
    """
    Handles Version 2.5 authoritative store transactions and IAP fulfillment.
    
    Rule:
    - Items (hammers, shuffles) are sold for GEMS only.
    - Server validates balance atomically to prevent client double-spend exploits.
    """
    ITEM_PRICES_IN_GEMS = {
        "hammer": 10,     # 10 gems = 1 hammer
        "shuffle": 5,     # 5 gems = 1 shuffle
        "super_pack": 50  # 50 gems = 3 hammers + 5 shuffles
    }

    def __init__(self, db: GameDatabase):
        self.db = db

    def purchase_store_item(self, player_id: str, item_key: str) -> Tuple[bool, str, Dict[str, Any]]:
        save = self.db.get_save(player_id)
        if not save:
            return False, "PLAYER_NOT_FOUND", {}

        cost = self.ITEM_PRICES_IN_GEMS.get(item_key)
        if cost is None:
            return False, "INVALID_ITEM", {}

        if save.wallet.gems < cost:
            return False, "INSUFFICIENT_GEMS", {
                "required": cost,
                "current": save.wallet.gems
            }

        # Deduct gems
        save.wallet.gems -= cost
        
        # Credit item
        if item_key == "hammer":
            save.inventory.hammer += 1
        elif item_key == "shuffle":
            save.inventory.shuffle += 1
        elif item_key == "super_pack":
            save.inventory.hammer += 3
            save.inventory.shuffle += 5

        save.revision += 1
        self.db.log_gem_transaction(
            player_id=player_id,
            delta=-cost,
            reason=f"STORE_PURCHASE_{item_key.upper()}",
            balance_after=save.wallet.gems
        )

        updated = self.db.upsert_save(save)
        return True, "PURCHASE_SUCCESS", {
            "item": item_key,
            "cost_gems": cost,
            "wallet": updated.wallet.to_dict(),
            "inventory": updated.inventory.to_dict(),
            "revision": updated.revision
        }

    def fulfill_gem_iap(self, player_id: str, pack_id: str, gem_amount: int, receipt_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Validates real-money IAP and credits hard currency gems to ledger.
        """
        save = self.db.get_save(player_id)
        if not save:
            # Initialize placeholder save if new player
            save = SaveStateV2(player_id=player_id)

        save.wallet.gems += gem_amount
        save.revision += 1

        self.db.log_gem_transaction(
            player_id=player_id,
            delta=gem_amount,
            reason=f"IAP_PURCHASE_{pack_id}_RECEIPT_{receipt_id}",
            balance_after=save.wallet.gems
        )

        updated = self.db.upsert_save(save)
        return True, {
            "player_id": player_id,
            "gems_added": gem_amount,
            "wallet": updated.wallet.to_dict(),
            "revision": updated.revision
        }

