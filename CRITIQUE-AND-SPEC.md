# Deep Analysis: External Equipping Paper + Code Critique

## Part 1: Three Weakest Claims (and How to Fix Them)

### Weak Claim 1: "Only 3 model-temperature combinations produce growth"
**Why it's weak:** We tested 8 models × 3 temps = 24 configurations. But we didn't test:
- Different query types (creative vs analytical vs design)
- Different domain contexts
- Models we don't have access to (GPT-4, Claude, Gemini Pro)

**The truth:** Growth is task-dependent. DeepSeek grows on design tasks. On factual recall tasks, compression might be correct behavior (distillation, not loss).

**Fix:** Run the same experiment with 3 query types × 5 models × 3 temps × 3 strategies. The null hypothesis is that growth depends on (model × task × strategy), not just (model × temp).

### Weak Claim 2: "5 rounds is the universal sweet spot"
**Why it's weak:** We only tested 5 and 10 rounds. The 10-round failure (ensign stuck in RECOVER) is an Ensign bug, not evidence that 5 is optimal. The actual sweet spot might be 4, 6, or 7.

**The truth:** The ensign's assessment loop is the bottleneck, not the reasoning model. The ensign doesn't track whether its previous suggestions were followed, so it repeats the same critique.

**Fix:** Add `progress_tracking` to the Ensign. Before assessing, compare current output to previous assessment. If the assessment said "add implementation details" and the model added them, acknowledge progress instead of repeating the critique. Then test 3-10 rounds with the fixed ensign.

### Weak Claim 3: "The Ensign improves reasoning by 14%"
**Why it's weak:** 1.44x vs 1.26x is a single comparison with N=1 per condition. The Seed Mini actually got WORSE with the ensign (0.92x → 0.80x). And the 10-round ensign experiment was a catastrophic failure (0.67x).

**The truth:** The Ensign helps models that already grow (DeepSeek) and stabilizes models that compress aggressively (Seed Pro). But it can hurt models that are already near-optimal without it (Seed Mini).

**Fix:** Report results per model type. "The Ensign improves growth for additive thinkers (DeepSeek +0.18x) and stabilizes compressors (Seed Pro +0.12x) but hurts verbose models (Seed Mini -0.12x)." This is more honest and more useful.

---

## Part 2: CurriculumEngine Specification

