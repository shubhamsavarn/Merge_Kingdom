import unittest
from server.models import SaveStateV2, Wallet, Inventory, Entitlements
from server.storage import GameDatabase
from server.sync_engine import AuthoritativeSyncEngine
from server.legacy_adapter import LegacyClientAdapter
from server.store_engine import GemStoreEngine

class TestLegacyBackwardCompatibility(unittest.TestCase):
    """
    Validates compatibility with older app versions (v2.0-v2.4) and Android 7 players (Fact 5).
    Guarantees:
    1. Legacy JSON parsing never crashes.
    2. Legacy client uploads NEVER overwrite or delete Version 2.5 Gems or sticky Entitlements.
    3. Multi-device play across versions (Phone on 2.5, Tablet on Android 7/v2.2) converges safely.
    """

    def setUp(self):
        self.db = GameDatabase()
        self.sync_engine = AuthoritativeSyncEngine(self.db)
        self.legacy_adapter = LegacyClientAdapter(self.db, self.sync_engine)
        self.store_engine = GemStoreEngine(self.db)

    def test_legacy_upload_does_not_wipe_gems(self):
        player_id = "player_cross_device_android7"

        # 1. Player has upgraded on their new phone to Version 2.5
        v2_phone_save = SaveStateV2(
            player_id=player_id,
            level=100,
            wallet=Wallet(coins=500, gems=250),  # Has 250 hard currency gems!
            inventory=Inventory(hammer=3, shuffle=2),
            entitlements=Entitlements(no_ads=True),
            migrated=True
        )
        self.db.upsert_save(v2_phone_save)

        # 2. Player opens their old Android 7 tablet running version 2.2.
        # Fact 2 legacy shape: contains NO 'gems' field, and older JsonUtility doesn't know about gems.
        legacy_upload_payload = {
            "player_id": player_id,
            "saved_at": 1761750000,
            "level": 102,       # Beat 2 levels on the tablet
            "coins": 600,       # Earned 100 coins
            "inventory": { "hammer": 3, "shuffle": 2 },
            "no_ads": False     # Stale false from old tablet disk
        }

        # 3. Legacy upload processed by server adapter
        legacy_response = self.legacy_adapter.handle_legacy_upload(legacy_upload_payload)

        # Verify response to legacy client matches Fact 1 / Fact 2 schema exactly
        self.assertIn("player_id", legacy_response)
        self.assertIn("level", legacy_response)
        self.assertIn("coins", legacy_response)
        self.assertIn("inventory", legacy_response)
        self.assertIn("no_ads", legacy_response)

        # 4. Check canonical database state on server
        canonical = self.db.get_save(player_id)

        # ASSERTION 1: Level successfully advanced to 102
        self.assertEqual(canonical.level, 102)

        # ASSERTION 2: GEMS MUST NOT BE DELETED! (250 gems intact)
        self.assertEqual(canonical.wallet.gems, 250, "CRITICAL ERROR: Legacy client wiped v2.5 gems!")

        # ASSERTION 3: No Ads must remain True
        self.assertTrue(canonical.entitlements.no_ads, "CRITICAL ERROR: Legacy client wiped No Ads!")

        print("[SUCCESS] Cross-version sync verified: Android 7 legacy client did not wipe gems or no-ads.")

    def test_gem_store_purchases(self):
        player_id = "p_store_shopper"
        save = SaveStateV2(
            player_id=player_id,
            wallet=Wallet(coins=1000, gems=30),  # 30 gems
            inventory=Inventory(hammer=1, shuffle=1)
        )
        self.db.upsert_save(save)

        # 1. Buy 1 hammer (costs 10 gems)
        success, msg, data = self.store_engine.purchase_store_item(player_id, "hammer")
        self.assertTrue(success)
        self.assertEqual(data["wallet"]["gems"], 20)
        self.assertEqual(data["inventory"]["hammer"], 2)

        # 2. Attempt to buy super_pack (costs 50 gems, but player only has 20)
        success, msg, data = self.store_engine.purchase_store_item(player_id, "super_pack")
        self.assertFalse(success)
        self.assertEqual(msg, "INSUFFICIENT_GEMS")

        # 3. Simulate IAP fulfillment: player buys 100 gems
        iap_success, iap_data = self.store_engine.fulfill_gem_iap(player_id, "pack_gems_small", 100, "rec_999")
        self.assertTrue(iap_success)
        self.assertEqual(iap_data["wallet"]["gems"], 120)

        # 4. Retry super_pack (120 >= 50)
        success2, msg2, data2 = self.store_engine.purchase_store_item(player_id, "super_pack")
        self.assertTrue(success2)
        self.assertEqual(data2["wallet"]["gems"], 70)
        self.assertEqual(data2["inventory"]["hammer"], 5)  # 2 + 3 = 5
        self.assertEqual(data2["inventory"]["shuffle"], 6) # 1 + 5 = 6

        print("[SUCCESS] Gem store purchase and IAP receipt crediting verified.")

if __name__ == "__main__":
    unittest.main()

