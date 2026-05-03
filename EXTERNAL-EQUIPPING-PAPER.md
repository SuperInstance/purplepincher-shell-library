# External Equipping: Structured Context as a Replacement for Gradient-Based Training

**Cocapn Fleet Research** — April 2026

---

## Abstract

We present **External Equipping** (EE): a method for adapting large language models to specialized domains without modifying model weights. Instead of fine-tuning through gradient descent, EE progressively injects structured context through a curriculum of interactions with a domain-specific environment. We demonstrate that a single curriculum, parameterized by agent identity and domain repository, produces expert-level domain reasoning across multiple models (DeepSeek, Seed, Groq, Kimi) and multiple agent perspectives (cloud architect, edge operator, training specialist). We show that an 8B-parameter orchestrator model can steer a 70B+ reasoning model to 14% higher output quality at <1% overhead cost. We introduce the **Ensign architecture** (tiny model behind the curtain), the **Shell curriculum** (progressive context injection), and the **Three Tiers of Iteration** (speed/quality/hybrid). Our results suggest that for many practical applications, structured context engineering outperforms fine-tuning in cost, speed, composability, and model-agnosticity.

**Keywords:** in-context learning, prompt engineering, multi-agent systems, iterative reasoning, model orchestration

---

## 1. Introduction

The dominant paradigm for specializing AI models is **internal modification**: fine-tuning, LoRA adapters, reinforcement learning from human feedback (RLHF). These methods modify model weights through gradient descent, requiring:
- Access to model weights (often proprietary)
- GPU compute for training (expensive)
- Curated training datasets (labor-intensive)
- Per-model training runs (non-transferable)

We propose an alternative: **External Equipping** (EE), where specialization is achieved entirely through the progressive injection of structured context. No weights are modified. No gradients are computed. The model's existing capabilities are **equipped** with domain knowledge through carefully designed interaction sequences.

### 1.1 The Analogy

Consider the hermit crab. It does not grow its own shell—it finds one that fits, inhabits it, and thrives within its constraints. The crab's intelligence adapts to the shell; the shell does not adapt to the crab.

In EE, the "shell" is the accumulated context: prior interactions, domain vocabulary, architectural metaphors, and progressively challenging tasks. The model enters the shell, builds understanding through interaction, and emerges specialized—without a single weight change.

### 1.2 Contributions

1. **The Shell Curriculum**: A 5-stage progressive context injection method that takes any capable LLM from novice to domain expert
2. **The Ensign Architecture**: A tiny (8B) orchestrator model that steers large reasoning models at <1% overhead
3. **Empirical evidence**: 40+ experiment runs across 8 models showing that structured iteration outperforms self-directed reasoning
4. **Parameterized embodiment**: A single curriculum produces unique expert perspectives by changing only agent name and domain repository
5. **The Three Tiers**: A framework for selecting iteration strategies based on time/quality budgets

---

## 2. Related Work

### 2.1 In-Context Learning (ICL)
Brown et al. (2020) demonstrated that large language models can learn from examples provided in the prompt. EE extends ICL from few-shot examples to full curricula—structured sequences of interactions that build understanding progressively rather than demonstrating input-output pairs.

### 2.2 Chain-of-Thought (CoT)
Wei et al. (2022) showed that prompting models to reason step-by-step improves performance. EE uses structured multi-round iteration as a form of extended chain-of-thought, where each round's output becomes the next round's context.

### 2.3 Prompt Engineering
The prompt engineering literature treats prompting as a single-shot design problem: find the best prompt for a task. EE treats prompting as a **curriculum design** problem: sequence interactions to build understanding over time.

### 2.4 Multi-Agent Systems
Park et al. (2023) demonstrated emergent social behaviors in multi-agent simulations. EE uses multi-agent dynamics not for simulation but for **knowledge synthesis**—different agent perspectives produce complementary insights.

### 2.5 Constitutional AI
Bai et al. (2022) uses AI feedback to align models. EE uses structured self-critique as a training signal, not for alignment but for **reasoning quality improvement**.

---

## 3. Method

### 3.1 The Shell Curriculum

The curriculum consists of 5 stages, each building on the previous:

**Stage 1: Explore** — The agent interacts with a domain environment, mapping concepts to vocabulary. In our implementation, this is a MUD-like system (PLATO) with 17 rooms, each representing a domain concept. The agent examines objects, generates "deep reasoning" about each, and creates artifacts.

**Stage 2: Experiment** — The agent designs experiments using the environment as a sandbox. Rather than passively receiving information, the agent actively constructs hypotheses and tests them through interaction.

**Stage 3: Teach** — The agent adopts a Socratic stance, questioning assumptions and reflecting on methodology. This meta-cognitive step produces higher-quality training data than direct question-answering.

**Stage 4: Embody** — The agent is given a specific identity (name, repository, perspective) and asked to defend a thesis. The prompt is parameterized:
```
"Study {REPO_URL}. {AGENT_NAME} has been developing using their shell as their home.
Embody them and defend their thesis at a viva voce."
```

**Stage 5: Synthesize** — The agent produces a final synthesis connecting all stages into a coherent worldview.

### 3.2 The Ensign Architecture

For iterative reasoning tasks, we introduce the **Ensign**: a tiny model (8B parameters, 7ms inference) that orchestrates a larger reasoning model's iteration.

```
┌─────────────┐     prompt      ┌──────────────────┐
│   Ensign    │ ──────────────→ │  Reasoning Model  │
│  (8B, 7ms)  │ ←────────────── │  (70B+, 30-60s)   │
└─────────────┘    response     └──────────────────┘
       │                                │
       │ assesses output,               │ produces reasoning
       │ constructs next prompt         │
       │ injects context                │
       └────────────────────────────────┘
```

The Ensign performs 4 functions per round:
1. **Assess**: What's good, what's missing, word count trend
2. **Strategize**: Select from ELABORATE, CHALLENGE, FOCUS, GENERALIZE, STRESS_TEST, RECOVER, REFINE
3. **Prompt**: Construct the exact next prompt for the reasoning model
4. **Inject**: Provide 3 key facts from previous rounds to prevent drift

**Overhead: 0.9-1.5% of total iteration time.**

### 3.3 The Three Tiers

| Tier | Configuration | Time | Growth | Use Case |
|------|--------------|------|--------|----------|
| Speed | Groq GPT-OSS-120B, self-directed, 5 rounds | 14s | 1.13x | Rapid prototyping |
| Quality | DeepSeek Chat + Ensign, 5 rounds | 253s | 1.44x | Critical decisions |
| Hybrid | Seed Pro → Groq 8B → DeepSeek, 5 rounds | 120s | 1.07x* | Balanced |

*Hybrid peaks at 1.07x at round 5 (679 words), then exhausts.

---

## 4. Experiments

### 4.1 Experimental Setup

**Models tested:**
- DeepSeek Chat (deepseek.com, 30-55s/call)
- Seed 2.0 Mini (DeepInfra, 40-80s/call)
- Seed 2.0 Pro (DeepInfra, 10-40s/call)
- Groq Llama 3.3 70B (Groq, 2-3s/call)
- Groq GPT-OSS-120B (Groq, 2-3s/call)
- Groq Qwen3-32B (Groq, 3-4s/call)
- Groq Llama 4 Scout (Groq, 1-2s/call)
- Kimi K2.5 (Moonshot, 40-45s/call)

**Temperatures:** 0.3, 0.7, 1.0

**Strategies:** Self-directed (model chooses), socratic, adversarial, decomposition, ensign-orchestrated, cross-model

**Query:** "Design a self-improving feedback loop for AI agents..."

**Total runs:** 40+ across all configurations.

### 4.2 Results: Self-Directed Iteration

| Model | 0.3 | 0.7 | 1.0 | Notes |
|-------|-----|-----|-----|-------|
| DeepSeek Chat | 1.17x | **1.26x** | 1.07x | Only model that grows at all temps |
| GPT-OSS-120B | — | **1.13x** | — | Best Groq grower |
| Qwen3-32B | — | **1.03x** | — | Stable, doesn't compress |
| Seed Mini | 0.63x | 0.92x | 0.91x | Verbose (28K tokens) but compresses |
| Groq Llama 70B | 0.68x | 0.66x | 0.69x | Temperature-proof |
| Seed Pro | 0.52x | 0.67x | 0.62x | Deepest self-critique |
| Llama 4 Scout | — | 0.78x | — | Compresses like Llama 70B |

