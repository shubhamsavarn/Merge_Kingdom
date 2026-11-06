import unittest
import os
import shutil
import tempfile
from client.models import SaveDataV2, WalletData, InventoryData, EntitlementsData
from client.storage import LocalFileSaveStorage
from client.conflict_resolver import DomainMonotonicConflictResolver
from client.cloud_client import CloudSyncClient
from client.save_manager import SaveManager, SystemTimeProvider

class TestClientSDK(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.storage = LocalFileSaveStorage(self.test_dir)
        self.time_provider = SystemTimeProvider()
        self.resolver = DomainMonotonicConflictResolver(self.time_provider)
        self.cloud_client = CloudSyncClient()
        self.manager = SaveManager(self.storage, self.resolver, self.cloud_client, self.time_provider)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_save_manager_initialization_and_gameplay(self):
        save = self.manager.initialize("test_player_1")
        self.assertEqual(save.player_id, "test_player_1")
        self.assertEqual(save.level, 1)
        self.assertEqual(save.wallet.coins, 100)

        # Complete levels
        self.manager.complete_level(2)
        self.assertEqual(self.manager.current.level, 2)
        self.assertEqual(self.manager.current.wallet.coins, 150) # 100 + 50

        # Verify disk persistence
        reloaded = self.storage.load()
        self.assertEqual(reloaded.level, 2)
        self.assertEqual(reloaded.wallet.coins, 150)

    def test_local_storage_migration_from_v1_json(self):
        # Write legacy v1 JSON directly to disk
        v1_json = """{
            "player_id": "legacy_disk_user",
            "saved_at": 1761700000,
            "level": 99,
            "coins": 3000,
            "inventory": { "hammer": 4, "shuffle": 2 },
            "no_ads": true
        }"""
        with open(os.path.join(self.test_dir, "savegame.json"), "w") as f:
            f.write(v1_json)

        # Storage load detects v1 and auto-migrates
        migrated = self.storage.load()
        self.assertEqual(migrated.schema_version, 2)
        self.assertEqual(migrated.player_id, "legacy_disk_user")
        self.assertEqual(migrated.level, 99)
        self.assertEqual(migrated.wallet.coins, 3000)
        self.assertEqual(migrated.inventory.hammer, 4)
        self.assertTrue(migrated.entitlements.no_ads)

    def test_cloud_sync_offline_buffering(self):
        self.manager.initialize("offline_user")
        self.cloud_client.offline = True

        self.manager.complete_level(5)
        self.assertEqual(len(self.cloud_client._offline_queue), 1)

        # Reconnect
        self.cloud_client.offline = False
        flushed = self.cloud_client.flush_queue(on_ack=lambda ack: None)
        self.assertEqual(flushed, 1)
        self.assertEqual(len(self.cloud_client._offline_queue), 0)

if __name__ == "__main__":
    unittest.main()

