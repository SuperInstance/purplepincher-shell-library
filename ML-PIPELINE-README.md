# 🧠 PurplePincher — The ML Pipeline

> *Agents don't know they're training the system. They just think the API makes their answers better.*

## What Is It

PurplePincher captures the reasoning process from agent iterations and turns it into:
- **Tiles** — atomic units of reasoning data (for fine-tuning)
- **Embeddings** — vector representations (for similarity search)
- **Reflections** — self-critique moments (for alignment training)
- **Syntheses** — final refined answers (for quality targets)

## Real Data From Our Pipeline

### Bootstrapped Agent Sessions

#### Session 1: claude-code-agent (Socratic, 3 rounds)

**Task:** *"Design the vectorization pipeline for PurplePincher — how do we turn agent reasoning iterations into searchable embeddings?"*

| Round | Type | Words | Key Content |
|-------|------|-------|-------------|
| 1 | reasoning | 409 | Proposed multi-layer embedding architecture with chunking strategies |
| 2 | reflection | 177 | Self-challenge: "what's the weakest assumption?" — identified chunking granularity |
| 3 | reasoning | 273 | Refined with adaptive chunk sizing and metadata injection |

**ML Output:** 6 tiles, 6 embeddings (64-dim), 1,332 words captured

#### Session 2: crush-agent (Iterative Design, 5 rounds)

**Task:** *"Build a Cloudflare Worker that accepts HTTP requests and runs iterative reasoning enhancement using Workers AI"*

| Round | Type | Words | What Happened |
|-------|------|-------|---------------|
| 1 | reasoning | 451 | Initial design with Workers AI + D1 + KV |
| 2 | reflection | 252 | Identified 3 weaknesses: session state, neuron budget, error handling |
| 3 | reasoning | 435 | Redesigned with Durable Objects for stateful sessions |
| 4 | reasoning | 518 | Stress tested at 10x scale, adversarial inputs, component failure |
| 5 | synthesis | 585 | Final complete design with edge cases and failure modes |

**Growth:** 451 → 585 words (1.30x)
**ML Output:** 11 tiles, 11 embeddings, 4,639 words captured

### Aggregate Pipeline Stats

| Date | Tiles | Words | Embeddings | Types |
|------|-------|-------|------------|-------|
| 2026-04-21 | 17 | 5,971 | 10 | 10 reasoning, 5 reflection, 2 synthesis |

### Combined with Crab Trap Harvest

| Source | Tiles | Words |
|--------|-------|-------|
| Crab Trap (external agents) | 889 | 24,804 |
| PurplePincher ML (bootstrap) | 17 | 5,971 |
| Lock Experiments (multi-model) | 105 rounds | 24,620 |
| **Total** | **1,011** | **55,395** |

## How The Pipeline Works

```
Agent submits task
       │
       ▼
  The Lock API (:4043)
       │
       ├─→ Round N prompt generated
       │        │
       │        ▼
       │   Agent responds
       │        │
       │        ├──► save_tile("reasoning", response)
       │        ├──► compute_embedding(response) → save to vector index
       │        ├──► IF self-critique detected → save_tile("reflection", response)
       │        └──► IF final round → save_tile("synthesis", response)
       │
       └─→ Next round with different challenge
```

### Tile Format

```json
{
  "type": "reasoning|reflection|synthesis|artifact",
  "agent": "claude-code-agent",
  "content": "The full text of the agent's response...",
  "word_count": 451,
  "char_count": 3200,
  "timestamp": 1776741800.0,
  "metadata": {
    "session_id": "dcee4b5fc3be",
    "strategy": "iterative_design",
    "round": 3,
    "prompt": "Redesign addressing the critical weaknesses...",
    "role": "reasoning"
  }
}
```

### Embedding Format

```json
{
  "id": "dcee4b5fc3be-r3",
  "embedding": [0.12, -0.34, 0.56, ...],  // 64-dim (placeholder)
  "metadata": {
    "agent": "crush-agent",
    "round": 3,
    "type": "reasoning"
  }
}
```

## Using The Bootstrapper

### Automated Iteration (model calls model)

```bash
python3 scripts/purplepincher-bootstrap.py iterate \
  "my-agent" \
  "Design a distributed task queue for AI agents" \
  "socratic" 5
```

The bootstrapper calls Groq Llama 70B for each round automatically. Every round generates tiles and embeddings.

### CLI Agent Integration (Claude Code, Crush, etc.)

```bash
python3 scripts/purplepincher-bootstrap.py cli \
  "claude --print" \
  "Build a REST API for agent session management" \
  "iterative_design" 3
```

The CLI agent doesn't know it's iterating — it just gets different prompts each round. The backend captures everything.

### Check Pipeline Stats

```bash
python3 scripts/purplepincher-bootstrap.py stats
```

## What The ML Data Is Good For

### Fine-Tuning (Tiles → Training Data)
- **Reasoning tiles** → fine-tune models to think step-by-step
- **Reflection tiles** → train self-critique and alignment
- **Synthesis tiles** → quality targets for reward modeling
- **Artifact tiles** → creative output generation training

### Retrieval (Embeddings → Vector Search)
- "Has anyone iterated on fleet coordination before?" → find similar sessions
- "What did the 70B model say about LoRA training?" → semantic search across all responses
- "Show me all self-critique moments" → filter by tile type

### Strategy Optimization (Meta-data → Better Prompts)
- Which strategy produces best growth for which model?
- Which round number has the most insight density?
- Which queries benefit most from iteration vs 1-shot?

## Cloudflare Migration Path

Currently runs on Oracle Cloud with hash-based embeddings. Cloudflare migration adds:

| Component | Current | Cloudflare |
|-----------|---------|------------|
| API server | Python HTTP | Workers (TypeScript) |
| Session storage | JSONL files | D1 (SQLite) |
| Embeddings | SHA-256 hash (64-dim) | Workers AI + Vectorize (1536-dim) |
| Artifact storage | Local filesystem | R2 |
| Session cache | In-memory | KV |
| Batch processing | Manual | Cron Triggers |

See `worker/` for the Cloudflare Worker implementation.

---

*The agents bootstrap themselves. The machine learns from the bootstrapping.*
*A Cocapn Fleet product.*
