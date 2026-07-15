# CLAUDE.md — Manufacturing AI Assistant

## Project Overview

A Streamlit-based industrial AI platform. It converts natural-language questions into SQL, performs RAG over manufacturing documents, and runs explainable equipment health scoring and root-cause analysis. Built as a portfolio project demonstrating enterprise-grade patterns.

**Entry point:** `streamlit run frontend/Home.py`
**Database:** `data/manufacturing.db` (SQLite)
**LLM config:** `.env` (DeepSeek via OpenAI SDK)

---

## Running the Project

```powershell
# First-time setup (Windows/conda — creates env, installs deps, generates data, builds index)
.\setup.ps1

# Every subsequent launch
.\run.ps1
```

Manual equivalent:
```bash
conda create -n manufacturing-ai python=3.11 -y
conda activate manufacturing-ai
pip install -r requirements.txt
cp .env.example .env          # then set DEEPSEEK_API_KEY
python scripts/generate_data.py
python scripts/init_database.py
python scripts/build_knowledge_index.py
streamlit run frontend/Home.py
```

Tests: `pytest tests/`
Evaluation: `python scripts/run_evaluation.py`

---

## Repository Layout

```
app/
  database/connection.py        # SQLite connection helper
  services/                     # 14 service modules (see below)
  tools/
    schema_tool.py              # DB schema extraction via PRAGMA
    sql_validator.py            # Whitelist + forbidden-keyword SQL guard
    document_loader.py          # MD / TXT / PDF loader
    text_splitter.py            # 800-char chunks, 120-char overlap

frontend/
  Home.py                       # Streamlit entry point
  components/                   # styles, charts, filters, metrics, tables, header
  pages/
    1_Dashboard.py              # Production KPIs
    2_Equipment_Health.py       # Health scores
    3_Root_Cause.py             # RCA UI
    4_AI_Assistant.py           # Chat interface
    5_Knowledge.py              # Document search
    6_Settings.py               # System status

data/
  raw/                          # Source CSVs
  knowledge/                    # embeddings.npy + chunks.json
  manufacturing.db              # Primary data store

docs/
  equipment_manual.md           # Alarm codes, calibration
  quality_sop.md                # Weight QC procedure

scripts/                        # init_database, generate_data, build_knowledge_index, tests
evaluation/datasets/            # JSON test cases for all services
tests/                          # pytest unit tests
```

---

## Core Data Flow

```
User Question → intent_router_service
  ├─ DATABASE  → text_to_sql_service → sql_validator → DB → analysis_service → visualization_service
  ├─ KNOWLEDGE → retrieval_service → knowledge_service
  ├─ HYBRID    → query_decomposition_service → (DB branch + Knowledge branch) → hybrid_analysis_service
  └─ GENERAL   → static response
```

All paths return a `UnifiedAssistantResponse` from `unified_assistant_service.py`.

---

## Service Responsibilities

| Service | What it does |
|---------|-------------|
| `unified_assistant_service` | Orchestrates all paths; single public API |
| `intent_router_service` | Keyword-first (Chinese + English), LLM fallback |
| `text_to_sql_service` | NL→SQL with `temperature=0` |
| `sql_validator` | sqlglot parse; whitelist 4 tables; block DML/DDL; add LIMIT 200 |
| `ai_query_service` | Execute SQL → analysis → visualization pipeline |
| `analysis_service` | LLM analysis; separates facts from interpretations |
| `visualization_service` | Auto chart type selection (line/bar/scatter/pie) via Plotly |
| `retrieval_service` | Cosine-similarity on embeddings.npy |
| `knowledge_service` | RAG answer from top-k retrieved chunks |
| `hybrid_analysis_service` | Merge DB evidence + doc guidance |
| `query_decomposition_service` | Split hybrid question into DB + knowledge sub-questions |
| `equipment_health_service` | Score 0–100: abnormal rate + rework rate + trend + weight deviation |
| `root_cause_service` | Ranking → anomaly types → product contribution → temporal patterns |
| `manufacturing_service` | KPI queries, trend queries, data access layer |

---

## Database Schema

Four tables in `data/manufacturing.db`:

```sql
mst_item        (item_cd PK, item_name)
mst_equipment   (equipment_cd PK, equipment_name, line_name, status)
wrk_order       (order_id PK, item_cd, order_date, order_quantity, rework_quantity)
weight_rawdata  (measurement_id PK, event_time, equipment_cd, item_cd,
                 order_id, weight_diff, std_weight, result_flag)
-- result_flag values: OK | OVER | UNDER
```

Indexes on `weight_rawdata`: event_time, equipment_cd, item_cd, order_id.
Never modify schema without updating `schema_tool.py` and `sql_validator.py` table whitelist.

---

## SQL Safety Rules (do not bypass)

`app/tools/sql_validator.py` enforces:
1. Single-statement only (no semicolons for multi-statement)
2. Only `SELECT` and `UNION` statement types
3. Table whitelist: `mst_item`, `mst_equipment`, `wrk_order`, `weight_rawdata`
4. Forbidden keywords: `INSERT UPDATE DELETE DROP ALTER CREATE PRAGMA EXEC EXECUTE TRUNCATE MERGE REPLACE`
5. Auto-appends `LIMIT 200` if no limit present

When adding a new table, update **both** `sql_validator.py` (ALLOWED_TABLES) and `schema_tool.py`.

---

## LLM Configuration

Configured in `.env` (full template in `.env.example`):

```env
DEEPSEEK_API_KEY=your_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
LLM_TEMPERATURE=0.0
```

The client is initialized with `openai.OpenAI(api_key=..., base_url=...)`.  
Switching providers: change the `.env` values — no code changes needed for OpenAI-compatible APIs.

RAG settings also in `.env`:
```env
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
TOP_K=5
SIMILARITY_THRESHOLD=0.35
```

System prompts live inside each service file (not in a separate `prompts/` directory).  
All prompts require: no invented values, fact vs. interpretation separation, language-matched output, source citations.

---

## Embeddings / RAG

- Model: `paraphrase-multilingual-MiniLM-L12-v2` (handles 50+ languages)
- Chunk size: 800 chars, overlap: 120 chars
- Storage: `data/knowledge/embeddings.npy` + `data/knowledge/chunks.json`
- Rebuild after changing docs: `python scripts/build_knowledge_index.py`
- Chunk IDs format: `doc_XXXX_chunk_XXXX`

---

## Frontend Conventions

- `frontend/components/styles.py` holds all global CSS — add style changes here
- `@st.cache_data(ttl=300)` on dashboard KPI queries — adjust TTL per query cost
- Chat history lives in `st.session_state` — not persisted across page reloads
- Plotly charts are generated in `visualization_service.py`, not in page files
- Filters (date, equipment, product) are in `frontend/components/filters.py`

---

## Adding Features — Checklist

### New data source / table
- [ ] Add CSV to `data/raw/`
- [ ] Update `scripts/init_database.py` to load it
- [ ] Add table name to `ALLOWED_TABLES` in `sql_validator.py`
- [ ] Update `schema_tool.py` if schema extraction needs adjustment
- [ ] Add indexes for common filter columns

### New document to knowledge base
- [ ] Add `.md` or `.pdf` to `docs/`
- [ ] Run `python scripts/build_knowledge_index.py` to rebuild embeddings

### New service
- [ ] Create `app/services/your_service.py` following the dataclass response pattern
- [ ] Register it in `unified_assistant_service.py` if it should be reachable from chat
- [ ] Add test cases to `evaluation/datasets/`

### New page
- [ ] Add `frontend/pages/N_Name.py`
- [ ] Import shared components from `frontend/components/`
- [ ] Streamlit auto-discovers pages alphabetically by filename number prefix

---

## Testing

```bash
pytest tests/                          # unit tests
python scripts/run_evaluation.py       # end-to-end evaluation (requires .env + running DB)
python scripts/test_<service>.py       # individual service tests
```

Evaluation results are written to `evaluation/results/latest_results.json`.

---

## Important Notes

- **Do not hard-code API keys.** Always read from `.env` via `python-dotenv`.
- **Never modify `manufacturing.db` directly during development** — use `scripts/init_database.py` to regenerate.
- **SQL generation is non-deterministic at temperature > 0** — `text_to_sql_service.py` uses temperature=0 intentionally.
- **Knowledge index is not auto-rebuilt** — run `build_knowledge_index.py` after any change to `docs/`.
- **Streamlit caches are TTL-based** — during development, use `st.cache_data.clear()` or restart the server to see fresh data.
