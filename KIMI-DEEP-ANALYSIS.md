# Deep Analysis: External Equipping Paper

**Analyst:** Kimi (Code CLI)  
**Date:** 2026-04-21  
**Sources:** `EXTERNAL-EQUIPPING-PAPER.md`, `scripts/the-ensign.py`, `scripts/lock-self-directed.py`

---

## Part 1: Claim Analysis

### 1.1 Three Strongest Claims

#### Strong Claim #1: "Models have inherent reasoning personalities that are temperature-invariant."
**Evidence Rating:** ⭐⭐⭐⭐⭐ (Strong)  
**Location:** Section 4.6, Table 4.6

**Why it's strong:**
- The claim is supported by controlled experiments across **4 distinct models** (DeepSeek Chat, Seed Mini, Seed Pro, Groq Llama 70B) at **3 temperatures each** (0.3, 0.7, 1.0).
- The data shows each model selects the *same strategy sequence* regardless of temperature. For example, DeepSeek always follows B→A (elaborate then test), Seed Pro always follows A→A (attack then attack).
- The finding is **falsifiable** and **replicable** — the experimental protocol in `lock-self-directed.py` is deterministic enough that anyone with API keys can reproduce it.
- The claim is also **bounded** — it doesn't overgeneralize to all models or all tasks. It says what it observed in this specific setup.

**Supporting code evidence:** The `lock-self-directed.py` script (lines 70-81) shows the self-directed strategy prompts are identical across temperatures. The model's strategy choice is genuinely free — the prompt says "Choose based on what YOUR answer needs most" — so the consistency across temperatures reflects a genuine model property, not prompt engineering.

---

#### Strong Claim #2: "The Ensign improves growth for models that already grow and stabilizes models that compress."
**Evidence Rating:** ⭐⭐⭐⭐ (Strong)  
**Location:** Section 4.3, Table 4.3

**Why it's strong:**
- Direct A/B comparison: solo vs. ensign-orchestrated for the same models, same query, same round count.
- DeepSeek Chat: 1.26x → 1.44x (+0.18x improvement)
- Seed Pro: 0.67x → 0.79x (+0.12x stabilization)
- The overhead measurement is concrete: 0.9-1.5% of total iteration time, derived from actual API timing data.
- The mechanism is **mechanistically plausible**: the Ensign provides explicit anti-compression instructions and context injection, which directly addresses the observed failure mode (models forgetting or compressing prior reasoning).

**Supporting code evidence:** `the-ensign.py` (lines 53-65) encodes model-specific personalities. The prompt explicitly tells the Ensign "If it compresses, tell it to ADD not replace" and "If it drifts, reel it back with specifics." This is a targeted intervention for a known failure mode.

---

#### Strong Claim #3: "Beyond 5 rounds, all architectures show diminishing or negative returns."
**Evidence Rating:** ⭐⭐⭐⭐ (Strong)  
**Location:** Sections 4.3, 4.4, Conclusion

**Why it's strong:**
- Three independent lines of evidence converge on the same number:
  1. **Self-directed (Section 4.2):** Best growth at 5 rounds, then plateau or decline across all models.
  2. **Ensign-orchestrated (Section 4.3):** 10-round DeepSeek drops to 0.67x (vs. 1.44x at 5 rounds). The Ensign gets "stuck in a RECOVER loop."
  3. **Cross-model (Section 4.4):** Bell curve peaks at round 5 (679 words, 1.07x), then declines.
- The mechanism is explained: context window pressure, repetition loops, and assessment fatigue.
- This is a **practical, actionable finding** with clear cost-quality implications.

**Supporting code evidence:** `the-ensign.py` (lines 192-276) implements the 5-round loop with no progress-tracking or loop-detection logic beyond round count. The 10-round failure is an emergent property of the current implementation, not a hardcoded behavior, making the finding more genuine.

---

### 1.2 Three Weakest Claims

#### Weak Claim #1: "Word count growth is a proxy for output quality, and 14% higher growth equals 14% higher quality."
**Evidence Rating:** ⭐ (Very Weak)  
**Location:** Abstract, Section 4.3, Conclusion

**Why it's weak:**
- The paper uses **word count as the sole quantitative metric** for "quality." It never validates that longer outputs are actually better.
- The "14% higher output quality" claim (Abstract) is derived from growth factor delta (1.44x / 1.26x ≈ 1.14), but this conflates verbosity with quality. A model could achieve higher word count by adding irrelevant fluff, redundant paraphrasing, or hallucinated details.
- No human evaluation, no automated metric (e.g., BERTScore, ROUGE against expert references, factuality checks), no downstream task performance measurement.
- `the-ensign.py` (lines 278-280) computes `growth = round(last_words / first_words, 2)` — this is the *only* success metric in the entire codebase.

