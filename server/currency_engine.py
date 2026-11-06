from typing import Dict, Any, Tuple
from server.models import SaveStateV2, Wallet
from server.storage import GameDatabase

class CurrencySplitEngine:
    """
    Implements Task 4: FIFO Payer-Protection Ledger Split.
    
    Invariant: "No player may lose progress, or anything that they paid for."
    
    Formula:
        C_purchased = Sum(record.coins for record in PurchaseRecords)
        C_current   = Current coin balance in player save
        PaidCoins   = min(C_current, C_purchased)
        EarnedCoins = C_current - PaidCoins
        New_Gems    = Round(PaidCoins * GemConversionRate)
        New_Coins   = EarnedCoins + GameplayBonus (if EarnedCoins == 0 and PaidCoins > 0)
    """

    DEFAULT_GEM_RATE: float = 0.1  # 10 Coins = 1 Gem (e.g. 100 coin booster costs 10 gems)
    ZERO_COIN_PAYER_GOODWILL_GEMS: int = 50
    COIN_STARTER_GRANT: int = 200

    def __init__(self, db: GameDatabase, gem_rate: float = DEFAULT_GEM_RATE):
        self.db = db
        self.gem_rate = gem_rate

    def calculate_split(self, player_id: str, current_coins: int) -> Dict[str, Any]:
        purchases = self.db.get_purchases(player_id)
        total_purchased_coins = sum(p.coins for p in purchases)

        # 1. Payer-favorable attribution: Assume spent coins were earned coins first
        paid_coins = min(current_coins, total_purchased_coins)
        earned_coins = max(0, current_coins - paid_coins)

        # 2. Convert paid coins to gems at store purchasing power parity
        gems = int(round(paid_coins * self.gem_rate))
        coins = earned_coins

        goodwill_applied = False
        starter_bonus_applied = False

        # Edge case A: Player bought coins historically, but currently has 0 coins.
        # They consumed their coins, but grant a goodwill reward to build trust.
        if total_purchased_coins > 0 and current_coins == 0:
            gems += self.ZERO_COIN_PAYER_GOODWILL_GEMS
            goodwill_applied = True

        # Edge case B: All player coins were converted to gems, leaving 0 coins for puzzle continues.
        # Grant starter gameplay coins so they are not blocked in levels.
        if coins == 0 and paid_coins > 0:
            coins += self.COIN_STARTER_GRANT
            starter_bonus_applied = True

        return {
            "player_id": player_id,
            "original_coins": current_coins,
            "total_purchased_coins": total_purchased_coins,
            "paid_coins_converted": paid_coins,
            "earned_coins_retained": earned_coins,
            "new_gems": gems,
            "new_coins": coins,
            "goodwill_applied": goodwill_applied,
            "starter_bonus_applied": starter_bonus_applied
        }

    def execute_migration(self, save: SaveStateV2) -> Tuple[SaveStateV2, Dict[str, Any]]:
        """
        Executes idempotent migration on a player account.
        """
        if save.migrated:
            # Already migrated, idempotent no-op
            return save, {"already_migrated": True}

        split = self.calculate_split(save.player_id, save.wallet.coins)

        save.wallet.coins = split["new_coins"]
        save.wallet.gems = split["new_gems"]
        save.coins = save.wallet.coins  # Mirror key
        save.migrated = True
        save.revision += 1

        self.db.log_gem_transaction(
            player_id=save.player_id,
            delta=split["new_gems"],
            reason="MIGRATION_V2_5_SPLIT",
            balance_after=save.wallet.gems
        )

        updated_save = self.db.upsert_save(save)
        return updated_save, split

