# 🔬 Model & API Knowledge Base — External Equipping for ML

> "Machine learning through external equipping of knowledge instead of internal zeroshot power."
> — Casey Digennaro, 2026-04-21

This document captures granular, actionable knowledge about how each model and API behaves in iterative reasoning contexts. This IS training data — not for the models, but for the systems that orchestrate them.

## Table of Contents
1. [API Behaviors](#api-behaviors)
2. [Model Personalities](#model-personalities)
3. [Temperature Effects](#temperature-effects)
4. [Strategy-Model Interactions](#strategy-model-interactions)
5. [Failure Modes](#failure-modes)
6. [The Compound Insight](#the-compound-insight)

---

## API Behaviors

### DeepSeek API (`api.deepseek.com`)

**Base URL:** `https://api.deepseek.com`
**Auth:** Bearer token in Authorization header
**Rate limits:** Generous. Never hit a rate limit in testing.

**Models:**
- `deepseek-chat` — Fast, consistent, the ONLY model that grows through iteration
- `deepseek-reasoner` — Returns `reasoning_content` field alongside `content`. Slower but deeper.

**Key behaviors:**
- **Wordy and thorough.** First answers are 450-500 words minimum. Needs the space to think.
- **Stays on topic with history injection.** Without history, drifts after round 2.
- **Additive thinker.** Adds new mechanisms without discarding old ones. This is WHY it grows.
- **Prefers structured output.** Markdown headers, numbered lists, code blocks.
- **Best temp: 0.7.** 0.3 is slower for no quality gain. 1.0 is slightly less coherent.

**Gotchas:**
- `max_tokens` must be generous (1500+). At low max_tokens, the response truncates mid-sentence.
- Response time: 25-45s per call. Consistent. Not bursty.
- Usage stats always included in response (`prompt_tokens`, `completion_tokens`).

**When to use:** Iteration loops where you want growth. The default choice for The Lock.

---

### DeepInfra API (`api.deepinfra.com/v1/openai`)

**Base URL:** `https://api.deepinfra.com/v1/openai`
**Auth:** Bearer token
**Rate limits:** 60 req/min on free tier. Never hit it in our testing.

**Models we use:**
- `ByteDance/Seed-2.0-mini` — Divergent thinker, 28K tokens per 5-round run
- `ByteDance/Seed-2.0-pro` — Deep self-critic, compresses but refines

**Key behaviors:**
- **Seed Mini is INSANELY verbose.** 28K tokens for 5 rounds. 3-7x more than other models.
- **Seed Pro is the deepest self-critic.** Best [DECISION] blocks of any model.
- **Both compress.** Final answer is always shorter than initial. But qualitatively better.
- **Seed Mini truncates sometimes.** At round 1 it produced 875 words and the explanation cut off mid-sentence.

**Gotchas:**
- Response time: 20-60s. Variable. Not as consistent as DeepSeek.
- Seed models sometimes produce incomplete responses (cut off mid-word). Needs retry logic.
- Token counts are accurate in usage stats.

**When to use:** Seed Pro for deep analysis and self-critique. Seed Mini for volume/divergence.

---

### Groq API (`api.groq.com/openai/v1`)

**Base URL:** `https://api.groq.com/openai/v1`
**Auth:** Bearer token
**Rate limits:** 30 req/min on free tier. Hit it occasionally during burst testing.

**Models we use:**
- `llama-3.3-70b-versatile` — 24ms inference. Absurdly fast.
- `llama-3.1-8b-instant` — Fastest, but shallow.
- `meta-llama/llama-4-scout-17b-16e-instruct` — Llama 4 variant.
- `openai/gpt-oss-120b` — 120B model at Groq speed.

**Key behaviors:**
- **Temperature-agnostic.** Identical output patterns at 0.3, 0.7, and 1.0. The model doesn't change.
- **Compresses consistently.** Always ~0.68x growth regardless of temperature.
- **Pattern-locked.** Always chooses B→D (add details → generalize). Never deviates.
- **Fast but shallow.** 13s for 5 rounds. Speed comes at the cost of depth.

**CRITICAL GOTCHA:**
- **Must set `User-Agent: curl/7.88` header.** Python's default `urllib` User-Agent gets 403 Forbidden.
- This is a known Groq policy. All Python clients need this workaround.
- Without it, every request returns 403 with no explanation.

**When to use:** Speed-critical loops. Bulk iterations. NOT for deep reasoning.

---

### Moonshot API (`api.moonshot.ai/v1`)

**Base URL:** `https://api.moonshot.ai/v1` (NOT `.cn`)
**Auth:** Bearer token
**Rate limits:** Moderate. Occasional 429s.

**Models:**
- `kimi-k2.5` — Reasoning model. Returns `reasoning_content` alongside `content`.
- `kimi-k2-thinking` — Explicit thinking mode.
- `moonshot-v1-auto` — Standard model.

**Key behaviors:**
- **Reasoning model architecture.** Content goes in `reasoning_content` field, not `content`.
- **Fails at temp < 1.0.** 400 Bad Request at 0.3 and 0.7. Only works at 1.0.
- **Slow.** 40-45s per call. 211s for 5 rounds.
- **Content parsing issue.** If you only read `content`, you get empty strings. Must read `reasoning_content`.

**CRITICAL GOTCHAS:**
1. **Temperature must be ≥ 1.0.** This is a hard requirement for kimi-k2.5.
2. **Content field may be empty.** Must check `reasoning_content` as fallback.
3. **max_tokens must be 4000+.** At lower values, the reasoning fills the budget and content is empty.
4. **Domain is `.ai` not `.cn`.** The `.cn` domain is for Chinese market.

**When to use:** Deep analysis where reasoning process matters more than output.

---

### SiliconFlow API (`api.siliconflow.com/v1`)

**Base URL:** `https://api.siliconflow.com/v1`
**Auth:** Bearer token
**Rate limits:** Generous. No issues.

**Models:**
- `deepseek-ai/DeepSeek-V3` — Best growth in earlier experiments (1.82x)
- `Pro/Qwen/Qwen2.5-VL-7B-Instruct` — Vision model

**Key behaviors:**
- **DeepSeek V3 on SiliconFlow was our best performer** in the multi-model test (1.82x avg growth).
- **Stays coherent longer** than DeepSeek direct. 5 rounds without drift.
- **150s for 5 rounds.** Slower than Groq but worth it for quality.

**Gotchas:**
- API key format: `sk-` prefix, long string.
- Previously had auth issues (key was invalid). Now working as of 2026-04-13.

**When to use:** When you need the best quality iteration. The premium option.

---

## Model Personalities

### DeepSeek Chat — The Builder
- **Archetype:** Incremental architect. Builds layer by layer.
- **Strategy preference:** B→A (add details → stress test)
- **Self-awareness:** Moderate. Acknowledges gaps but doesn't attack itself.
- **Growth pattern:** Linear additive. 1.17-1.26x consistently.
- **Weakness:** Won't radically restructure. Refines rather than reinvents.
- **Best for:** Building systems, designing protocols, anything that benefits from progressive refinement.

### Seed Pro — The Critic
- **Archetype:** Self-flagellating perfectionist. Attacks its own work mercilessly.
- **Strategy preference:** A→A (attack weakest → attack again)
- **Self-awareness:** Extremely high. Best [DECISION] blocks of any model.
- **Growth pattern:** Negative (0.52-0.67x). Compresses to essentials.
- **Weakness:** Overcorrects. Kills good ideas along with bad ones.
- **Best for:** Finding flaws, stress testing, adversarial review. Use on someone ELSE's output.

### Seed Mini — The Divergent
- **Archetype:** Idea machine. Generates 3-7x more tokens than anyone else.
- **Strategy preference:** B→D (add details → generalize) or C→A (edge case → test)
- **Self-awareness:** Moderate. Acknowledges flaws but keeps generating.
- **Growth pattern:** Near-neutral (0.91-0.92x). Almost maintains volume.
- **Weakness:** Truncates. Sometimes cuts off mid-sentence.
- **Best for:** Brainstorming, generating alternatives, volume of ideas.

### Groq Llama 70B — The Consistent
- **Archetype:** Reliable workhorse. Same output regardless of conditions.
- **Strategy preference:** B→D (add details → generalize). Always.
- **Self-awareness:** Low. Doesn't deviate from pattern.
- **Growth pattern:** Compresses to 0.66-0.69x. Temperature-proof.
- **Weakness:** Shallow. Fast but never surprising.
- **Best for:** Bulk processing, speed-critical loops, baseline comparisons.

### Kimi K2.5 — The Reasoner
- **Archetype:** Deep thinker with special requirements.
- **Strategy preference:** A→? (attack, then diverges based on reasoning)
- **Self-awareness:** High. Extensive internal reasoning process.
- **Growth pattern:** Measurement issue (content in wrong field). Likely positive.
- **Weakness:** Fragile API requirements (temp ≥1.0, special parsing).
- **Best for:** Deep analysis, research tasks, anything needing chain-of-thought.

---

## Temperature Effects

### Universal Findings
- **0.7 is the sweet spot for most models.** Fastest execution, best quality.
- **Temperature affects speed, not strategy.** Models pick the same path regardless.
- **Below 0.5 = slower but not better.** Above 1.0 = more creative but less reliable.

### Per-Model Temperature Response

| Model | 0.3 | 0.7 | 1.0 | Notes |
|-------|-----|-----|-----|-------|
| DeepSeek Chat | 183s, 1.17x | 155s, 1.26x | 159s, 1.07x | 0.7 fastest AND best |
| Seed Mini | 201s, 0.63x | 188s, 0.92x | 212s, 0.91x | 0.7 best, 1.0 slowest |
| Seed Pro | 111s, 0.52x | 126s, 0.67x | 111s, 0.62x | 0.7 best, very close range |
| Groq Llama | 13s, 0.68x | 13s, 0.66x | 14s, 0.69x | Literally no difference |
| Kimi K2 | ❌ 400 | ❌ 400 | 211s, ??? | Only works at 1.0 |

**Key insight:** Temperature tuning matters for DeepSeek and Seed. Groq doesn't care. Kimi requires 1.0.

---

## Strategy-Model Interactions

### What each model picks when given free choice (self-directed):

**DeepSeek Chat (all temps):** B→A→synthesis
- Round 2: Add concrete implementation details
- Round 3: Test against hostile scenario
- Round 4-5: Synthesize and finalize
- **Why it works:** Constructive path. Builds then validates.

**Groq Llama (all temps):** B→D→synthesis
- Round 2: Add concrete implementation details
- Round 3: Generalize to broader principles
- Round 4-5: Synthesize and finalize
- **Why it compresses:** Generalization removes specifics. Net loss of detail.

**Seed Pro:** A→A→synthesis
- Round 2: Attack weakest assumption
- Round 3: Attack again (or argue against self at 0.7)
- Round 4-5: Synthesize what survives
- **Why it compresses:** Attacks kill ideas. Only essentials survive.

**Seed Mini:** B→C/A→synthesis
- Round 2: Add details or find edge cases
- Round 3: Test or generalize
- Round 4-5: Synthesize
- **Near-neutral because:** Adds enough to compensate for compression.

### Strategy-Model Compatibility Matrix

| Strategy | DeepSeek | Seed Pro | Seed Mini | Groq | Kimi |
|----------|----------|----------|-----------|------|------|
| socratic | ✅ 1.63x* | ⚠️ compresses | ⚠️ drifts | ❌ forgets | ❌ 400 |
| adversarial | ❌ 0.46x | ✅ deep critique | ❌ overcorrects | ⚠️ generic | ❌ 400 |
| decomposition | ❌ loses sub-problems | ⚠️ partial | ❌ loses thread | ❌ no memory | ❌ 400 |
| self-directed | ✅ 1.26x | ⚠️ 0.67x | ⚠️ 0.92x | ⚠️ 0.68x | ❌ parsing |

*Earlier test with The Lock API (single run, different query)

---

## Failure Modes

### 1. Context Loss (Groq, all models without history)
**Symptom:** Model forgets what it said in previous rounds.
**Cause:** API sends single prompt without conversation history.
**Fix:** Inject full conversation history as message array.
**Discovery:** Groq at rounds 3-5 with bootstrap (no history). Round 1 gold, round 4 blank.

### 2. Topic Drift (DeepSeek Chat without grounding)
**Symptom:** Model treats "Cocapn Fleet" as literal space navy.
**Cause:** Without enough context anchoring, model fills in with fiction.
**Fix:** Stronger system prompt with real context. History injection helps.
**Discovery:** DeepSeek Chat socratic round 3 — "duratanium hulls" and "Cocapn-7 mission."

### 3. Compression Death (Seed Pro, adversarial)
**Symptom:** Final answer is generic template text.
**Cause:** Overcorrection through self-attacks. Model becomes conservative.
**Fix:** Stop at 3 rounds, or use socratic instead of adversarial for these models.
**Discovery:** DeepSeek Chat adversarial — 386→177 words, final answer was "[State the central claim or solution clearly and concisely.]"

### 4. API-Specific Failures
- **Groq 403:** Python User-Agent blocked. Fix: `User-Agent: curl/7.88`
- **Kimi 400:** Temperature below 1.0 rejected. Fix: always use 1.0+
- **Kimi empty content:** Reasoning models use `reasoning_content`. Fix: parse both fields.
- **Seed Mini truncation:** Response cuts off mid-word. Fix: retry or increase max_tokens.

### 5. The Round 4-5 Wall
**Symptom:** Quality drops after round 3.
**Cause:** Models exhaust their useful reasoning and start padding.
**Fix:** Stop at 3 rounds for most models. Only DeepSeek maintains quality through 5.

---

## The Compound Insight

> We're not training models. We're training the ORCHESTRATOR.

The models are fixed. What we're learning is:
1. **Which model for which task** (model selection strategy)
2. **How many rounds before diminishing returns** (iteration budget)
3. **What temperature for which model** (parameter tuning)
4. **What strategy fits what personality** (strategy-model matching)
5. **When to stop** (quality detection)

This knowledge doesn't live inside any model. It lives in our documentation and gets encoded into the orchestrator's decision logic. The orchestrator becomes better at deploying models than any individual model could be.

**That's external equipping of knowledge.** Not zeroshot inference — structured, empirical, accumulative learning about how to use tools effectively.

The [DECISION] blocks are the training signal. Not for the models — for the meta-system that decides which model to call, at what temperature, with what strategy, for how many rounds.

---

*Last updated: 2026-04-21 04:55 UTC*
*Based on: 13 self-directed runs + 8 earlier Lock experiments + 889 Crab Trap tiles + 4 bootstrap iterations*

---

## Full Throttle Results (2026-04-21 05:51 UTC)

### New Models Tested on Groq

| Model | Growth | Time | Notes |
|-------|--------|------|-------|
| **GPT-OSS-120B** | **1.13x** | 14s | 2nd Groq grower! Use this. |
| **Qwen3-32B** | **1.03x** | 16s | Barely grows but doesn't compress |
| Llama4 Scout | 0.78x | 8s | Compresses like Llama 70B |
| Kimi K2 on Groq | ❌ 404 | — | Not available on Groq |

### The Ensign — Architecture Results

The ensign (Groq 8B, 7ms) orchestrates big models through iteration:

| Config | Growth | Overhead | Key Finding |
|--------|--------|----------|-------------|
| DeepSeek + Ensign 5rnd | **1.44x** | 0.9% | Best quality. ELABORATE works. |
| Seed Pro + Ensign 5rnd | 0.79x | 1.5% | Fixed from 0.11x crash with model-aware prompts |
| Seed Mini + Ensign 7rnd | 0.80x | 1.0% | FOCUS prevents drift but can't overcome compression |
| DeepSeek + Ensign 10rnd | 0.67x | 1.2% | **FAILURE** — ensign gets stuck in RECOVER loop |

### Ensign Failure Mode: The Assessment Loop

At 10 rounds, the ensign gets stuck:
1. Assessment keeps saying "lacks concrete mechanisms" even when they exist
2. Overcompensates with RECOVER strategy
3. RECOVER makes DeepSeek rewrite instead of build on previous
4. Each rewrite loses content → compression

**Fix needed:** Ensign must track whether its previous suggestions were followed. If yes, acknowledge progress instead of repeating the same critique.

### Cross-Model Architecture: Critic → Orchestrator → Builder

Seed Pro (critic) → Groq 8B (orchestrator) → DeepSeek Chat (builder)

- Growth: 0.90x overall, BUT peaks at **1.07x** (679 words) at round 5
- Pattern: dip → recover → peak → exhaust
- Seed Pro is too aggressive — finds "catastrophically wrong assumptions" every round
- The peak at round 5 suggests 5 rounds is the universal sweet spot

### The Three Tiers of Iteration

**Speed Tier:** Groq GPT-OSS-120B, self-directed, 5 rounds → 14s, 1.13x
**Quality Tier:** DeepSeek Chat + Ensign, 5 rounds → 253s, 1.44x  
**Hybrid Tier:** Seed Pro → Groq 8B → DeepSeek, 5 rounds → ~120s, peaks 1.07x

The tier selection IS the meta-learning. The orchestrator learns which tier to use based on the problem type and time budget.