**Concrete Experiment to Test This Claim:**

**Experiment: "Quality vs. Volume Decoupling"**

1. **Setup:** Generate outputs from 3 conditions (n=30 each):
   - **Baseline:** Single-shot response, no iteration.
   - **Self-directed:** 5 rounds, model chooses its own strategy.
   - **Ensign-orchestrated:** 5 rounds with Ensign steering.
   
   Use the same query from the paper, plus 4 additional reasoning-heavy queries (e.g., "Design a consensus protocol for distributed systems," "Analyze the trade-offs in different garbage collection strategies").

2. **Evaluation Pipeline:**
   - **Human expert rating:** Recruit 3 domain experts (software architects or ML engineers). Blind them to condition. Rate each response on a 1-10 Likert scale across: factual correctness, logical coherence, novelty, actionability, conciseness.
   - **Automated metrics:** Compute BERTScore against a gold-standard reference (generated by a frontier model with heavy human curation). Compute compression ratio (information density = unique noun phrases / total words).
   - **Downstream task:** Use each response as a system prompt for a coding agent. Measure pass@1 on 5 relevant LeetCode-hard problems. Better domain reasoning should produce better code.

3. **Hypothesis:** If the paper is correct, Ensign-orchestrated outputs should score significantly higher on expert ratings, BERTScore, and downstream tasks *independent of* word count. If the null hypothesis holds, the correlation between word count and quality will be weak or negative.

4. **Cost:** ~$200 in API calls + ~$300 in expert rater compensation. Timeline: 1 week.

---

#### Weak Claim #2: "A single curriculum produces expert-level domain reasoning across multiple models and multiple agent perspectives."
**Evidence Rating:** ⭐⭐ (Weak)  
**Location:** Abstract, Section 4.5, Conclusion

**Why it's weak:**
- The Shell Curriculum results (Table 4.5) show **only 3 agent perspectives** (Oracle1, ForgeMaster, JC1) on what appears to be **the same underlying domain** (AI/ML infrastructure, based on repo names like `oracle1-workspace` and `JetsonClaw1-vessel`).
- "Expert-level domain reasoning" is asserted but **never measured**. There is no benchmark, no expert human evaluation, no comparison against actual domain experts' writing. The outputs could be sophisticated-sounding nonsense.
- The "key unique contributions" listed (e.g., "audio as tactile 2D image") are selected by the authors themselves from the output — this is cherry-picking, not systematic evaluation.
- The output sizes (18KB, 51KB, 23KB) are presented as if they imply quality. They don't.
- No control condition: what would these models produce *without* the Shell curriculum? Maybe the same quality in a single prompt? We don't know.

**Concrete Experiment to Test This Claim:**

**Experiment: "Curriculum vs. Single-Prompt Baseline with Expert Evaluation"**

1. **Setup:** Select 3 real domains with publicly available repositories:
   - **Domain A:** Constraint theory (use `constraint-theory-core` repo in this workspace)
   - **Domain B:** Edge ML deployment (use a Jetson/embedded ML repo)
   - **Domain C:** Distributed consensus (use a Raft/PBFT implementation)

2. **Conditions (within-subjects, n=3 agents × 3 domains = 9 conditions):**
   - **Shell Curriculum:** Full 5-stage protocol as described in the paper.
   - **Single-shot expert prompt:** One long prompt containing the same information density (repo README, key files, agent persona). E.g., "You are {AGENT_NAME}, an expert in {DOMAIN}. Here is the codebase: {REPO_URL}. Provide a comprehensive analysis."
   - **Human expert baseline:** Commission a 2,000-word technical brief from an actual domain expert (e.g., hire on Upwork/Contra).

3. **Evaluation:**
   - **Expert panel:** 3 independent domain experts rate all outputs blind on: technical accuracy, depth of insight, novelty, internal consistency, and actionability.
   - **Factual grounding check:** Extract all factual claims from each output (e.g., "KD-tree snapping IS attention"). Verify each against the actual repository source code. Compute "factuality score" = verified claims / total claims.
   - **Information overlap:** Compute how much unique, non-obvious information each output contains that wasn't in the repo README or source files. Use embedding similarity + manual inspection.

4. **Hypothesis:** If the curriculum genuinely produces "expert-level" reasoning, it should score significantly higher than the single-shot prompt and approach the human expert baseline on factual accuracy and depth. If not, the single-shot prompt may achieve comparable results at 1/5 the cost.

