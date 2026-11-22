---
name: hw05-api-performance
description: Design, execute, and review reproducible API performance tests with JMeter and raw JTL evidence. Use for a chosen API endpoint group and Load, Stress, Spike, or soak scenarios.
---

# API performance workflow

Use this skill when a user supplies an API/SUT and asks for a performance test or JTL review. Parameterize endpoint names, credentials, load levels and thresholds from the user's actual SUT; do not carry HW05's values into another application without calibration.

1. Read the implementation/API spec, identify the endpoint group and a complete workflow. List auth, state transitions, cleanup and error semantics. Mark ambiguous expectations before calling them bugs.
2. Establish a repeatable seed and CSV. Use synthetic or authorized accounts, unique names/IDs, and no secrets in audit or report. Record SUT commit, tool versions, hardware and proposed pass criteria **before** measuring.
3. Generate JMeter plans with the same workflow for Load, Stress and Spike. Use CSV and extractors for runtime token/IDs. Validate conditionals with a real 1 VU/1 iteration smoke; static XML load is insufficient. Assert both status and meaningful response/body/state when the SUT returns 200 for no-op writes. Avoid expensive GUI listeners during CLI load.
4. Run short calibration, then full scenarios. Save each raw JTL, log, HTML report, resource time series and run manifest separately. Never overwrite earlier runs. If a timer stops VUs mid-workflow, snapshot leftover IDs, distinguish completed workflows from request success, and clean only test-owned records after preserving evidence.
5. Analyze **raw** JTL with sample counts per label/phase, p95 in milliseconds, error codes and request RPS in a defined hold window. Never average p95 values across windows or infer server maximum from the highest VU tested. Compare resource use and client contention. Freeze AI's first interpretation before independently checking it.
6. Give the user a traceable report with JTL paths/hashes, result tables, workload limits, actual bugs with expected vs actual evidence, and feasible vs unverified optimization ideas. Propose a CI gate that compares like hardware/workload/baseline and repeats noisy regressions. Keep human review, live screenshots and personal narration as explicit user tasks.

For this assignment, run a demonstration on a **complete endpoint group**, not a single isolated request: analyze both `02_categories_list` and `03_products_list` from one real run with the same window and record the sample counts, p95 and RPS. Show the actual skill invocation, input files and output in the student's narrated video; a transcript alone is not a video.
