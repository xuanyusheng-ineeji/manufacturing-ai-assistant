# Project Summary — Manufacturing AI Assistant

## What This Project Is

A portfolio-grade industrial AI platform that lets manufacturing engineers query production data in natural language, diagnose equipment problems, and look up SOP/manual documents — all from a single Streamlit web interface. The key technical differentiator is a pipeline that safely converts natural language to SQL, then routes between database queries, RAG knowledge retrieval, and hybrid analysis based on intent detection.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit 1.59 (multi-page app) |
| Backend services | Python 3.x, 14 service modules |
| Database | SQLite (embedded, file-based) |
| LLM | DeepSeek via OpenAI SDK (configurable) |
| Embeddings | sentence-transformers `paraphrase-multilingual-MiniLM-L12-v2` |
| Vector Search | FAISS |
| Visualization | Plotly Express + Graph Objects |
| Data processing | Pandas, NumPy |
| SQL safety | sqlglot (parsing + validation) |
| Runtime | Python 3.11 (conda) |

---

## Directory Structure

```
manufacturing-ai-assistant/
├── app/
│   ├── database/
│   │   └── connection.py          # SQLite connection & query execution
│   ├── services/                  # 14 service modules (see below)
│   └── tools/
│       ├── schema_tool.py         # Extracts DB schema via PRAGMA
│       ├── sql_validator.py       # Whitelist + forbidden-keyword SQL safety
│       ├── document_loader.py     # Loads MD / TXT / PDF docs
│       └── text_splitter.py       # 800-char chunks, 120-char overlap
│
├── frontend/
│   ├── Home.py                    # Landing page with system status
│   ├── components/                # Reusable UI components (styles, charts, filters…)
│   └── pages/
│       ├── 1_Dashboard.py         # Production KPIs & trends
│       ├── 2_Equipment_Health.py  # Health score per equipment
│       ├── 3_Root_Cause.py        # Evidence-based RCA
│       ├── 4_AI_Assistant.py      # Chat interface
│       ├── 5_Knowledge.py         # Document semantic search
│       └── 6_Settings.py          # System status & config
│
├── data/
│   ├── raw/                       # CSV master & transaction files
│   ├── knowledge/                 # embeddings.npy + chunks.json
│   └── manufacturing.db           # SQLite (main data store)
│
├── docs/
│   ├── equipment_manual.md        # Alarm codes E101–E104, calibration steps
│   └── quality_sop.md             # Filling weight QC procedure
│
├── scripts/                       # DB init, data generation, knowledge index build
├── evaluation/                    # Test datasets + benchmark results
├── tests/                         # Unit tests
├── setup.ps1                      # One-command env setup (Windows/conda)
├── run.ps1                        # One-command app launch (Windows/conda)
├── requirements.txt
├── .env / .env.example
└── README.md
```

---

## Database Schema

Four tables in `data/manufacturing.db`:

| Table | Key Columns |
|-------|------------|
| `mst_item` | item_cd, item_name |
| `mst_equipment` | equipment_cd, equipment_name, line_name, status |
| `wrk_order` | order_id, item_cd, order_date, order_quantity, rework_quantity |
| `weight_rawdata` | measurement_id, event_time, equipment_cd, item_cd, order_id, weight_diff, std_weight, result_flag (OK/OVER/UNDER) |

Indexes on `weight_rawdata`: event_time, item_cd, equipment_cd, order_id.

---

## Service Architecture

```
User Question → Intent Router
  ├─ DATABASE  → Text-to-SQL → SQL Validator → DB → Analysis → Visualization
  ├─ KNOWLEDGE → Semantic Retrieval → RAG Answer
  ├─ HYBRID    → Query Decomposition → (DB + Knowledge) → Integrated Analysis
  └─ GENERAL   → Predefined response
```

### Service Map