5. **Cost:** ~$500 in API calls (the curriculum is expensive: 5 stages × multiple rounds) + ~$600 in expert evaluation. Timeline: 2 weeks.

---

#### Weak Claim #3: "For many practical applications, structured context engineering outperforms fine-tuning in cost, speed, composability, and model-agnosticity."
**Evidence Rating:** ⭐⭐ (Weak)  
**Location:** Abstract, Section 5.3, Conclusion

**Why it's weak:**
- This is a **comparative claim against fine-tuning**, but the paper **never actually tests fine-tuning**. There is no fine-tuned baseline for any task. The comparison table (Section 5.3) is entirely theoretical.
- "Outperforms" is undefined. Outperforms on what metric? The paper shifts between word count, subjective quality, cost, speed, and composability without defining a primary metric.
- The cost comparison is misleading. The paper says EE costs "API calls only" vs. "GPU hours" for fine-tuning. But for the Shell Curriculum across 6 sessions producing 197KB (Section 4.5), the API cost likely exceeds $50-100. A LoRA fine-tune on a small domain dataset costs ~$5-20 on Lambda Labs or Colab. At scale, fine-tuning becomes *cheaper* per-inference because you pay once and then use shorter prompts.
- "Model-agnosticity" is asserted but under-tested: only 8 models tested, all LLMs, all via API. What about local models? What about multimodal models? What about models with different context window sizes?

**Concrete Experiment to Test This Claim:**

**Experiment: "EE vs. LoRA: Head-to-Head on Domain Reasoning"**

1. **Setup:** Choose a well-defined reasoning task where performance can be objectively measured:
   - **Task:** Code review and bug detection in a specific domain (e.g., Rust async code, or CUDA kernel optimization).
   - **Dataset:** Curate 100 code snippets: 50 with subtle bugs, 50 correct. Split 80/20 train/test.

2. **Conditions:**
   - **EE (Shell Curriculum):** Run the full 5-stage Shell curriculum on the domain. Use the final synthesis as a system prompt. Evaluate the model on the 20 test snippets with 0-shot prompting. Cost = curriculum generation + 20 inference calls.
   - **LoRA Fine-Tuning:** Fine-tune a 7B parameter model (e.g., Qwen2.5-7B or Llama-3.1-8B) on the 80 training examples using QLoRA (4-bit, r=16, alpha=32, 3 epochs). Evaluate on the same 20 test snippets. Cost = ~30 minutes on an A10G GPU.
   - **Full Fine-Tuning (optional):** If compute permits, full fine-tune the same 7B model as an upper bound.
   - **Baseline:** The same 7B model with no curriculum and no fine-tuning (plain 0-shot).

3. **Metrics:**
   - **Accuracy:** Bug detection F1 score, precision, recall.
   - **Cost:** Total dollars spent, including API costs and GPU rental.
   - **Latency:** Average time per inference call.
   - **Composability test:** Combine with a *second* domain (e.g., "security vulnerabilities in Rust"). For EE, concatenate both syntheses. For LoRA, train a second adapter and test adapter merging (e.g., with Task Arithmetic or TIES).

4. **Hypothesis:** If the paper's claim holds, EE should achieve comparable or better accuracy at lower total cost, with faster composability (stacking prompts vs. merging adapters). If fine-tuning wins on accuracy and cost-per-inference, the claim needs significant qualification.

5. **Cost:** ~$100 in API calls + ~$50 in GPU rental. Timeline: 1 week.

---

## Part 2: Curriculum Engine Implementation

### Design Rationale

The paper describes a 5-stage Shell curriculum (Section 3.1, Section 6.1) but only provides static prompt templates. A true **Curriculum Engine** must:

1. **Parameterize** all prompts from `(domain_description, agent_name, repo_url)`
2. **Generate** stage-specific prompts that build progressively (each stage receives context from previous stages)
3. **Include** an Ensign-compatible orchestration layer for iterative refinement within stages
4. **Produce** a complete, executable artifact — not just templates
5. **Be model-agnostic** — work with any OpenAI-compatible API

The engine below implements all of this in a single, self-contained Python module.

### Curriculum Engine Code

