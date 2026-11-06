# Chaos Engine Labs: Round 2 Interview & Technical Defense Guide
## "Defending the System Design & AI Fluency"

> **Context**: Section 04 and 06 of the take-home brief state:  
> *"Keep your AI conversation. You will use it in the next round."*  
> *"We want to see the judgment behind the design: what you noticed in the facts, what you chose, and why."*

This guide anticipates the critical questions the Chaos Engine Labs founding engineers and tech leads will ask in your defense interview and provides direct, concise, high-signal responses.

---

### Category 1: Deep Reading of the Facts & System Invariants

#### Q1: "Why didn't you just use NTP synchronization on the mobile client to fix the timestamps?"
* **Core Answer**:  
  *"Because client clocks can never be a source of truth in a distributed system, especially on mobile. NTP only mitigates unintentional clock skew. It does not stop intentional date tampering (as in Support Incident 2 where the player changed the date to tomorrow for a chest), nor does it prevent offline race conditions (as in Incident 1 where an airplane-mode phone generated a later timestamp for stale progress). The architectural fix is to abandon client-timestamp Last-Write-Wins entirely in favor of server-assigned monotonic revision sequences and domain-specific merge rules."*

#### Q2: "Why not enforce a minimum client version of 2.5 and force-update all players?"
* **Core Answer**:  
  *"Fact 5 explicitly contains two disqualifying constraints:  
  1. Our last forced update lost 18% of the players who saw the update screen—that level of churn on a live revenue-generating game is unacceptable.  
  2. 10% of players are on versions 2.0–2.1, and about half of them are on Android 7, which cannot update to modern builds at all.  
  Force-updating would permanently destroy ~5% of our daily active player base and alienate paying players on older hardware. Our server-side backward-compatibility adapter allows these legacy clients to play safely without risking hard currency corruption."*

#### Q3: "What happens if a Version 2.2 client on Android 7 syncs while the player also plays Version 2.5 on a phone?"
* **Core Answer**:  
  *"Because Fact 2 proves that Unity's `JsonUtility` silently drops unrecognized fields, a v2.2 client deserializing a v2.5 save will completely discard `gems`. If the server were a dumb blob store, the v2.2 upload would wipe the gems. In our design, the server's Legacy Adapter intercepts v1 JSON, updates level and inventory monotonically, but strictly preserves the player's gem balance and sticky entitlements. A legacy client can never decrease or erase hard currency."*

---

### Category 2: Economic Modeling & The Currency Split

#### Q4: "Why did you choose the FIFO Payer-Protection Ledger Split over a Pro-Rata split?"
* **Core Answer**:  
  *"A pro-rata split divides remaining coins based on the historical ratio of purchased coins to earned coins. While mathematically tidy, it violates the Invariable Rule: 'No player may lose anything that they paid for.' If a paying player bought 5,000 coins for $20 to buy store boosters, spent 1,000 coins on gameplay, and now has 4,000 coins, but store items now cost gems, a pro-rata split would leave a large chunk of their money as soft coins that can no longer purchase store boosters!  
  FIFO assumes that players consumed their free, gameplay-earned coins first. Thus, all remaining coins up to total lifetime purchases are converted into gems ($PaidCoins = \min(C_{current}, \sum \text{PurchasedCoins})$). This 100% guarantees the purchasing power they paid real money for is intact."*

#### Q5: "What is the financial cost to Chaos Engine Labs under your split rule?"
* **Core Answer**:  
  *"Under ASC 606 revenue recognition standards, the cash cost is $0.00 (no refunds are issued). On the balance sheet, it is a reclassification of deferred revenue liabilities from coin obligations to gem obligations. The only true cost is opportunity cost: payers who receive gems to cover their unspent paid coins will defer their next IAP purchase by a few weeks. However, because F2P grinders receive 0 gems for gameplay-earned coins, we create zero unearned hard-currency inflation."*

---

### Category 3: Self-Teaching & AI Fluency (Where the AI was Wrong)

#### Q6: "How did you use AI, and where did the AI give you the wrong answer?"
* **Core Answer**:  
  *"I used AI as an adversarial collaborator to stress-test race conditions and generate boilerplate schemas, but I rejected several of its default suggestions because it lacked domain systems judgment:  
  1. **The AI suggested a forced update**: Standard LLM prompting recommended a hard version gate (`min_version = 2.5`). I had to correct it by pointing to Fact 5's 18% churn rate and the non-updatable Android 7 population.  
  2. **The AI assumed server spend logs existed**: The AI initially drafted an algorithm querying historical coin spend records. I corrected it because Fact 4 explicitly states the server has zero record of how coins were spent on the phone.  
  3. **The AI suggested NTP clock sync**: The AI attempted to keep Last-Write-Wins and fix the client clock. I rejected this because client timestamps can never be trusted in distributed systems, directing it instead to implement domain-monotonic CRDT merges and server sequence numbers."*

---

### Category 4: The Invariant Summary Matrix

| Metric / Scenario | Legacy System (v2.0-v2.4) | Version 2.5 System Design |
| :--- | :--- | :--- |
| **Ordering Authority** | Untrusted Client `DateTimeOffset` | Monotonic Server Revisions |
| **Level Progress** | Blind LWW (can regress) | Monotonic Maximum $\max(L_{local}, L_{remote})$ |
| **Entitlements (No Ads)** | Overwritten by stale device | Sticky-True Logical OR |
| **Hard Currency (Gems)** | Undifferentiated from coins | Server Authoritative Ledger |
| **Android 7 Fleet** | Would be dropped or broken | Indefinite backward compatibility via proxy |
| **Forced Update Churn** | 18% churn risk | 0% churn (Zero forced updates) |