| Service | Responsibility |
|---------|---------------|
| `unified_assistant_service.py` | Top-level orchestrator; returns `UnifiedAssistantResponse` |
| `intent_router_service.py` | Keyword-first, LLM-fallback intent classification (database / knowledge / hybrid / general) |
| `text_to_sql_service.py` | LLM-based NL→SQL, temperature=0 |
| `sql_validator.py` | Parses SQL with sqlglot; whitelist of 4 tables; blocks DML/DDL; enforces LIMIT 200 |
| `ai_query_service.py` | Executes SQL, pipes results to analysis & visualization |
| `analysis_service.py` | LLM analysis of query results with fact/interpretation separation |
| `visualization_service.py` | Auto-selects chart type (line / bar / scatter / pie) via Plotly |
| `retrieval_service.py` | Cosine-similarity search on sentence-transformer embeddings |
| `knowledge_service.py` | RAG answer generation from retrieved doc chunks |
| `hybrid_analysis_service.py` | Merges database evidence + document guidance |
| `query_decomposition_service.py` | Splits hybrid questions into independent DB + knowledge sub-questions |
| `equipment_health_service.py` | Scores equipment 0–100 (abnormal rate, rework rate, trend, weight deviation) |
| `root_cause_service.py` | Evidence-based RCA: equipment ranking → anomaly types → product contribution → temporal patterns |
| `manufacturing_service.py` | Data access layer: KPI aggregation, trend queries |

---

## LLM Integration

- **Provider:** DeepSeek (OpenAI-compatible API, configurable via `.env`)
- **Model:** `deepseek-chat` (default)
- **Client:** `openai.OpenAI` with custom `base_url`

LLM is used for: Text-to-SQL, result analysis, RAG answer synthesis, intent routing fallback, query decomposition, hybrid integration, and RCA narration.

All prompts enforce: no invented data, fact vs. interpretation separation, language-matched responses, source citations.

---

## Key Design Patterns

### SQL Safety (Defense-in-Depth)
1. sqlglot parses the statement (syntax error → reject)
2. Only `SELECT` and `UNION` allowed
3. Whitelist of exactly 4 table names
4. Forbidden keywords: INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, PRAGMA, EXEC, …
5. Auto-appends `LIMIT 200` if absent

### Intent Routing
- Chinese + English keyword lists for each intent (DATABASE_KEYWORDS, KNOWLEDGE_KEYWORDS, HYBRID_ACTION_KEYWORDS)
- Keyword match wins; LLM classification only as fallback
- Enables zero-latency routing for common queries

### Hybrid Analysis
- `query_decomposition_service` splits one user question into two: a database sub-question and a knowledge sub-question
- Both run independently; `hybrid_analysis_service` integrates the results into one coherent answer
- Prevents hallucination by grounding each half separately

### Equipment Health Scoring
- Abnormal-rate penalty (0–40 pts)
- Rework-rate penalty (0–20 pts)
- Recent-trend penalty (0–20 pts)
- Weight-deviation penalty (0–20 pts)
- Total 0–100; classified as Excellent / Good / Warning / Critical

### RAG Pipeline
- Documents chunked at 800 chars with 120-char overlap
- Chunk IDs: `doc_XXXX_chunk_XXXX`
- Embeddings stored as `.npy`; metadata as `chunks.json`
- Retrieval by cosine similarity; top-k chunks fed to LLM as context

### Caching & Performance
- `@st.cache_data(ttl=300)` on dashboard KPI queries
- SQLite indexes on all common filter columns
- Session-state chat history (no DB persistence needed)

---

## How to Run

```powershell
# Option A — automated (Windows/conda)
.\setup.ps1    # first time only: creates env, installs deps, generates data, builds index
.\run.ps1      # every subsequent launch
```

```bash
# Option B — manual
conda create -n manufacturing-ai python=3.11 -y
conda activate manufacturing-ai
pip install -r requirements.txt
cp .env.example .env   # set DEEPSEEK_API_KEY and adjust other settings
python scripts/generate_data.py
python scripts/init_database.py
python scripts/build_knowledge_index.py
streamlit run frontend/Home.py
```

App runs on http://localhost:8501 by default.

---

## Evaluation

Test datasets in `evaluation/datasets/`:
- `sql_cases.json` — NL→SQL generation cases
- `intent_cases.json` — intent routing cases
- `decomposition_cases.json` — hybrid query decomposition
- `rag_cases.json` — knowledge retrieval cases
- `root_cause_cases.json` — RCA analysis cases

Run with `python scripts/run_evaluation.py`. Results saved to `evaluation/results/latest_results.json`.
