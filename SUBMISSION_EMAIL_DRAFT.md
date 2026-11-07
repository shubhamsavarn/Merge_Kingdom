# Chaos Engine Labs Take-Home Assignment: Submission Email Draft

Use the template below when sending your completed assignment to the hiring team at Chaos Engine Labs:

---

**Subject**: Take-Home Submission: AI Engineer – Merge Kingdom v2.5 Architecture – Shubham Savarn

**To**: Reply directly to the assignment invitation email you received from Chaos Engine Labs (keep the same thread)

**Dear Chaos Engine Labs Team,**

Thank you for the assignment invitation. I planned to start on [Planned Start Date, e.g., Saturday, November 7, 2026], and I am submitting this within 48 hours of that date as requested.

Please find attached my completed take-home assignment for the **AI Engineer** position, designing and shipping the Version 2.5 dual-currency system for *Merge Kingdom*.

### Summary of Deliverables Attached:
1. **Written Solution Document**: `CEL_AI_Engineer_Assignment_Solution.md`
   - Detailed answers to Tasks 1 through 6, fully grounded in the provided facts with exact line numbers, table rows, and support messages cited.
   - Complete architectural design adhering to SOLID principles, a FIFO Payer-Protection currency split economic model, and a zero-downtime phased rollout plan.
2. **Full, Unsummarized AI Conversation Logs**: `transcript.jsonl`
   - Unedited, full log export of my AI collaboration session as requested in Section 04.
3. **Executable Codebase & Verification Test Suite**:
   - `client/`: Production Python SDK implementing SOLID interfaces (`ISaveStorage`, `IConflictResolver`, `ICloudSyncClient`, `ITimeProvider`, `SaveManager`) with crash-safe atomic persistence.
   - `java/`: Complete Java object model parity.
   - `server/`: Live-ops backend service in FastAPI with authoritative monotonic revision sequencing, FIFO ledger replay, and an Android 7 legacy adapter proxy.
   - `tests/` & `run_all_simulations.py`: 15 automated test suites (unit, integration, and 1,000-account Monte Carlo simulation) passing with 100% success in < 0.1s.

---

### Key Architectural Highlights:
* **Rule Invariant Preserved**: The design strictly satisfies *"No player may lose progress, or anything that they paid for."*
* **Root Cause Elimination**: Support Incidents 1 (offline queue race), 2 (date tampering / clock rollback), and 3 (entitlement loss on dormant devices) are eliminated via CRDT domain-monotonic merges ($\max(\text{Level})$, sticky-true $\text{NoAds}$, consumable protection) and server sequence numbers replacing untrusted client timestamps.
* **Preserving Android 7 & Zero Churn**: Knowing that forced updates historically lost 18% of players and that ~5% of daily active players are permanently locked onto Android 7, the design deploys an active server proxy ensuring legacy clients can continue playing without risking hard-currency corruption.
* **FIFO Currency Split**: Unspent paid coins are converted to gems ($PaidCoins = \min(C_{current}, \sum \text{Purchases})$), ensuring paying players retain 100% of their store purchasing power without creating unearned hard-currency inflation for F2P players.

---

### Section 04 Statements:
* **AI Collaboration**: I used AI as an adversarial peer reviewer to test race conditions and generate boilerplate schemas. However, I explicitly rejected standard AI recommendations that violated live-ops reality—specifically rejecting forced client updates (due to Fact 5's 18% churn data), rejecting assumptions of server spend logs (contradicted by Fact 4), and rejecting client-side NTP clock fixes in favor of monotonic server sequence revisions.
* **Rough Time Spent**: ~3.5 hours across system analysis, C#/Python/Java architecture, mathematical modeling, and automated test implementation.

I look forward to discussing the design, trade-offs, and failure boundaries in the next round!

Best regards,

**[Your Name]**  
[Your Phone Number]  
[Your LinkedIn / Portfolio Profile]

