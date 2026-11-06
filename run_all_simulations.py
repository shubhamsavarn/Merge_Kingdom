#!/usr/bin/env python3
"""
Master Verification & Simulation Runner for Chaos Engine Labs Take-Home Assignment.

Executes:
1. Support Incidents 1, 2, and 3 regression prevention tests.
2. Task 4 FIFO Payer-Protection Ledger Split mathematical invariants across 1,000 accounts.
3. Legacy backward-compatibility tests protecting Android 7 and v2.0-v2.4 players.
4. Authoritative gem store item purchases and IAP fulfillment.
"""

import unittest
import sys
import os

# Add workspace directory to python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from tests.test_support_scenarios import TestSupportIncidentsResolution
from tests.test_currency_split_rules import TestCurrencySplitRules
from tests.test_legacy_backward_compatibility import TestLegacyBackwardCompatibility
from tests.test_api_endpoints import TestApiEndpoints
from tests.test_client_sdk import TestClientSDK

def main():
    print("=" * 80)
    print(" CHAOS ENGINE LABS - MERGE KINGDOM VERSION 2.5 VERIFICATION SUITE")
    print(" Senior Systems & AI Engineer Assessment")
    print(" Invariant Rule: 'No player may lose progress, or anything that they paid for.'")
    print("=" * 80)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestSupportIncidentsResolution))
    suite.addTests(loader.loadTestsFromTestCase(TestCurrencySplitRules))
    suite.addTests(loader.loadTestsFromTestCase(TestLegacyBackwardCompatibility))
    suite.addTests(loader.loadTestsFromTestCase(TestApiEndpoints))
    suite.addTests(loader.loadTestsFromTestCase(TestClientSDK))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 80)
    if result.wasSuccessful():
        print(" [PASSED] ALL VERIFICATION GATES PASSED (100% SUCCESS)")
        print(" - Support Incidents 1, 2, and 3 are proven completely eliminated.")
        print(" - Currency Split Invariants hold across 1,000 randomized accounts.")
        print(" - Legacy Android 7 clients safely coexist with Version 2.5 clients.")
        print(" - Hard currency (Gems) and No-Ads entitlements cannot be overwritten.")
        print("=" * 80)
        sys.exit(0)
    else:
        print(" [FAILED] TESTS FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
