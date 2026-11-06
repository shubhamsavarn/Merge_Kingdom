using System;
using MergeKingdom.SaveSystem.Interfaces;
using MergeKingdom.SaveSystem.Models;

namespace MergeKingdom.SaveSystem.Core
{
    /// <summary>
    /// Single Responsibility: Resolves multi-device and offline sync conflicts.
    /// Invariant: "No player may lose progress, or anything that they paid for."
    /// 
    /// Adheres to CRDT (Conflict-Free Replicated Data Type) monotonic convergence rules:
    /// - Level: max(local, remote) -> Solves Support Incidents 1 and 2.
    /// - No-Ads: local OR remote -> Solves Support Incident 3.
    /// - Inventory: max(local, remote) for consumables.
    /// - Revision: max(local, remote) server sequence number.
    /// </summary>
    public class DomainMonotonicConflictResolver : IConflictResolver
    {
        private readonly ITimeProvider _timeProvider;

        public DomainMonotonicConflictResolver(ITimeProvider timeProvider)
        {
            _timeProvider = timeProvider ?? throw new ArgumentNullException(nameof(timeProvider));
        }

        public SaveDataV2 Resolve(SaveDataV2 local, SaveDataV2 incoming)
        {
            if (incoming == null) return local;
            if (local == null) return incoming;

            // Ensure mirrors are up to date on both sides before resolving
            local.ReconcileFromMirrors();
            incoming.ReconcileFromMirrors();

            SaveDataV2 resolved = new SaveDataV2
            {
                schema_version = 2,
                player_id = local.player_id ?? incoming.player_id,
                device_id = local.device_id ?? incoming.device_id,

                // Monotonic revision takes the maximum known authoritative sequence number
                revision = Math.Max(local.revision, incoming.revision),
                client_saved_at = _timeProvider.GetCurrentUnixTimeSeconds(),

                // 1. Puzzle Progress: Level can NEVER regress (incident 1 & 2 fix)
                level = Math.Max(local.level, incoming.level),

                // 2. Durable Entitlements: Sticky-true (incident 3 fix)
                entitlements = new EntitlementsData
                {
                    no_ads = local.entitlements.no_ads || incoming.entitlements.no_ads
                },

                // 3. Consumable Inventory: Protects player boosters
                inventory = new InventoryData
                {
                    hammer = Math.Max(local.inventory.hammer, incoming.inventory.hammer),
                    shuffle = Math.Max(local.inventory.shuffle, incoming.inventory.shuffle)
                },

                // 4. Wallet Protection:
                // Hard currency (Gems) is authoritative from server ledger, but if merging offline,
                // we never allow gems to drop silently.
                wallet = new WalletData
                {
                    gems = Math.Max(local.wallet.gems, incoming.wallet.gems),
                    coins = Math.Max(local.wallet.coins, incoming.wallet.coins)
                }
            };

            // Synchronize backward-compatible mirror fields
            resolved.SynchronizeMirrorFields();

            return resolved;
        }
    }
}

