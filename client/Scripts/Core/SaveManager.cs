using System;
using UnityEngine;
using MergeKingdom.SaveSystem.Interfaces;
using MergeKingdom.SaveSystem.Models;

namespace MergeKingdom.SaveSystem.Core
{
    /// <summary>
    /// Coordinates save state lifecycle, level completions, purchase events, and cloud synchronization.
    /// Follows SOLID principles:
    /// - Depends on abstractions (DIP) via ISaveStorage, IConflictResolver, ICloudSyncClient, ITimeProvider.
    /// - Replaces legacy static SaveSystem with testable, injectable lifecycle coordinator.
    /// </summary>
    public class SaveManager
    {
        private readonly ISaveStorage _storage;
        private readonly IConflictResolver _conflictResolver;
        private readonly ICloudSyncClient _cloudClient;
        private readonly ITimeProvider _timeProvider;

        public SaveDataV2 Current { get; private set; }

        public event Action<SaveDataV2> OnSaveLoaded;
        public event Action<SaveDataV2> OnSaveCommitted;
        public event Action<SaveDataV2> OnSyncConflictResolved;

        public SaveManager(
            ISaveStorage storage,
            IConflictResolver conflictResolver,
            ICloudSyncClient cloudClient,
            ITimeProvider timeProvider)
        {
            _storage = storage ?? throw new ArgumentNullException(nameof(storage));
            _conflictResolver = conflictResolver ?? throw new ArgumentNullException(nameof(conflictResolver));
            _cloudClient = cloudClient ?? throw new ArgumentNullException(nameof(cloudClient));
            _timeProvider = timeProvider ?? throw new ArgumentNullException(nameof(timeProvider));
        }

        /// <summary>
        /// Called when the game starts.
        /// </summary>
        public void Initialize(string defaultPlayerId)
        {
            Current = _storage.Load();

            if (Current == null)
            {
                Current = new SaveDataV2
                {
                    player_id = defaultPlayerId,
                    device_id = SystemInfo.deviceUniqueIdentifier,
                    schema_version = 2,
                    revision = 0,
                    client_saved_at = _timeProvider.GetCurrentUnixTimeSeconds(),
                    level = 1,
                    wallet = new WalletData { coins = 100, gems = 0 },
                    inventory = new InventoryData { hammer = 1, shuffle = 1 },
                    entitlements = new EntitlementsData { no_ads = false }
                };
                Current.SynchronizeMirrorFields();
                _storage.Save(Current);
            }

            OnSaveLoaded?.Invoke(Current);

            // Fetch any remote updates in the background
            _cloudClient.FetchLatest(Current.player_id, 
                onSuccess: (remoteSave) => {
                    if (remoteSave != null && remoteSave.revision > Current.revision)
                    {
                        ApplyCloudSave(remoteSave);
                    }
                },
                onFailure: (err) => {
                    Debug.LogWarning($"[SaveManager] Initial cloud fetch skipped: {err}");
                });
        }

        /// <summary>
        /// Called after every level completion or in-game transaction.
        /// </summary>
        public void CommitSave()
        {
            if (Current == null) return;

            Current.client_saved_at = _timeProvider.GetCurrentUnixTimeSeconds();
            Current.SynchronizeMirrorFields();

            // 1. Commit locally first to ensure no data loss on power drop
            _storage.Save(Current);
            OnSaveCommitted?.Invoke(Current);

            // 2. Dispatch to cloud (queueing handled internally if offline)
            _cloudClient.Upload(Current,
                onSuccess: (serverAck) => {
                    if (serverAck != null)
                    {
                        // Server acknowledges and provides updated revision sequence
                        Current.revision = Math.Max(Current.revision, serverAck.revision);
                        _storage.Save(Current);
                    }
                },
                onFailure: (error) => {
                    Debug.LogWarning($"[SaveManager] Cloud upload deferred (offline queue active): {error}");
                });
        }

        /// <summary>
        /// Invoked when a cloud update arrives from server or other paired device.
        /// Replaces the dangerous LWW if (server.saved_at > Current.saved_at) logic.
        /// </summary>
        public void ApplyCloudSave(SaveDataV2 incomingServerSave)
        {
            if (incomingServerSave == null) return;

            SaveDataV2 resolved = _conflictResolver.Resolve(Current, incomingServerSave);
            Current = resolved;
            _storage.Save(Current);

            OnSyncConflictResolved?.Invoke(Current);
            Debug.Log($"[SaveManager] Cloud save merged successfully. Level: {Current.level}, Coins: {Current.wallet.coins}, Gems: {Current.wallet.gems}, NoAds: {Current.entitlements.no_ads}");
        }

        public void CompleteLevel(int completedLevel)
        {
            if (completedLevel > Current.level)
            {
                Current.level = completedLevel;
            }
            // Reward 50 coins for clearing puzzle level
            Current.wallet.coins += 50;
            CommitSave();
        }

        public void GrantEntitlement(string entitlementKey)
        {
            if (entitlementKey == "no_ads")
            {
                Current.entitlements.no_ads = true;
                CommitSave();
            }
        }
    }
}

