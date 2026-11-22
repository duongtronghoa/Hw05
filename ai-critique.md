# AI Critique (Mandatory Appendix)

**Student ID:** 23120127  
**Course:** Software Testing / Performance Testing (HW05 AI)  
**Target SUT:** EShop REST Backend API  
**Word Count:** 239 words (Target: 200–300 words)

---

During this performance testing assignment, the AI demonstrated significant technical assistance in generating initial JMeter test plans and parsing execution metrics. However, critical flaws emerged during the analysis phase. Most notably, the AI exhibited severe aggregation bias: it reported a smooth overall 95th-percentile latency of 18 ms for the Stress scenario, completely obscuring that latency in the final 80-VU tier spiked to 23 ms overall and 32 ms for DELETE operations. Furthermore, the AI committed architectural hallucinations by proposing a connection pool and index optimizations for SQLite—disregarding that SQLite is a file-based embedded engine whose primary key already indexes category records. It also misinterpreted an operating system working-set memory trim at 17:31:10 as V8 garbage collection achieving a supposed 32.4 MiB memory ceiling.

The AI failed to catch these issues because large language models lack autonomous ground-truth grounding; they generate probabilistic textual patterns and naturally favor global averages over phase-specific percentiles unless explicitly constrained. Moreover, the AI evaluated test success purely through HTTP 200 status codes, failing to detect residual database records caused by thread interruptions or recognize that the SUT returns HTTP 200 on non-existent IDs.

The fundamental principle I learned is that AI must never serve as an authoritative oracle in performance testing. While AI excels at rapid boilerplate authoring, human engineers must rigorously cross-examine every analytical assertion against raw execution logs and source code architecture. Verification must rely on ground-truth telemetry rather than persuasive AI prose.
