package com.chaosengine.mergekingdom.models;

import java.io.Serializable;

public class SaveDataV2 implements Serializable {
    private static final long serialVersionUID = 2L;

    public int schema_version = 2;
    public String player_id;
    public String device_id;
    public long revision;
    public long client_saved_at;
    public int level;

    public WalletData wallet = new WalletData();
    public InventoryData inventory = new InventoryData();
    public EntitlementsData entitlements = new EntitlementsData();

    // Legacy mirror fields
    public int coins;
    public boolean no_ads;

    public static class WalletData implements Serializable {
        public int coins; // Soft currency: earned by gameplay only
        public int gems;  // Hard currency: bought with real money only
    }

    public static class InventoryData implements Serializable {
        public int hammer;
        public int shuffle;
    }

    public static class EntitlementsData implements Serializable {
        public boolean no_ads; // Sticky true once acquired
    }
}

