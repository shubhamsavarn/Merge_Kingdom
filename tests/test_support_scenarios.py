import unittest
import time
from server.models import SaveStateV2, Inventory, Wallet, Entitlements
from server.storage import GameDatabase
from server.sync_engine import AuthoritativeSyncEngine

class TestSupportIncidentsResolution(unittest.TestCase):
    """
    Directly proves that Version 2.5 architecture eliminates all three support failure modes
    cited in Fact 6 of the assignment brief.
    """

    def setUp(self):
        self.db = GameDatabase()
        self.sync_engine = AuthoritativeSyncEngine(self.db)

    def test_incident_1_tablet_vs_airplane_phone(self):
        """
        Message 1:
        "I played on my tablet all weekend and got to level 160. My son played on my old phone
        in airplane mode on Sunday night, after I stopped. Today I am back at level 151. Where
        did my levels go?"
        
        Proof: Under v2.5 monotonic level resolution, level 160 is preserved when the old phone flushes.
        """
        player_id = "player_incident_1"
        t_sun_evening = 1761700000  # Sunday 18:00
        t_sun_night = 1761710800    # Sunday 21:00 (Later in time!)

        # 1. Tablet finishes weekend at Level 160 and syncs to server
        tablet_save = SaveStateV2(
            player_id=player_id,
            device_id="tablet",
            revision=10,
            client_saved_at=t_sun_evening,
            level=160,
            wallet=Wallet(coins=4000, gems=50),
            inventory=Inventory(hammer=5, shuffle=2),
            entitlements=Entitlements(no_ads=True)
        )
        server_after_tablet, _ = self.sync_engine.sync(tablet_save)
        self.assertEqual(server_after_tablet.level, 160)

        # 2. Son plays offline on old phone to Level 151.
        # Phone local clock generates a LATER timestamp (t_sun_night > t_sun_evening).
        old_phone_save = SaveStateV2(
            player_id=player_id,
            device_id="old_phone",
            revision=5,
            client_saved_at=t_sun_night,
            level=151,
            wallet=Wallet(coins=3800, gems=50),
            inventory=Inventory(hammer=3, shuffle=1),
            entitlements=Entitlements(no_ads=True)
        )

        # 3. Monday morning: airplane mode turned off, old phone upload arrives at server
        server_after_flush, meta = self.sync_engine.sync(old_phone_save)

        # ASSERTION: The level MUST remain 160! Progress is not destroyed!
        self.assertEqual(server_after_flush.level, 160, "Level regressed from 160 to 151! Rule violated.")
        self.assertEqual(server_after_flush.inventory.hammer, 5)
        self.assertGreater(server_after_flush.revision, tablet_save.revision)
        print("[SUCCESS] Incident 1 resolved: Level 160 preserved despite newer offline phone clock.")

    def test_incident_2_date_tampering_time_travel(self):
        """
        Message 2:
        "I changed the date on my phone to tomorrow, opened the free chest early and played
        one level. Then I changed the date back. Later I played more levels on the bus with no
        internet. When I got home, those levels were gone."
        
        Proof: Under v2.5, future clock spoofing does not poison monotonic level and revision state.
        """
        player_id = "player_incident_2"
        t_base = 1761700000
        t_future = t_base + 86400  # Tomorrow (+24 hours)
        t_bus = t_base + 3600      # Restored clock on the bus (+1 hour from base, but 23 hours behind t_future!)

        # 1. Player spoofed clock to tomorrow and cleared Level 51
        spoofed_save = SaveStateV2(
            player_id=player_id,
            device_id="phone",
            revision=1,
            client_saved_at=t_future,
            level=51,
            wallet=Wallet(coins=500, gems=0)
        )
        server_after_spoof, _ = self.sync_engine.sync(spoofed_save)
        self.assertEqual(server_after_spoof.level, 51)

        # 2. Player restored phone clock and played levels 52, 53, 54 on the bus offline
        bus_save = SaveStateV2(
            player_id=player_id,
            device_id="phone",
            revision=1,
            client_saved_at=t_bus,  # Stamped with restored clock (23 hours older than t_future)
            level=54,
            wallet=Wallet(coins=650, gems=0)
        )

        # 3. Arrives home and connects to Wi-Fi
        server_after_home, _ = self.sync_engine.sync(bus_save)

        # ASSERTION: Server must accept Level 54, even though client_saved_at is in the 'past' of t_future!
        self.assertEqual(server_after_home.level, 54, "Bus levels 52-54 were destroyed by future timestamp poison!")
        self.assertEqual(server_after_home.wallet.coins, 650)
        print("[SUCCESS] Incident 2 resolved: Level 54 preserved after date rollback.")

    def test_incident_3_no_ads_stale_device_reversion(self):
        """
        Message 3:
        "I paid for No Ads in March. Last week the ads came back. I play on my phone and on my
        old tablet."
        
        Proof: Under v2.5, durable entitlements are sticky-true and cannot be unset by stale devices.
        """
        player_id = "player_incident_3"
        t_march = 1742000000
        t_lastweek = 1761700000

        # 1. Phone buys No Ads in March
        phone_save = SaveStateV2(
            player_id=player_id,
            device_id="phone",
            revision=20,
            client_saved_at=t_march,
            level=80,
            entitlements=Entitlements(no_ads=True)
        )
        server_state, _ = self.sync_engine.sync(phone_save)
        self.assertTrue(server_state.entitlements.no_ads)

        # 2. Old tablet powered on last week. Has local cached state with no_ads: False.
        # Stamped with t_lastweek (months after March).
        stale_tablet_save = SaveStateV2(
            player_id=player_id,
            device_id="old_tablet",
            revision=15,
            client_saved_at=t_lastweek,
            level=81,
            entitlements=Entitlements(no_ads=False)  # Stale false!
        )

        # 3. Tablet uploads to server
        server_state_after, _ = self.sync_engine.sync(stale_tablet_save)

        # ASSERTION: No Ads entitlement must remain TRUE!
        self.assertTrue(server_state_after.entitlements.no_ads, "Paid No-Ads entitlement was wiped by stale tablet!")
        self.assertEqual(server_state_after.level, 81, "Tablet level progress was also merged.")
        print("[SUCCESS] Incident 3 resolved: No Ads entitlement permanently retained.")

if __name__ == "__main__":
    unittest.main()

