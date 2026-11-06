package com.chaosengine.mergekingdom.core;

import com.chaosengine.mergekingdom.models.SaveDataV2;

public class DomainMonotonicConflictResolver {

    /**
     * Resolves conflict between local and incoming save state.
     * Enforces the invariant: "No player may lose progress, or anything that they paid for."
     */
    public SaveDataV2 resolve(SaveDataV2 local, SaveDataV2 incoming) {
        if (incoming == null) return local;
        if (local == null) return incoming;

        SaveDataV2 resolved = new SaveDataV2();
        resolved.schema_version = 2;
        resolved.player_id = (local.player_id != null) ? local.player_id : incoming.player_id;
        resolved.device_id = (local.device_id != null) ? local.device_id : incoming.device_id;
        resolved.revision = Math.max(local.revision, incoming.revision);
        resolved.client_saved_at = System.currentTimeMillis() / 1000L;

        // Rule 1: Level is strictly monotonic (resolves Incident 1 and 2)
        resolved.level = Math.max(local.level, incoming.level);

        // Rule 2: Durable Entitlements are sticky-true (resolves Incident 3)
        resolved.entitlements.no_ads = local.entitlements.no_ads || incoming.entitlements.no_ads || local.no_ads || incoming.no_ads;

        // Rule 3: Consumables never drop
        resolved.inventory.hammer = Math.max(local.inventory.hammer, incoming.inventory.hammer);
        resolved.inventory.shuffle = Math.max(local.inventory.shuffle, incoming.inventory.shuffle);

        // Rule 4: Wallet protection
        resolved.wallet.coins = Math.max(local.wallet.coins, incoming.wallet.coins);
        resolved.wallet.gems = Math.max(local.wallet.gems, incoming.wallet.gems);

        // Mirror fields
        resolved.coins = resolved.wallet.coins;
        resolved.no_ads = resolved.entitlements.no_ads;

        return resolved;
    }
}

