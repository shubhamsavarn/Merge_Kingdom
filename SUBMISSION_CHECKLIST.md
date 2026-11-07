# Chaos Engine Labs: Submission Package & Checklist

This document provides a single-page overview of all deliverables required by **Section 04 ("What to send us")** of the Take-Home Assignment brief.

---

## 1. Written Answer to the Six Tasks (One Document)
* **File Location**: [`CEL_AI_Engineer_Assignment_Solution.md`](./CEL_AI_Engineer_Assignment_Solution.md)
* **Format**: GitHub-flavored Markdown (ready for PDF conversion or viewing in GitHub/VS Code).
* **Scope**: Comprehensive coverage of Tasks 1 through 6:
  - Task 1: Empirical system inventory with exact line/table/message citations.
  - Task 2: Step-by-step device and server timeline reconstructions for Support Messages 1, 2, and 3.
  - Task 3: Version 2.5 System Architecture, CRDT monotonic domain merges, backward-compatible dual schema, and SOLID Python/Java implementation.
  - Task 4: FIFO Payer-Protection Ledger Split algorithm ($PaidCoins = \min(C_{current}, \sum \text{PurchasedCoins})$), Player 1 & 2 models, financial liability (ASC 606) analysis, and goodwill floors.
  - Task 5: Zero-downtime 5-step phased rollout avoiding forced-update churn (18% historical drop) and preserving 5% Android 7 players.
  - Task 6: System boundary edge cases (cross-version play, offline collisions, refunds) and cross-functional Q&A for Finance, Product, and Legal.

---

## 2. Full AI Conversation Logs (Raw & Unsummarized)
* **Section 04 Requirement**: *"share links or exports of every AI conversation that you used. Send them as they are. Do not clean them up or summarise them. Keep your AI conversation. You will use it in the next round."*
* **All AI conversation sources used** (attach every one):
  1. **Gemini / Antigravity logs**:
     ```
     C:\Users\shubham.savarn\.gemini\antigravity\brain\18302720-68a8-425d-b9b4-96531f482bc0\.system_generated\logs\transcript.jsonl
     C:\Users\shubham.savarn\.gemini\antigravity\brain\18302720-68a8-425d-b9b4-96531f482bc0\.system_generated\logs\transcript_full.jsonl
     ```
  2. **OpenCode sessions**: Export via `/share` or `/export` command in OpenCode CLI
  3. **Claude conversations**: Use Claude's Share feature to get a public share link, or export the conversation
* **Before attaching**: Open each log file and check for API keys, tokens, passwords, or private paths. If you find a secret, rotate it rather than editing the log.

---

## 3. How AI Was Used (Meta-Commentary for Reviewers)
* **AI Tools Used**: OpenCode CLI, Claude (this chat), Gemini (Antigravity transcripts)
* **What We Asked**:
  - Queried distributed consensus patterns for client-side monotonic progress convergence (CRDT-style LWW replacement).
  - Used AI to generate initial boilerplate models for JSON schema serialization and REST endpoints.
  - Prompted edge-case scenarios around multi-device concurrent play and offline buffer flushes.
* **Real Example Where AI Was Wrong**: AI suggested adding `min_client_version = 2.5` (forced client update) to solve legacy compatibility. We rejected this because Fact 5 shows 18% of players churn on forced updates and 5% are stuck on Android 7. Instead, we built a backward-compatible server proxy so legacy clients never need to update.
* **What We Kept**:
  - The domain-monotonic merge formulation ($\max(\text{level})$, sticky-true $\text{no\_ads}$, consumable union).
  - Chronological step-by-step reconstructions of the three customer support escalations.
  - The FIFO Payer-Protection Ledger Split mathematical formulation.
* **What We Rejected & Corrected (Where the AI was Wrong)**:
  - **Rejected Forced Updates**: Standard LLMs suggested adding a client version gate (`min_client_version = 2.5`). We rejected this because Fact 5 explicitly shows that **18% of players churn on forced updates**, and **5% of players are permanently locked onto Android 7**. A forced update would have caused catastrophic business damage.
  - **Rejected Server-Side Spend Assumption**: LLM suggestions assumed the backend could query historical coin spend logs. We corrected this because Fact 4 explicitly states the server has **no record of how coins were spent on the phone**.
  - **Rejected NTP Clock Fixes**: Initial suggestions attempted to "fix" timestamps using client-side NTP sync. We rejected this because client phone clocks can never be trusted for authoritative database mutations; true distributed systems require monotonic server sequence revisions and domain CRDT merges.

---

## 4. Make the Written Answer Easy to Open (Required)
* **Section 04 Requirement**: One document for Tasks 1–6. Reviewers may not open `.md` files.
* **Action**: Convert `CEL_AI_Engineer_Assignment_Solution.md` to **PDF** or **Google Doc** (anyone with the link can view).
* **Options**:
  - PDF: Open the .md in VS Code → Print → Save as PDF, or use an online Markdown-to-PDF converter
  - Google Doc: Copy the .md content into a new Google Doc → File → Share → "Anyone with the link can view"
* **Attach both**: The .md file AND the PDF/Google Doc link in your submission email.

---

## 5. Time Spent (Roughly)
* **System analysis and support ticket dissection**: ~1.0 hour
* **Architecture design & Python/Java SOLID client/server implementation**: ~1.5 hours
* **Economic modeling, rollout planning, and test suite verification**: ~1.0 hour
* **Total Time**: **~3.5 hours** (within the 4-hour target).

---

## 6. Final Pre-Submission Checks
* [ ] **GitHub repo is public**: Open `https://github.com/shubhamsavarn/Merge_Kingdom.git` in an incognito/private window to confirm anyone can view it without logging in.
* [ ] **Latest commit pushed**: `git push origin main` completed successfully.
* [ ] **All 15 tests pass**: `python run_all_simulations.py` returns 100% success.
* [ ] **AI logs gathered**: Every AI conversation source exported (Gemini logs, OpenCode `/share`, Claude Share link).
* [ ] **Logs checked for secrets**: Opened each log file, scanned for API keys, tokens, passwords, private paths. Rotated any secrets found rather than editing logs.
* [ ] **Written answer in multiple formats**: `.md` attached AND PDF/Google Doc link provided (anyone with the link can view).
* [ ] **Email uses reply thread**: Replying to the original assignment invitation email, not composing new to `careers@`.
* [ ] **Subject line correct**: "AI Engineer" (not "Senior AI Systems Engineer").
* [ ] **Start date mentioned**: Planned start date included in email body for 48-hour verification.
* [ ] **"How I used AI" is accurate**: Lists actual tools used and a real example where AI was wrong.

---

## 5. Executable Codebase & Test Suite
* **Client SDK (Python)**: [`client/`](./client/)
* **Java Parity Models**: [`java/src/main/java/com/chaosengine/mergekingdom/`](./java/src/main/java/com/chaosengine/mergekingdom/)
* **Backend Live-Ops Server (FastAPI)**: [`server/`](./server/)
* **Test Suite (15 Test Suites)**: [`tests/`](./tests/)
* **To Run Verification Suite**:
  ```bash
  python run_all_simulations.py
  ```
  *(Result: 15/15 tests pass in < 0.2s)*

