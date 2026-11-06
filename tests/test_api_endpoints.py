import unittest
from server.api import health, sync_v2_modern, sync_v1_legacy, buy_item, db

class TestApiEndpoints(unittest.TestCase):
    def setUp(self):
        db.reset()

    def test_health_check(self):
        res = health()
        self.assertEqual(res["status"], "HEALTHY")
        self.assertEqual(res["version"], "2.5.0")

    def test_v2_sync_and_store_workflow(self):
        player_id = "api_test_player"

        # 1. First sync v2
        payload = {
            "player_id": player_id,
            "device_id": "iphone_15",
            "level": 12,
            "wallet": {"coins": 500, "gems": 100},
            "inventory": {"hammer": 1, "shuffle": 2},
            "entitlements": {"no_ads": True}
        }
        res = sync_v2_modern(payload)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["save"]["level"], 12)
        self.assertEqual(res["save"]["wallet"]["gems"], 100)

        # 2. Buy store item with gems
        buy_res = buy_item({"player_id": player_id, "item": "hammer"})
        self.assertEqual(buy_res["status"], "SUCCESS")
        buy_data = buy_res["data"]
        self.assertEqual(buy_data["wallet"]["gems"], 90)     # 100 - 10 = 90
        self.assertEqual(buy_data["inventory"]["hammer"], 2) # 1 + 1 = 2

    def test_legacy_v1_sync_endpoint(self):
        # Legacy payload matching Fact 1 shape exactly
        legacy_payload = {
            "player_id": "p_legacy_user",
            "saved_at": 1761700000,
            "level": 40,
            "coins": 1500,
            "inventory": {"hammer": 2, "shuffle": 1},
            "no_ads": True
        }
        resp_data = sync_v1_legacy(legacy_payload)
        self.assertEqual(resp_data["player_id"], "p_legacy_user")
        self.assertEqual(resp_data["level"], 40)
        self.assertEqual(resp_data["coins"], 1500)
        self.assertTrue(resp_data["no_ads"])

if __name__ == "__main__":
    unittest.main()
