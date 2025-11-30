# Missing Functionality & Mismatches

This log records gaps between the README/documented capabilities and the current codebase. Each entry cites the relevant files so we can rebuild the missing pieces without losing context.

## LexAPI_Metabolics (Port 8005)
- **Status (Nov 25):** REST endpoints (`/analyze/metabolism/{user}`, `/analyze/drug_metabolism/{drug}`) and `/health` restored, backed by ClickHouse queries via `MetabolismAnalyzer` and `DrugAnalyzer`.
- **GraphQL:** `/graphql` now reuses the analyzers instead of DuckDB. Future work is to expand coverage once richer metabolomics tables are available.
- **Remaining gaps:** No tool hooks in AI Gateway yet (see section below) and Populomics parity still outstanding.

## LexAPI_Populomics (Port 8006)
- **Status (Nov 25):** `/health`, `/analyze/environmental_risk/{location}`, and `/analyze/disease_risk/{disease}` are live again. Both analyzers now query ClickHouse population tables.
- **Remaining gaps:** Need to wire these endpoints into the AI Gateway tool executor so the agent can request population data. Environmental datasets beyond variant frequencies are still pending.

## AIGateway Tool Coverage vs. README
- **Status (Nov 25):** Tool executor now exposes `get_metabolic_profile`, `get_drug_metabolism`, `get_environmental_risk`, and `get_disease_risk` so the agent can reach Metabolics and Populomics.
- **Update (Nov 25):** System prompt enhanced with complete tool catalog including all 13 available tools. AI now has full agentic freedom with up to 12 iterations for complex reasoning.

## AI Model Server
- **Status (Nov 25):** Migrated from llama.cpp to LM Studio for production deployment
- **Reason:** LM Studio provides better stability and performance with fine-tuned genomics models
- **Port Change:** 8010 → 1234 (LM Studio default)
- **Benefits:** OpenAI-compatible API, easier GPU configuration, user-friendly interface, better error handling

_Last updated: 2025-11-25_

---

### Notes Logged

| Date       | File/Area                                | Observation                                                                                  |
|------------|------------------------------------------|----------------------------------------------------------------------------------------------|
| 2025-11-25 | `demonstrate_capabilities.py` (archived) | Outdated demo script referencing deprecated Metabolics/Populomics behavior; moved to Archive |
| 2025-11-25 | `find_working_clickhouse.py` (archived)  | Manual ClickHouse discovery script superseded by startup health checks; moved to Archive      |
| 2025-11-25 | `install_dependencies.bat` (archived)    | Legacy installer no longer used now that environment is provisioned; moved to Archive        |
| 2025-11-25 | `run_demo.bat` (archived)                | Old demo launcher no longer relevant after new startup flow; moved to Archive                |
| 2025-11-25 | `run_benchmark.py` + `run_benchmark_retry.py` (archived) | Replaced by `run_full_benchmark.py`; archived to avoid duplicate scripts |
| 2025-11-25 | `AI_MODEL_INTEGRATION_PLAN.md` (archived) | Historical LM Studio/ollama plan retained for reference; moved to Archive                   |
| 2025-11-25 | `COMPLETE_SYSTEM_STARTUP_GUIDE.md` (archived) | Superseded by `start_complete_system.bat`; archived to avoid drift                           |
| 2025-11-25 | `DIGITAL_TWIN_INTEGRATION_PLAN.md` (archived) | Documentation snapshot kept in Archive; current state reflected in code                     |
| 2025-11-25 | `USER_EXPERIENCE_FLOW.md` (archived)      | UX plan archived for reference while active docs stay concise                               |
| 2025-11-25 | LexAPI_Metabolics                          | REST/GraphQL endpoints reconnected to ClickHouse analyzers; Gateway tool hooks added        |
| 2025-11-25 | LexAPI_Populomics                         | Environmental & disease risk endpoints restored with ClickHouse-backed analyzers            |
| 2025-11-25 | AI Model Integration                       | Migrated from llama.cpp (port 8010) to LM Studio (port 1234) for improved stability with fine-tuned qwen3-dna-expert model |
| 2025-11-25 | AIGateway Agentic Capabilities            | Increased max tool iterations from 10 to 12; enhanced system prompt for greater AI autonomy and tool exploration freedom |