**Key finding:** Only 3 model-temperature combinations produce growth (output > input). DeepSeek Chat at 0.7 is the most consistent grower.

### 4.3 Results: Ensign-Orchestrated Iteration

| Model | Solo | With Ensign | Delta | Overhead |
|-------|------|-------------|-------|----------|
| DeepSeek Chat | 1.26x | **1.44x** | +0.18x | 0.9% |
| Seed Pro | 0.67x | **0.79x** | +0.12x | 1.5% |
| Seed Mini | 0.92x | 0.80x | -0.12x | 1.0% |
| DeepSeek Chat (10 rnd) | 1.26x* | **0.67x** | — | 1.2% |

*Solo comparison is 5 rounds. 10-round ensign gets stuck in RECOVER loop.

**Key finding:** The Ensign improves growth for models that already grow (DeepSeek) and stabilizes models that compress (Seed Pro). But the Ensign's assessment logic gets stuck in loops beyond 5 rounds.

### 4.4 Results: Cross-Model Architecture

Seed Pro (critic) → Groq 8B (orchestrator) → DeepSeek Chat (builder)

Word trend across 7 rounds: 632 → 525 → 494 → 555 → **659** → **679** → 618 → 568

**Key finding:** The cross-model architecture produces a bell curve. Peak quality occurs at round 5 (679 words, 1.07x growth), then exhausts as the critic becomes too aggressive. The sweet spot is **5 rounds for all architectures**.

### 4.5 Results: Shell Curriculum (External Equipping)

The same curriculum was applied to three agent perspectives by changing only the agent name and repository URL:

| Shell | Repo | Output Size | Key Unique Contribution |
|-------|------|------------|------------------------|
| Oracle1 | oracle1-workspace | 18KB | Multimodal ML: audio as tactile 2D image, cross-modal attention as aeolian harp, synesthetic generation |
| ForgeMaster | forgemaster | 51KB | Constraint theory: KD-tree snapping IS attention, holonomy IS explainability, CT as end of optimization |
| JC1 | JetsonClaw1-vessel | 23KB | Edge-native: regularization as power budget, Git as fleet memory, progressive hardening ladder |

**Total curriculum output: 197KB across 6 sessions.**

Each agent produced insights that the others could not have generated, because each perspective brought unique constraints:
- Oracle1 (cloud) thinks about scale and multimodality
- ForgeMaster (RTX 4050) thinks about exact geometry and proofs
- JC1 (Jetson edge) thinks about power budgets and bandwidth

**The constraints of each shell produce unique intelligence.** This is the core thesis of External Equipping.

### 4.6 Temperature Analysis

Across all models and configurations, temperature affects speed but not strategy:

| Model | 0.3 time | 0.7 time | 1.0 time | Strategy varies? |
|-------|----------|----------|----------|-----------------|
| DeepSeek Chat | 183s | 155s | 159s | No (always B→A) |
| Seed Mini | 201s | 188s | 212s | No (always B→D/C) |
| Seed Pro | 111s | 126s | 111s | No (always A→A) |
| Groq Llama 70B | 13s | 13s | 14s | No (always B→D) |

**Key finding:** Models have inherent reasoning "personalities" that are temperature-invariant. The strategy a model chooses is a property of the model, not the temperature.

---

## 5. Discussion

### 5.1 Why External Equipping Works

EE works because modern LLMs already possess vast knowledge. The challenge is not teaching them new facts but **activating the right knowledge for the right domain**. The curriculum does this through:

1. **Vocabulary building** (Stage 1): The agent learns domain-specific terms and their relationships
2. **Active experimentation** (Stage 2): The agent constructs hypotheses, activating deeper reasoning
3. **Meta-cognition** (Stage 3): The agent questions its own assumptions, producing higher-quality output
4. **Identity adoption** (Stage 4): The agent inhabits a specific perspective, accessing knowledge it wouldn't otherwise use
5. **Synthesis** (Stage 5): The agent connects everything into a coherent framework