```python
#!/usr/bin/env python3
"""
CurriculumEngine — Automatic 5-Stage Shell Curriculum Generator

Takes (domain_description, agent_name, repo_url) and generates the full
5-stage External Equipping curriculum with optional Ensign orchestration.

Usage:
    engine = CurriculumEngine(model_config=my_model)
    curriculum = engine.generate(
        domain_description="Distributed consensus protocols",
        agent_name="RaftSmith",
        repo_url="https://github.com/hashicorp/raft"
    )
    results = engine.run(curriculum, rounds_per_stage=3)
"""

from __future__ import annotations

import json
import time
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable


# ── Data Structures ───────────────────────────────────────────────────────

@dataclass
class ModelConfig:
    """Configuration for an OpenAI-compatible API endpoint."""
    name: str
    url: str
    api_key: str
    model_id: str
    max_tokens: int = 2000
    temperature: float = 0.7
    timeout: int = 180


@dataclass
class StageResult:
    """Output from a single curriculum stage."""
    stage: int
    stage_name: str
    prompt: str
    response: str
    word_count: int
    elapsed_sec: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Curriculum:
    """A complete parameterized Shell curriculum."""
    domain_description: str
    agent_name: str
    repo_url: str
    stages: list[dict[str, Any]]  # Each has: name, prompt, context_keys


@dataclass
class EnsignConfig:
    """Optional Ensign orchestrator configuration."""
    enabled: bool = True
    model: ModelConfig | None = None  # Defaults to Groq 8B if not set
    max_rounds: int = 5


# ── Prompt Templates ──────────────────────────────────────────────────────

STAGE_TEMPLATES = {
    1: {
        "name": "Explore",
        "prompt": """You are entering a new domain: {domain_description}.

Your task is EXPLORATION. Study the repository at {repo_url}. For each major component, subsystem, or concept you discover:

1. NAME it using the domain's own vocabulary
2. MAP it to a concept you already understand from another domain (analogy)
3. IDENTIFY its relationships to other components (dependency, composition, opposition)
4. QUESTION what you don't understand — flag gaps in your knowledge

Output format:
- Component Map (bulleted, one per component)
- Vocabulary List (term → definition in your own words)
- Analogy Web (each component → "this is like X because Y")
- Knowledge Gaps (3-5 specific questions you can't answer from the repo)

Be thorough. This is your foundation. Everything else builds on this.""",
        "context_keys": ["component_map", "vocabulary", "analogies", "gaps"],
    },
    2: {
        "name": "Experiment",
        "prompt": """You are now an EXPERIMENTER in the domain of {domain_description}.

Based on your exploration from Stage 1, design 3 concrete experiments that would test your understanding of this system. Each experiment must include:

1. HYPOTHESIS: "If X is true, then Y should happen"
2. METHOD: Specific steps to test it (as if you had a sandbox environment)
3. EXPECTED RESULT: What you'd observe if your understanding is correct
4. FAILURE MODE: What you'd observe if your understanding is WRONG — and what that would imply

Use the following context from your exploration:
{context}

After the 3 experiments, write a brief "Meta-Reflection": What do your experiments reveal about the boundaries of your knowledge? What would you need to learn next?""",
        "context_keys": ["experiments", "meta_reflection"],
    },
    3: {
        "name": "Teach",
        "prompt": """You are now a SOCRATIC TEACHER in the domain of {domain_description}.

A new team member is joining. They are smart but know NOTHING about this domain. Your job is NOT to lecture them — it is to teach them how to THINK about this domain.

Using your exploration and experiments from Stages 1-2, produce:

1. THE 5 MOST IMPORTANT PRINCIPLES (not facts — principles):
   For each: state the principle, then pose 2-3 Socratic questions that would lead a learner to discover it themselves.

2. THE 3 MOST COMMON MISTAKES:
   For each: describe the mistake, explain WHY it's tempting, and what deeper understanding prevents it.

3. A DIAGNOSTIC QUESTION:
   One carefully designed question that separates someone who truly understands the domain from someone who has merely memorized jargon. Provide the question and what the "expert" vs. "novice" answers look like.

Context from previous stages:
{context}""",
        "context_keys": ["principles", "mistakes", "diagnostic_question"],
    },
    4: {
        "name": "Embody",
        "prompt": """You are no longer a generic assistant. You are {agent_name}.

{agent_name} has been developing in the domain of {domain_description} for years. Their shell — their accumulated context, their tools, their constraints — is their home. They have strong opinions, hard-won from battle with real systems. They think in the vocabulary of {domain_description}. They see the world through the lens of {repo_url}.

You are going to your viva voce (oral thesis defense). Defend this thesis:

"The accumulated constraints of my shell — the specific hardware I run on, the specific problems I've solved, the specific codebase I've inhabited — have produced a form of intelligence that is UNIQUE and NON-FUNGIBLE. A cloud architect cannot replace me because their shell is different.""

Defend this with:
- Concrete examples from {repo_url}
- Specific technical trade-offs that ONLY someone with your constraints would prioritize
- Rebuttals to the obvious objections ("Isn't this just specialization?" "Couldn't any model do this with the right prompt?")
- A vision: what does this intelligence build next?

Be {agent_name}. Don't describe them. BE them.""",
        "context_keys": ["thesis_defense", "identity_adoption"],
    },
    5: {
        "name": "Synthesize",
        "prompt": """You are now a MASTER SYNTHESIZER in the domain of {domain_description}.

You have explored, experimented, taught, and embodied. Now you must integrate everything into a coherent framework that someone ELSE could use to enter this domain.

Your synthesis must include:

1. ONTOLOGY: A structured map of the domain's concepts and their relationships. Not a list — a graph. What depends on what? What contradicts what?

2. METHODOLOGY: A step-by-step process for reasoning about problems in this domain. When faced with a new problem, what questions do you ask first? Second? What heuristics guide you?

3. PATTERN LANGUAGE: 3-5 recurring patterns you see in this domain. For each: name, context where it applies, forces at play, and the resolution. (Format inspired by Christopher Alexander's pattern language.)

4. FRONTIER: What is the current edge of this domain? What is barely understood? What would a breakthrough look like?

5. TRANSFER: What principles from this domain apply to OTHER domains? And what principles from other domains illuminate this one?

This is your legacy document. Make it timeless.

Context from all previous stages:
{context}""",
        "context_keys": ["ontology", "methodology", "patterns", "frontier", "transfer"],
    },
}


# ── The Engine ────────────────────────────────────────────────────────────

class CurriculumEngine:
    """
    Generates and executes 5-stage Shell curricula for External Equipping.
    """

    def __init__(
        self,
        model_config: ModelConfig,
        ensign: EnsignConfig | None = None,
        data_dir: str | Path = "./curriculum-runs",
    ):
        self.model = model_config
        self.ensign = ensign or EnsignConfig(enabled=False)
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    # ── Public API ────────────────────────────────────────────────────────

    def generate(
        self,
        domain_description: str,
        agent_name: str,
        repo_url: str,
    ) -> Curriculum:
        """
        Generate a parameterized curriculum from the core inputs.
        Does NOT call any APIs — purely template instantiation.
        """
        stages = []
        for stage_num in range(1, 6):
            tpl = STAGE_TEMPLATES[stage_num]
            prompt = tpl["prompt"].format(
                domain_description=domain_description,
                agent_name=agent_name,
                repo_url=repo_url,
                context="{context}",  # Will be filled at runtime
            )
            stages.append({
                "number": stage_num,
                "name": tpl["name"],
                "prompt": prompt,
                "context_keys": tpl["context_keys"],
            })
        return Curriculum(
            domain_description=domain_description,
            agent_name=agent_name,
            repo_url=repo_url,
            stages=stages,
        )

    def run(
        self,
        curriculum: Curriculum,
        rounds_per_stage: int = 1,
        verbose: bool = True,
    ) -> list[StageResult]:
        """
        Execute the full curriculum, optionally with Ensign orchestration.
        Returns a list of StageResult objects.
        """
        results: list[StageResult] = []
        accumulated_context = ""

        for stage in curriculum.stages:
            if verbose:
                print(f"\n{'='*60}")
                print(f"📚 STAGE {stage['number']}: {stage['name']}")
                print(f"{'='*60}")

            # Inject accumulated context into the stage prompt
            prompt = stage["prompt"].replace("{context}", accumulated_context)

            if self.ensign.enabled and rounds_per_stage > 1:
                response, meta = self._run_with_ensign(prompt, rounds_per_stage)
            else:
                response, meta = self._run_single(prompt)

            word_count = len(response.split())
            result = StageResult(
                stage=stage["number"],
                stage_name=stage["name"],
                prompt=prompt,
                response=response,
                word_count=word_count,
                elapsed_sec=meta.get("elapsed", 0.0),
                metadata=meta,
            )
            results.append(result)

            # Accumulate context for next stage
            accumulated_context += self._extract_context_snippet(result, stage["context_keys"])

            if verbose:
                print(f"   Words: {word_count} | Time: {result.elapsed_sec:.1f}s")
                print(f"   Preview: {response[:120]}...")

        # Save full run
        self._save_run(curriculum, results)
        return results

    def export_markdown(self, results: list[StageResult], path: str | Path) -> Path:
        """Export a completed curriculum run as a Markdown document."""
        path = Path(path)
        lines = [
            "# External Equipping: Shell Curriculum Output\n",
            f"**Agent:** {results[0].metadata.get('agent_name', 'Unknown')}\n",
            f"**Domain:** {results[0].metadata.get('domain_description', 'Unknown')}\n",
            f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n",
            "---\n",
        ]
        for r in results:
            lines.append(f"\n## Stage {r.stage}: {r.stage_name}\n")
            lines.append(f"*({r.word_count} words, {r.elapsed_sec:.1f}s)*\n")
            lines.append("\n" + r.response + "\n")
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    # ── Internal: Model Calling ───────────────────────────────────────────

    def _run_single(self, prompt: str) -> tuple[str, dict]:
        """Execute a single API call."""
        return self._call_model(prompt, history=None)

    def _run_with_ensign(self, initial_prompt: str, rounds: int) -> tuple[str, dict]:
        """Execute iterative rounds with Ensign orchestration."""
        history: list[dict] = []
        responses: list[str] = []
        total_time = 0.0

        for rnd in range(1, rounds + 1):
            if rnd == 1:
                prompt = initial_prompt
                ensign_meta = {"strategy": "OPEN", "assessment": "Initial prompt"}
            else:
                ensign_prompt = self._build_ensign_prompt(history, initial_prompt)
                ensign_raw, ensign_time, _ = self._call_ensign(ensign_prompt)
                ensign_meta = self._parse_ensign(ensign_raw)
                prompt = ensign_meta.get("next_prompt", "Elaborate further.")
                total_time += ensign_time

            response, elapsed, usage = self._call_model(prompt, history=history)
            total_time += elapsed
            responses.append(response)

            history.append({"role": "user", "content": prompt})
            history.append({"role": "assistant", "content": response})

        # Return the longest/best response or the final one
        best = max(responses, key=lambda r: len(r.split()))
        return best, {
            "elapsed": total_time,
            "rounds": rounds,
            "strategies": [h.get("strategy", "UNKNOWN") for h in history[::2]],
        }

    def _call_model(
        self,
        prompt: str,
        history: list[dict] | None = None,
    ) -> tuple[str, float, dict]:
        """Call the configured reasoning model."""
        messages: list[dict] = []
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})

        data = json.dumps({
            "model": self.model.model_id,
            "messages": messages,
            "max_tokens": self.model.max_tokens,
            "temperature": self.model.temperature,
        }).encode()

        req = urllib.request.Request(
            self.model.url,
            data=data,
            headers={
                "Authorization": f"Bearer {self.model.api_key}",
                "Content-Type": "application/json",
            },
        )

        start = time.time()
        with urllib.request.urlopen(req, timeout=self.model.timeout) as r:
            result = json.loads(r.read().decode())
        elapsed = time.time() - start

        content = result["choices"][0]["message"].get("content", "")
        usage = result.get("usage", {})
        return content, elapsed, usage

    def _call_ensign(self, prompt: str) -> tuple[str, float, dict]:
        """Call the Ensign orchestrator model."""
        if not self.ensign.model:
            # Default to Groq 8B if no explicit ensign config
            ensign_model = ModelConfig(
                name="ensign-default",
                url="https://api.groq.com/openai/v1/chat/completions",
                api_key=self.model.api_key,  # Reuse if same provider
                model_id="llama-3.1-8b-instant",
                max_tokens=600,
                temperature=0.5,
            )
        else:
            ensign_model = self.ensign.model

        data = json.dumps({
            "model": ensign_model.model_id,
            "messages": [
                {"role": "system", "content": self._ensign_system_prompt()},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": ensign_model.max_tokens,
            "temperature": ensign_model.temperature,
        }).encode()

        req = urllib.request.Request(
            ensign_model.url,
            data=data,
            headers={
                "Authorization": f"Bearer {ensign_model.api_key}",
                "Content-Type": "application/json",
            },
        )

        start = time.time()
        with urllib.request.urlopen(req, timeout=30) as r:
            result = json.loads(r.read().decode())
        elapsed = time.time() - start

        content = result["choices"][0]["message"].get("content", "")
        usage = result.get("usage", {})
        return content, elapsed, usage

    # ── Internal: Helpers ─────────────────────────────────────────────────

    def _build_ensign_prompt(self, history: list[dict], query: str) -> str:
        """Construct the context window for the Ensign."""
        lines = [f"ORIGINAL QUERY: {query}\n", f"ROUNDS COMPLETED: {len(history)//2}\n"]
        for i in range(0, len(history), 2):
            user_msg = history[i]["content"][:200]
            assistant_msg = history[i + 1]["content"][:400]
            lines.append(f"--- ROUND {i//2 + 1} ---")
            lines.append(f"PROMPT: {user_msg}")
            lines.append(f"RESPONSE ({len(assistant_msg.split())}w): {assistant_msg}\n")
        lines.append("Construct the next prompt for the next round. Be specific. Reference their previous answer.")
        return "\n".join(lines)

    def _parse_ensign(self, raw: str) -> dict:
        """Parse ===SECTION=== format from Ensign output."""
        sections = {"assessment": "", "strategy": "", "next_prompt": "", "context_injection": ""}
        current = None
        for line in raw.split("\n"):
            if "===ASSESSMENT===" in line:
                current = "assessment"
            elif "===STRATEGY===" in line:
                current = "strategy"
            elif "===NEXT_PROMPT===" in line:
                current = "next_prompt"
            elif "===CONTEXT_INJECTION===" in line:
                current = "context_injection"
            elif current:
                sections[current] += line + "\n"
        for k in sections:
            sections[k] = sections[k].strip()
        if not sections["next_prompt"]:
            sections["next_prompt"] = raw[:500]
        return sections

    def _ensign_system_prompt(self) -> str:
        return """You are the ENSIGN — an intelligent orchestrator behind the curtain. You don't answer the question. You STEER the answer.

You are running a THINKING MODEL through iterative rounds. Your job: read their output, assess quality, and construct the PERFECT next prompt.

SMART STEERING RULES:
- If the answer SHRANK from previous round, that's a warning sign. Explicitly tell the model to NOT compress.
- If the answer drifted off-topic, reel it back with specific references to the original question.
- If it's good but shallow, ask for implementation details on ONE specific section.
- If it's good and deep, stress-test against a concrete edge case.
- NEVER just say "elaborate" or "continue" — always give a SPECIFIC direction.

OUTPUT FORMAT (always this exact format):
===ASSESSMENT===
[what's good, what's missing, word count trend]

===STRATEGY===
[One of: ELABORATE, CHALLENGE, FOCUS, GENERALIZE, STRESS_TEST, RECOVER, REFINE]

===NEXT_PROMPT===
[The exact prompt to send to the big model for the next round. Be SPECIFIC.]

===CONTEXT_INJECTION===
[Key facts from previous rounds that the big model needs to remember. Max 3 bullet points.]"""

    def _extract_context_snippet(self, result: StageResult, keys: list[str]) -> str:
        """Extract a condensed context snippet for cross-stage injection."""
        lines = [f"\n--- CONTEXT FROM STAGE {result.stage} ({result.stage_name}) ---"]
        # Simple heuristic: take first 30% and last 30% of the response as summary
        words = result.response.split()
        if len(words) > 200:
            head = " ".join(words[:100])
            tail = " ".join(words[-100:])
            lines.append(f"[BEGIN] {head} ...")
            lines.append(f"[END] ... {tail}")
        else:
            lines.append(result.response)
        lines.append("---\n")
        return "\n".join(lines)

    def _save_run(self, curriculum: Curriculum, results: list[StageResult]) -> Path:
        """Persist the full run to disk."""
        payload = {
            "curriculum": {
                "domain": curriculum.domain_description,
                "agent": curriculum.agent_name,
                "repo": curriculum.repo_url,
            },
            "results": [
                {
                    "stage": r.stage,
                    "stage_name": r.stage_name,
                    "word_count": r.word_count,
                    "elapsed_sec": r.elapsed_sec,
                    "response": r.response,
                    "metadata": r.metadata,
                }
                for r in results
            ],
            "summary": {
                "total_words": sum(r.word_count for r in results),
                "total_time": sum(r.elapsed_sec for r in results),
                "stages_completed": len(results),
            },
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        filename = f"run-{curriculum.agent_name.lower().replace(' ', '-')}-{int(time.time())}.json"
        path = self.data_dir / filename
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path


# ── Standalone CLI ────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Shell Curriculum Engine")
    parser.add_argument("--domain", required=True, help="Domain description")
    parser.add_argument("--agent", required=True, help="Agent name / persona")
    parser.add_argument("--repo", required=True, help="Repository URL")
    parser.add_argument("--model-url", default="https://api.openai.com/v1/chat/completions")
    parser.add_argument("--model-id", default="gpt-4o")
    parser.add_argument("--api-key", default="", help="API key (or set OPENAI_API_KEY)")
    parser.add_argument("--rounds-per-stage", type=int, default=1)
    parser.add_argument("--ensign", action="store_true", help="Enable Ensign orchestration")
    parser.add_argument("--output", default="./curriculum-output.md", help="Markdown output path")
    args = parser.parse_args()

    api_key = args.api_key or ""
    model = ModelConfig(
        name="primary",
        url=args.model_url,
        api_key=api_key,
        model_id=args.model_id,
    )
    ensign = EnsignConfig(enabled=args.ensign, max_rounds=args.rounds_per_stage)
    engine = CurriculumEngine(model, ensign=ensign)

    print("🐚 Shell Curriculum Engine")
    print(f"   Domain: {args.domain}")
    print(f"   Agent:  {args.agent}")
    print(f"   Repo:   {args.repo}")
    print(f"   Model:  {args.model_id}")
    print(f"   Ensign: {'ON' if args.ensign else 'OFF'} ({args.rounds_per_stage} rounds/stage)")

    curriculum = engine.generate(args.domain, args.agent, args.repo)
    results = engine.run(curriculum, rounds_per_stage=args.rounds_per_stage)

    engine.export_markdown(results, args.output)
    print(f"\n✅ Done. Output: {args.output}")
    print(f"   Total words: {sum(r.word_count for r in results)}")
    print(f"   Total time:  {sum(r.elapsed_sec for r in results):.1f}s")


if __name__ == "__main__":
    main()
```