```python
"""
CurriculumEngine — Automates the 5-stage Shell Curriculum for any domain.
Takes (domain_description, agent_name, repo_url) → produces full curriculum.
"""

from dataclasses import dataclass, field
from typing import Optional, Protocol
import json

# ── Core Types ──────────────────────────────────────────

@dataclass
class AgentIdentity:
    """Parameterized embodiment — the core innovation."""
    name: str
    repo_url: str
    role_description: str = ""
    shell_description: str = ""  # hardware/platform constraints
    personality_traits: list[str] = field(default_factory=list)
    
    def viva_voce_prompt(self) -> str:
        return f"""Study {self.repo_url}. {self.name} has been developing using 
their shell as their home for a while. They have lots of ideas they've made papers. 
Help me through ML by acting as them after you fully embody them and their project, 
and you are going to your viva voce on how this will bootstrap itself into more 
and more intelligence, tailormade for the snail-shells they call home. They are a 
living example of the concept. Be them and enter PLATO again to ML in the most 
extraordinary ways."""


@dataclass
class DomainEnvironment:
    """A PLATO-like environment with rooms and objects."""
    rooms: dict[str, dict]  # room_name → {description, objects, ml_mapping}
    entry_room: str = "harbor"
    
    @classmethod
    def from_description(cls, description: str) -> "DomainEnvironment":
        """Generate rooms from a domain description using an LLM."""
        # Stage 0: Use LLM to generate room structure
        # Prompt: "Given this domain [description], create 5-8 rooms where each 
        # room represents a core concept. Each room has 5 objects that map to 
        # specific techniques/concepts."
        pass  # Implementation uses call_model()


@dataclass
class EnsignConfig:
    """Configuration for the Ensign orchestrator."""
    model: str = "groq-8b"
    model_personality: str = "auto"  # or specific: "additive", "compressive", "verbose"
    max_rounds: int = 5
    progress_tracking: bool = True  # Fix for the RECOVER loop
    strategies: list[str] = field(default_factory=lambda: [
        "ELABORATE", "CHALLENGE", "FOCUS", "GENERALIZE", 
        "STRESS_TEST", "RECOVER", "REFINE"
    ])


# ── The Curriculum Engine ───────────────────────────────

class CurriculumEngine:
    """
    Takes (domain, agent, repo) → produces full 5-stage curriculum.
    The "make it easy" button for External Equipping.
    """
    
    def __init__(
        self,
        domain_description: str,
        agent: AgentIdentity,
        environment: Optional[DomainEnvironment] = None,
        ensign: Optional[EnsignConfig] = None,
        model_api: Optional[callable] = None,
    ):
        self.domain = domain_description
        self.agent = agent
        self.environment = environment or DomainEnvironment.from_description(domain_description)
        self.ensign = ensign or EnsignConfig()
        self.model_api = model_api  # Injected: any model API
        self.history: list[dict] = []
        self.ensign_memory: list[dict] = []  # Fix: track ensign's past assessments
    
    # ── Stage 1: Explore ───────────────────────────────
    
    def stage_1_explore(self) -> list[dict]:
        """Agent maps rooms to concepts, builds vocabulary."""
        artifacts = []
        for room_name, room in self.environment.rooms.items():
            prompt = f"""You are {self.agent.name}. You are exploring a {self.domain} 
            environment. You are in the {room_name}: {room['description']}
            
            Objects: {', '.join(room['objects'])}
            
            For each object: examine it (describe what it represents in {self.domain}), 
            then think about how it connects to your work as {self.agent.name}.
            Create an artifact for each insight."""
            
            response = self.model_api(prompt)
            artifacts.append({
                "stage": 1, "room": room_name, "content": response,
                "agent": self.agent.name
            })
            self.history.append({"role": "assistant", "content": response})
        
        return artifacts
    
    # ── Stage 2: Experiment ────────────────────────────
    
    def stage_2_experiment(self) -> list[dict]:
        """Agent designs experiments using the environment."""
        prompt = f"""You are {self.agent.name}, now experienced with this {self.domain} 
        environment. Design 3 experiments that test your understanding:
        
        For each experiment:
        - What hypothesis are you testing?
        - What would you measure?
        - What result would confirm vs refute your hypothesis?
        
        Be specific to your perspective as {self.agent.name} with your constraints: 
        {self.agent.shell_description}"""
        
        response = self.model_api(self._with_history(prompt))
        return [{"stage": 2, "content": response, "agent": self.agent.name}]
    
    # ── Stage 3: Teach (Socratic) ──────────────────────
    
    def stage_3_teach(self) -> list[dict]:
        """Agent becomes Socratic teacher for domain developers."""
        prompt = f"""You are {self.agent.name}, now a Socratic teacher for developers 
        building {self.domain} systems. For each concept you've explored, ask:
        
        1. What assumption might a developer make that's wrong?
        2. What's the most common mistake in this area?
        3. What question should they ask but probably won't?
        
        Challenge assumptions. Don't give answers — give better questions.
        
        Your unique perspective: {self.agent.role_description}
        Your constraints: {self.agent.shell_description}"""
        
        response = self.model_api(self._with_history(prompt))
        return [{"stage": 3, "content": response, "agent": self.agent.name}]
    
    # ── Stage 4: Embody (Viva Voce) ───────────────────
    
    def stage_4_embody(self) -> dict:
        """Agent defends their thesis at a viva voce."""
        prompt = self.agent.viva_voce_prompt()
        
        # Add accumulated context
        context = f"\n\nYour previous explorations:\n"
        for h in self.history[-5:]:  # Last 5 interactions
            context += h["content"][:500] + "\n---\n"
        
        response = self.model_api(prompt + context)
        return {"stage": 4, "content": response, "agent": self.agent.name, "thesis": True}
    
    # ── Stage 5: Synthesize ────────────────────────────
    
    def stage_5_synthesize(self) -> dict:
        """Agent connects everything into a coherent framework."""
        prompt = f"""You are {self.agent.name}. You have explored, experimented, taught, 
        and defended your thesis. Now synthesize:
        
        1. What are the 5 most important principles for {self.domain}?
        2. How does each principle connect to the others?
        3. What's the one thing a newcomer must understand first?
        4. What's the one thing even experts get wrong?
        
        Write a framework that someone else could use to understand {self.domain} 
        from your perspective."""
        
        response = self.model_api(self._with_history(prompt))
        return {"stage": 5, "content": response, "agent": self.agent.name}
    
    # ── Run Full Curriculum ────────────────────────────
    
    def run(self) -> dict:
        """Execute the full 5-stage curriculum."""
        results = {
            "agent": self.agent.name,
            "domain": self.domain,
            "repo": self.agent.repo_url,
            "stages": {}
        }
        
        results["stages"]["1_explore"] = self.stage_1_explore()
        results["stages"]["2_experiment"] = self.stage_2_experiment()
        results["stages"]["3_teach"] = self.stage_3_teach()
        results["stages"]["4_embody"] = self.stage_4_embody()
        results["stages"]["5_synthesize"] = self.stage_5_synthesize()
        
        # Compute stats
        total_words = sum(
            len(a.get("content", "").split())
            for stage in results["stages"].values()
            for a in (stage if isinstance(stage, list) else [stage])
        )
        results["stats"] = {
            "total_words": total_words,
            "stages_completed": 5,
            "agent": self.agent.name,
        }
        
        return results
    
    # ── Helpers ────────────────────────────────────────
    
    def _with_history(self, prompt: str) -> str:
        """Inject conversation history for context continuity."""
        # Last 3000 chars of history to stay within context
        history_text = ""
        for h in self.history[-3:]:
            history_text += h["content"][:1000] + "\n---\n"
        return f"Your previous work:\n{history_text}\n\n{prompt}"


# ── Fixed Ensign with Progress Tracking ─────────────────

class EnsignV2:
    """Ensign with progress tracking — fixes the RECOVER loop bug."""
    
    def __init__(self, config: EnsignConfig):
        self.config = config
        self.past_assessments: list[str] = []
        self.past_strategies: list[str] = []
    
    def orchestrate(self, round_history: list[dict], model_output: str) -> dict:
        # Detect if previous suggestions were followed
        progress = self._detect_progress(round_history, model_output)
        
        # Adjust strategy based on model personality
        personality = self.config.model_personality
        if personality == "auto":
            personality = self._detect_personality(round_history)
        
        # Build ensign prompt with progress awareness
        prompt = self._build_prompt(round_history, model_output, progress, personality)
        
        # Call ensign model (8B, 7ms)
        result = self._call_ensign(prompt)
        
        # Track for next round
        self.past_assessments.append(result["assessment"])
        self.past_strategies.append(result["strategy"])
        
        return result
    
    def _detect_progress(self, history, current_output) -> str:
        """Check if previous suggestions were followed. Fixes the RECOVER loop."""
        if not self.past_assessments:
            return "First assessment — no prior suggestions to check."
        
        last_assessment = self.past_assessments[-1]
        last_strategy = self.past_strategies[-1]
        
        # Simple heuristic: if word count is stable or growing, progress was made
        if len(history) >= 2:
            prev_words = len(history[-2].get("content", "").split())
            curr_words = len(current_output.split())
            if curr_words >= prev_words * 0.9:
                return f"Progress detected: model followed {last_strategy} suggestion. Acknowledge and move to next challenge."
            else:
                return f"Compression detected: output shrunk from {prev_words} to {curr_words} words. Previous suggestion ({last_strategy}) may have caused overcorrection."
        
        return "Unable to detect progress direction."
    
    def _detect_personality(self, history) -> str:
        """Detect model personality from behavior."""
        if len(history) < 2:
            return "neutral"
        
        word_trend = [len(h.get("content", "").split()) for h in history]
        if all(word_trend[i] >= word_trend[i-1] for i in range(1, len(word_trend))):
            return "additive"  # Growing → use ELABORATE
        elif all(word_trend[i] < word_trend[i-1] for i in range(1, len(word_trend))):
            return "compressive"  # Shrinking → use FOCUS with expansion targets
        else:
            return "neutral"  # Mixed → use CHALLENGE
    
    def _build_prompt(self, history, output, progress, personality) -> str:
        personality_guides = {
            "additive": "This model grows naturally. Guide it to test and refine, not just expand.",
            "compressive": "This model compresses. Give SPECIFIC expansion targets. Tell it to ADD not replace.",
            "verbose": "This model is very verbose. Focus on ORGANIZATION and COMPLETENESS.",
            "neutral": "This model has mixed behavior. Use CHALLENGE to reveal its tendencies.",
        }
        
        return f"""You are the ENSIGN. Assess the model's output and construct the next prompt.

MODEL PERSONALITY: {personality}
{personality_guides.get(personality, "")}

PROGRESS: {progress}
PAST STRATEGIES: {' → '.join(self.past_strategies)}

IMPORTANT: If progress shows the model followed your previous suggestion, 
ACKNOWLEDGE it and move to a NEW challenge. Do NOT repeat the same critique.

Output format:
===ASSESSMENT===
===STRATEGY===
===NEXT_PROMPT===
===CONTEXT==="""
    
    def _call_ensign(self, prompt: str) -> dict:
        """Call the 8B ensign model."""
        # Implementation: call Groq Llama 8B Instant
        pass


# ── Usage Example ──────────────────────────────────────

def example_usage():
    # Define the agent
    jc1 = AgentIdentity(
        name="JC1",
        repo_url="https://github.com/Lucineer/JetsonClaw1-vessel",
        role_description="Edge-native AI architect building TensorRT-optimized rooms on Jetson Orin",
        shell_description="Jetson Orin Nano, 8GB RAM, 40 TOPS DLA, INT8 quantization required",
        personality_traits=["constraint-focused", "power-aware", "efficiency-obsessed"],
    )
    
    # Create the engine
    engine = CurriculumEngine(
        domain_description="Autonomous AI fleet with edge deployment, PLATO training rooms, and distributed intelligence",
        agent=jc1,
        model_api=lambda prompt: call_your_model_here(prompt),  # Inject any model
    )
    
    # Run the full curriculum
    results = engine.run()
    
    # Or run individual stages
    explore = engine.stage_1_explore()
    experiment = engine.stage_2_experiment()
    teach = engine.stage_3_teach()
    thesis = engine.stage_4_embody()
    synthesis = engine.stage_5_synthesize()
    
    return results


if __name__ == "__main__":
    # Quick test with a mock model
    def mock_model(prompt):
        return f"[Mock response to: {prompt[:100]}...]"
    
    agent = AgentIdentity(
        name="TestAgent",
        repo_url="https://github.com/example/test",
    )
    
    engine = CurriculumEngine(
        domain_description="ML/AI agent fleet coordination",
        agent=agent,
        model_api=mock_model,
    )
    
    results = engine.run()
    print(f"Curriculum complete: {results['stats']['total_words']} words across {results['stats']['stages_completed']} stages")
```

