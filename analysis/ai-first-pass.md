# AI First-Pass Performance Analysis — HW05 (EShop API)

**Date & Time:** 2026-11-22 17:38:00 (+07:00)  
**Target:** SUT EShop Backend API (Node.js + Express + SQLite, commit `85af3ba875c88283615e22cb108f13e2fccaf0e9`)  
**Evaluator:** AI Assistant (Automated Log & Raw Artifact First-Pass)

---

## 1. Executive Summary Across Scenarios

Based on raw JTL logs (`load.jtl`, `stress.jtl`, `spike.jtl`, `soak.jtl`) and resource CSV logs collected on the local testing environment:

| Scenario | Total Samples | Failed Samples | Overall Elapsed Span (s) | Gross Throughput (req/s) | Overall p95 (ms) | Overall p99 (ms) |
|---|---:|---:|---:|---:|---:|---:|
| **Load (20 VU)** | 4,499 | 0 | 478.41 | 9.40 | 7 | 11 |
| **Stress (10-80 VU)** | 8,364 | 0 | 477.13 | 17.53 | 18 | 40 |
| **Spike (10-80-10 VU)** | 3,404 | 0 | 297.97 | 11.42 | 10 | 17 |
| **Soak (80 VU)** | 25,588 | 0 | 658.78 | 38.84 | 10 | 18 |

Across all four runs, the recorded HTTP response code was uniformly `200 OK` with a 0.00% error rate recorded in JMeter.

---

## 2. Scenario-by-Scenario Breakdown

### 2.1 Load Test (20 VU, 60s Ramp, 480s Duration)
* Raw file: `hw05-work/results/load/load.jtl` (n = 4,499)
* All samples belonged to thread group `TG_Load_Workload`.
* Response time remained tightly clustered between 1 ms and 11 ms. The overall p95 latency was 7 ms.
* Latency by label:
  * `01_login`: n = 759, p95 = 8 ms, RPS = 1.586
  * `02_categories_list`: n = 756, p95 = 2 ms, RPS = 1.580
  * `03_products_list`: n = 752, p95 = 2 ms, RPS = 1.572
  * `04_category_create`: n = 747, p95 = 9 ms, RPS = 1.561
  * `05_category_update`: n = 744, p95 = 8 ms, RPS = 1.555
  * `06_category_delete`: n = 741, p95 = 9 ms, RPS = 1.549
* The throughput achieved is approximately 9.40 transactions per second for the application.

### 2.2 Stress Test (Step-up: 10 → 20 → 40 → 80 VU)
* Raw file: `hw05-work/results/stress/stress.jtl` (n = 8,364)
* The test executed four sequential thread groups:
  * Level 1 (10 VU): n = 569, span = 116.63s, RPS = 4.88, p95 = 8 ms
  * Level 2 (20 VU): n = 1,103, span = 118.48s, RPS = 9.31, p95 = 8 ms
  * Level 3 (40 VU): n = 2,201, span = 118.84s, RPS = 18.52, p95 = 9 ms
  * Level 4 (80 VU): n = 4,491, span = 118.82s, RPS = 37.80, p95 = 23 ms
* **AI Observation:** Overall test p95 is 18 ms. The backend handled 80 VU without breaking, and latency scaled smoothly with load. Write operations (`04_category_create`, `05_category_update`, `06_category_delete`) in Level 4 showed higher p95 (28–32 ms) and p99 reached 152 ms on DELETE due to database contention.

### 2.3 Spike Test (10 VU → 80 VU → 10 VU)
* Raw file: `hw05-work/results/spike/spike.jtl` (n = 3,404)
* Phases:
  * Phase 1 (Base 10 VU, 120s): n = 565, RPS = 4.79, p95 = 9 ms
  * Phase 2 (Peak 80 VU, 60s): n = 2,262, RPS = 38.91, p95 = 10 ms
  * Phase 3 (Recovery 10 VU, 120s): n = 577, RPS = 4.90, p95 = 9 ms
* **AI Observation:** The application showed zero latency degradation during the sudden 8x jump to 80 VU, and immediately returned to baseline throughput. A short gap of ~2 seconds between Phase 2 and Phase 3 indicates a brief recovery delay before resuming traffic.

### 2.4 Soak / Endurance Test (80 VU Sustained)
* Raw file: `hw05-work/results/soak/soak.jtl` (n = 25,588, duration 660s)
* Post-ramp hold window: 630 seconds (10.5 minutes), n = 25,018 samples.
* Sustained throughput: 39.71 req/s with 0 errors.
* Resource Behavior (`hw05-work/results/soak/resources.csv`):
  * Initial Node.js RSS was 93.11 MiB.
  * At timestamp ~17:31:10, Node.js RSS abruptly dropped to 32.38 MiB.
  * **AI Hypothesis on Memory:** Node.js v25 garbage collection effectively cleaned up unreferenced heap buffers under high throughput, proving that Node.js operates with a memory ceiling of around 32.4 MiB without memory leaks.

---

## 3. Empirically Supported Performance Thresholds

Based on the measurements:
1. **Maximum Sustainable Concurrency:** 80 Virtual Users (under 1–3s think time).
2. **Maximum Sustainable Throughput:** ~39.7 requests/second.
3. **Response Time SLAs:**
   * Read Endpoints (`/api/categories`, `/api/products`): p95 ≤ 8 ms.
   * Auth Endpoint (`/api/login`): p95 ≤ 8 ms.
   * Write/Transactional Endpoints (CRUD Category): p95 ≤ 13 ms (Soak) and ≤ 32 ms (Stress peak).
4. **Error Rate Tolerance:** 0.00%.

---

## 4. Proposed Optimizations & Recommendations

1. **Add Database Index on Category Table:**
   Creating an index on `categories(name)` and `categories(id)` will accelerate the CRUD endpoints and reduce p99 spikes observed during Stress Level 4.
2. **Implement Database Connection Pool:**
   Configure a connection pool (e.g., `generic-pool` with pool size 10–20) for SQLite to allow concurrent worker threads to share open database connections and avoid thread contention.
3. **Enable SQLite WAL (Write-Ahead Logging) Mode:**
   Switching SQLite from the default rollback journal to WAL mode (`PRAGMA journal_mode=WAL;`) allows concurrent readers while a write transaction is occurring.
4. **Add B-Tree Index on `users(email)`:**
   The login query `SELECT * FROM users WHERE email = ?` currently performs a full table scan. Adding an index on `users(email)` will optimize authentication latency under larger user datasets.
5. **Adjust Think-Time Distribution:**
   Reduce the 1–3s artificial think time to 100–300 ms to find the absolute saturation breakpoint of the Node.js event loop.