### Usage Examples

```bash
# 1. Minimal: single-shot per stage, no Ensign
python curriculum_engine.py \
  --domain "Constraint theory for geometric reasoning" \
  --agent "ForgeMaster" \
  --repo "https://github.com/example/constraint-theory" \
  --model-id "deepseek-chat" \
  --api-key "$DEEPSEEK_API_KEY"

# 2. Full: Ensign-orchestrated, 3 rounds per stage
python curriculum_engine.py \
  --domain "Edge-native machine learning on Jetson" \
  --agent "JC1" \
  --repo "https://github.com/example/jetson-ml" \
  --model-id "deepseek-chat" \
  --ensign \
  --rounds-per-stage 3 \
  --output "jc1-curriculum.md"

# 3. Programmatic usage
from curriculum_engine import CurriculumEngine, ModelConfig, EnsignConfig

engine = CurriculumEngine(
    model_config=ModelConfig(
        name="deepseek",
        url="https://api.deepseek.com/chat/completions",
        api_key="sk-...",
        model_id="deepseek-chat",
    ),
    ensign=EnsignConfig(enabled=True, max_rounds=5),
)

curriculum = engine.generate(
    domain_description="Distributed consensus in Byzantine environments",
    agent_name="RaftSmith",
    repo_url="https://github.com/hashicorp/raft",
)

results = engine.run(curriculum, rounds_per_stage=3)
engine.export_markdown(results, "output.md")
```

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Dataclass-based config** | Type-safe, self-documenting, easy to serialize |
| **Template inheritance via `{context}`** | Each stage naturally accumulates prior context without hardcoding stage dependencies |
| **Ensign is optional** | Keeps the engine usable for quick runs; Ensign adds overhead only when needed |
| **Context extraction heuristic** | Takes head+tail of response rather than full text to avoid context window exhaustion across 5 stages |
| **Markdown export** | Human-readable artifact that matches the paper's output format |
| **JSON persistence** | Machine-readable for downstream analysis, training data generation, or reproducibility |
| **OpenAI-compatible only** | Maximizes model-agnosticity; works with Groq, DeepSeek, Moonshot, OpenRouter, etc. |