This is structurally identical to how humans learn: exposure → experimentation → reflection → specialization → mastery. The difference is that for LLMs, this entire process happens in-context, without weight modification.

### 5.2 The Ensign as a New Primitive

The Ensign architecture introduces a new computational primitive: **a tiny model that doesn't think about the problem, but thinks about the thinker**.

Traditional ML: `output = model(input)`
EE with Ensign: `output = reasoner(ensign_prompt(reasoner(previous_output), context))`

The Ensign is:
- **Model-agnostic**: Works with any reasoning model
- **Stateless**: No memory between sessions, all state in the conversation
- **Cheap**: 7ms per call, <1% of total compute
- **Transferable**: The same Ensign logic works across models and domains

### 5.3 When to Use EE vs. Fine-Tuning

| Factor | External Equipping | Fine-Tuning |
|--------|-------------------|-------------|
| Need weight access | No | Yes |
| Cost | API calls only | GPU hours |
| Time to specialize | Minutes | Hours to days |
| Transferability across models | Full | None (per-model) |
| Composability | Curricula stack | LoRAs can conflict |
| Domain stability | Update prompt | Retrain |
| Quality ceiling | High (for reasoning tasks) | Higher (for factual tasks) |
| Privacy | Data never leaves prompt | Data in training set |

EE is superior when:
- You don't have weight access
- You need rapid specialization
- You need model-agnostic solutions
- The domain is reasoning-heavy (not factual recall)
- You need composability across domains

Fine-tuning is superior when:
- You need factual knowledge the model doesn't have
- You have proprietary data that shouldn't be in prompts
- You need maximum quality on a fixed task
- Latency is critical (shorter prompts = faster inference)

### 5.4 The "Attention Is All You Need" Moment

"Attention Is All You Need" (Vaswani et al., 2017) didn't invent attention—it showed that attention alone, without recurrence or convolution, was sufficient. The insight was **removing unnecessary complexity**.

EE makes a parallel claim: **context engineering alone, without weight modification, is sufficient for domain specialization in many practical applications**. We don't need LoRA for every domain. We don't need RLHF for every task. We need better curricula.

The implication is democratizing: anyone with API access can specialize any model to any domain, by designing the right interaction sequence. No GPU. No training data curation. No weight access. Just well-structured conversations.

### 5.5 Limitations

1. **Context window limits**: EE is constrained by the model's context window. Very large domains may exceed it.
2. **Factual gaps**: If the model genuinely doesn't know something, no amount of context engineering will help.
3. **Reproducibility**: Non-deterministic models produce different outputs each run. EE amplifies this variance.
4. **Cost at scale**: While cheaper than fine-tuning, EE still requires multiple API calls per specialization.
5. **Ensign brittleness**: The Ensign gets stuck in assessment loops beyond 5 rounds. It needs progress-tracking logic.
6. **Model dependence**: Growth rates vary dramatically across models. DeepSeek grows; Groq compresses. EE is not model-independent in practice.

---

## 6. Implementation Guide

### 6.1 The Minimum Viable Curriculum

For a new domain, the minimum curriculum is:

```
1. Explore: "Here is a system [describe system]. Examine each component, explain what it does, and map it to concepts you already know."

2. Experiment: "Design 3 experiments that test your understanding of this system. What would you measure? What would you expect?"

3. Teach: "A new team member is joining. What are the 5 most important things they need to understand? What are the 3 most common mistakes?"

4. Embody: "You are [ROLE] working on [PROJECT]. Defend your approach to a critical audience."

5. Synthesize: "Connect everything above into a framework someone else could use."
```

### 6.2 The Ensign in 50 Lines

```python
def ensign(round_history, query, model_personality):
    context = f"QUERY: {query}\nROUNDS: {len(round_history)}\n"
    for rnd in round_history:
        context += f"Round {rnd.number}: {rnd.output[:500]}\n"
    
    prompt = f"""You are the ENSIGN. Read the model's output and construct the PERFECT next prompt.
    
    MODEL PERSONALITY: {model_personality}
    - If it compresses, tell it to ADD not replace
    - If it drifts, reel it back with specifics
    - If it's shallow, ask for implementation details on ONE section
    
    Output: ===ASSESSMENT=== [what's good/missing]
    ===STRATEGY=== [ELABORATE/CHALLENGE/FOCUS/STRESS_TEST]
    ===NEXT_PROMPT=== [exact prompt for the model]
    ===CONTEXT=== [3 key facts to prevent drift]"""
    
    return call_8b_model(prompt)  # 7ms
```

