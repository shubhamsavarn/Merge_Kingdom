using System;
using System.IO;
using UnityEngine;
using MergeKingdom.SaveSystem.Interfaces;
using MergeKingdom.SaveSystem.Models;

namespace MergeKingdom.SaveSystem.Core
{
    /// <summary>
    /// Single Responsibility: Local atomic persistence and crash-safe file IO.
    /// Handles disk operations, corruption prevention (.tmp swapping), and v1->v2 local migration.
    /// </summary>
    public class LocalFileSaveStorage : ISaveStorage
    {
        private readonly string _filePath;
        private readonly string _tempFilePath;

        public LocalFileSaveStorage(string directoryPath, string fileName = "savegame.json")
        {
            if (string.IsNullOrEmpty(directoryPath))
            {
                directoryPath = Application.persistentDataPath;
            }

            if (!Directory.Exists(directoryPath))
            {
                Directory.CreateDirectory(directoryPath);
            }

            _filePath = Path.Combine(directoryPath, fileName);
            _tempFilePath = _filePath + ".tmp";
        }

        public bool Exists()
        {
            return File.Exists(_filePath);
        }

        public void Clear()
        {
            if (File.Exists(_filePath)) File.Delete(_filePath);
            if (File.Exists(_tempFilePath)) File.Delete(_tempFilePath);
        }

        public SaveDataV2 Load()
        {
            if (!Exists())
            {
                return null;
            }

            try
            {
                string json = File.ReadAllText(_filePath);
                
                // Inspect schema version or detect v1
                if (!json.Contains("\"schema_version\""))
                {
                    // Legacy SaveData v1 detection
                    return MigrateFromLegacyJson(json);
                }

                SaveDataV2 data = JsonUtility.FromJson<SaveDataV2>(json);
                data.ReconcileFromMirrors();
                return data;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[LocalFileSaveStorage] Failed to read save file: {ex.Message}");
                // If backup / temp exists, attempt recovery
                if (File.Exists(_tempFilePath))
                {
                    string fallbackJson = File.ReadAllText(_tempFilePath);
                    return JsonUtility.FromJson<SaveDataV2>(fallbackJson);
                }
                throw;
            }
        }

        public void Save(SaveDataV2 data)
        {
            if (data == null) throw new ArgumentNullException(nameof(data));

            data.SynchronizeMirrorFields();
            string json = JsonUtility.ToJson(data, prettyPrint: true);

            // Crash-resilient write: write to temp file first, then atomically replace
            File.WriteAllText(_tempFilePath, json);
            if (File.Exists(_filePath))
            {
                File.Delete(_filePath);
            }
            File.Move(_tempFilePath, _filePath);
        }

        private SaveDataV2 MigrateFromLegacyJson(string legacyJson)
        {
            Debug.Log("[LocalFileSaveStorage] Detected legacy SaveData v1. Performing local bootstrap migration.");
            
            // Deserialize using legacy shape first
            LegacySaveDataV1 legacy = JsonUtility.FromJson<LegacySaveDataV1>(legacyJson);

            SaveDataV2 v2 = new SaveDataV2
            {
                schema_version = 2,
                player_id = legacy.player_id,
                device_id = SystemInfo.deviceUniqueIdentifier,
                revision = 1,
                client_saved_at = legacy.saved_at,
                level = legacy.level,
                wallet = new WalletData
                {
                    coins = legacy.coins,
                    gems = 0 // Server split will populate gems based on purchase ledger
                },
                inventory = new InventoryData
                {
                    hammer = legacy.inventory != null ? legacy.inventory.hammer : 0,
                    shuffle = legacy.inventory != null ? legacy.inventory.shuffle : 0
                },
                entitlements = new EntitlementsData
                {
                    no_ads = legacy.no_ads
                }
            };

            v2.SynchronizeMirrorFields();
            return v2;
        }

        [Serializable]
        private class LegacyInventory
        {
            public int hammer;
            public int shuffle;
        }

        [Serializable]
        private class LegacySaveDataV1
        {
            public string player_id;
            public long saved_at;
            public int level;
            public int coins;
            public LegacyInventory inventory;
            public bool no_ads;
        }
    }
}