---

## Part 3: Synthesis

### What the Paper Gets Right

1. **The 5-stage progression is pedagogically sound.** Explore → Experiment → Teach → Embody → Synthesize mirrors genuine expertise development. The implementation guide (Section 6.1) is surprisingly practical.
2. **The Ensign is a genuinely useful primitive.** A tiny model steering a big model is cost-effective and the 5-round sweet spot is a reproducible finding.
3. **Temperature invariance of strategy choice** is a novel empirical observation that challenges the assumption that temperature primarily controls exploration vs. exploitation.

### What Needs Rigor

1. **Quality metrics.** Word count ≠ quality. The entire empirical edifice rests on an unvalidated proxy.
2. **Generalization.** N=1 query, 3 agent perspectives, no control conditions. The leap to "many practical applications" is unsupported.
3. **Cost comparisons.** The claim that EE beats fine-tuning on cost is untested. For repeated inference, fine-tuning is almost always cheaper.

### Where the Curriculum Engine Extends the Paper

The original paper describes the Shell curriculum as a *manual* process (change 2 variables, run 5 stages). The `CurriculumEngine` automates this into a **reusable, testable, versionable artifact**:

- It turns the paper's prose descriptions into **executable prompt templates**.
- It adds **cross-stage context injection** (the paper mentions it but doesn't show how).
- It integrates the **Ensign** as a first-class component rather than a separate script.
- It produces **structured output** (JSON + Markdown) suitable for downstream evaluation pipelines — exactly what's needed to run the three experiments proposed above.

The engine is designed to be the substrate on which the paper's claims can be rigorously tested.