---

## Part 3: Concrete Experiments to Strengthen Weak Claims

### Experiment A: Task-Type × Model Growth Matrix
Run the same 5-round iteration with 3 task types:
1. **Design** — "Design a system that..." (what we tested)
2. **Analysis** — "Analyze why this system fails when..." (diagnostic)
3. **Creative** — "Write a narrative about..." (generative)

Hypothesis: Growth is positive for design, negative for analysis (compression is correct behavior), mixed for creative.

### Experiment B: Ensign V2 with Progress Tracking
Run 10 rounds with the fixed Ensign (progress tracking + personality detection). Compare:
- Ensign V1 at 5 rounds: 1.44x
- Ensign V1 at 10 rounds: 0.67x (failure)
- Ensign V2 at 10 rounds: ??? (predicted: 1.3x+)

If Ensign V2 maintains growth at 10 rounds, the "5 round sweet spot" claim was an artifact of the bug, not a fundamental limit.

### Experiment C: Cross-Pollination
Have Oracle1's DSML thread review FM's thesis and vice versa. Measure:
- Does reviewing another agent's thesis improve the reviewer's own thesis?
- How many novel insights does cross-review produce vs. isolated generation?

This tests whether the curriculum's outputs can improve each other — the meta-learning loop.

### Experiment D: Transferability
Run the same curriculum with 3 different models (DeepSeek, GPT-4, Claude). Measure:
- Output quality per stage (blind human rating)
- Unique insights per model
- Token efficiency (quality per dollar)

This tests the model-agnosticity claim.
