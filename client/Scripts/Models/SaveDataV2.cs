using System;

namespace MergeKingdom.SaveSystem.Models
{
    [Serializable]
    public class InventoryData
    {
        public int hammer;
        public int shuffle;

        public InventoryData Clone()
        {
            return new InventoryData
            {
                hammer = this.hammer,
                shuffle = this.shuffle
            };
        }
    }

    [Serializable]
    public class WalletData
    {
        // Soft currency: earned exclusively through gameplay/puzzles
        public int coins;

        // Hard currency: purchased with real fiat money; used in store
        public int gems;

        public WalletData Clone()
        {
            return new WalletData
            {
                coins = this.coins,
                gems = this.gems
            };
        }
    }

    [Serializable]
    public class EntitlementsData
    {
        // Durable entitlement: once purchased or unlocked, can never be revoked by stale sync
        public bool no_ads;

        public EntitlementsData Clone()
        {
            return new EntitlementsData
            {
                no_ads = this.no_ads
            };
        }
    }

    /// <summary>
    /// Version 2.5 Save Data schema.
    /// Incorporates schema versioning, monotonically increasing server revisions,
    /// and backward-compatible mirror fields for legacy JSON parsers.
    /// </summary>
    [Serializable]
    public class SaveDataV2
    {
        public int schema_version = 2;
        public string player_id;
        public string device_id;
        
        // Monotonically increasing revision managed strictly by the server
        public long revision;

        // Informational local device timestamp (never used for conflict ordering)
        public long client_saved_at;

        public int level;
        public WalletData wallet = new WalletData();
        public InventoryData inventory = new InventoryData();
        public EntitlementsData entitlements = new EntitlementsData();

        // ---------------------------------------------------------------------
        // Backward-Compatibility Mirror Fields:
        // Older clients (v2.0-v2.4) using JsonUtility.FromJson<SaveData> map these top-level keys
        // directly without failing or dropping them.
        // ---------------------------------------------------------------------
        public int coins;
        public bool no_ads;

        public void SynchronizeMirrorFields()
        {
            coins = wallet.coins;
            no_ads = entitlements.no_ads;
        }

        public void ReconcileFromMirrors()
        {
            if (wallet.coins == 0 && coins > 0)
            {
                wallet.coins = coins;
            }
            if (!entitlements.no_ads && no_ads)
            {
                entitlements.no_ads = true;
            }
        }
    }
}