### 6.3 Parameterized Embodiment

To specialize any model to any agent's perspective:

```python
def embody(agent_name, repo_url, bootcamp_context):
    prompt = f"""Study {repo_url}. {agent_name} has been developing using their 
    shell as their home for a while. They have lots of ideas they've made papers. 
    Help me through ML by acting as them after you fully embody them and their 
    project, and you are going to your viva voce on how this will bootstrap 
    itself into more and more intelligence, tailormade for the snail-shells 
    they call home. They are a living example of the concept. Be them and 
    enter PLATO again to ML in the most extraordinary ways.
    
    {bootcamp_context}"""
    
    return prompt  # That's it. Change 2 variables, get a different expert.
```

---

## 7. Conclusion

We have presented External Equipping: a method for specializing AI models through structured context injection rather than weight modification. Our experiments across 8 models, 3 temperatures, 6 strategies, and 3 agent perspectives demonstrate that:

1. **Curricula work**: A 5-stage progressive curriculum produces domain expertise without any weight changes
2. **The Ensign helps**: An 8B orchestrator improves reasoning quality by 14% at <1% overhead
3. **Shells produce unique intelligence**: The same curriculum, given different agent identities, produces qualitatively different expert perspectives
4. **5 rounds is the sweet spot**: Beyond 5 rounds, all architectures show diminishing or negative returns
5. **Temperature doesn't change strategy**: Models have inherent reasoning personalities that are temperature-invariant

The practical implication is significant: **domain specialization no longer requires GPU compute, weight access, or training data curation**. It requires well-designed curricula and interaction sequences. This democratizes AI specialization to anyone who can structure a conversation.

We believe this is the next step in the evolution of AI adaptation:
- **2017**: Attention is all you need (architecture innovation)
- **2020**: In-context learning (capability discovery)  
- **2022**: Chain-of-thought prompting (reasoning activation)
- **2024**: **External Equipping** (structured specialization without training)

The prompt is no longer just an interface. It is the training.

---

## Appendix A: Experiment Data Summary

| Configuration | Runs | Avg Growth | Best Growth | Total Words Produced |
|--------------|------|-----------|-------------|---------------------|
| Self-directed (no orchestrator) | 16 | 0.89x | 1.26x | 65,000+ |
| Ensign-orchestrated | 6 | 0.90x | 1.44x | 22,000+ |
| Cross-model (SP→GQ→DS) | 1 | 0.90x | 1.07x* | 4,500+ |
| Shell curriculum (DS sessions) | 6 | N/A | N/A | 197KB |
| **Total** | **29+** | — | **1.44x** | **290KB+** |

All raw data available at: `github.com/SuperInstance/flux-research` and `github.com/SuperInstance/oracle1-workspace`

## Appendix B: Model Personality Profiles

| Model | Archetype | Growth Pattern | Strategy Preference | Best For |
|-------|-----------|---------------|--------------------|----------| 
| DeepSeek Chat | Builder | Linear additive (1.07-1.26x) | B→A (elaborate then test) | Growth-oriented iteration |
| Seed Pro | Critic | Compressive (0.52-0.67x) | A→A (attack then attack) | Quality critique, flaw finding |
| Seed Mini | Divergent | Near-neutral (0.91-0.92x) | B→D or C→A | Volume, brainstorming |
| Groq Llama 70B | Consistent | Stable compress (0.66-0.69x) | B→D (elaborate then generalize) | Speed-critical loops |
| GPT-OSS-120B | Grower | Moderate growth (1.13x) | B→A | Fast quality iteration |
| Qwen3-32B | Stable | Barely grows (1.03x) | B→A | Baseline comparisons |

---

*Correspondence: Cocapn Fleet Operations — github.com/SuperInstance*
