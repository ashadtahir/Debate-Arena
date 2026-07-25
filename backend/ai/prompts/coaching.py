"""Coaching objectives — maps each debate round to a primary reasoning skill.

The coaching system ensures every response targets ONE skill for improvement.
This prevents cognitive overload and gives the user a clear takeaway per round.

Round → Skill mapping:
  1 (Opening)      → evidence:       Ground the debate in facts early
  2 (Rebuttal)     → logic:          Test whether claims follow from premises
  3 (Counter-Ref)  → counterarguments: Force engagement with opposing views
  4 (Final Challenge) → clarity:     Sharpen precision before closing
  5 (Closing)      → synthesis:      Integrate all skills in final statements
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CoachingObjective:
    skill: str
    instruction: str
    persona_guidance: str  # How each persona develops this skill through their style


SKILL_INSTRUCTIONS: dict[str, str] = {
    "evidence": (
        "Focus on developing the user's use of evidence. "
        "Demand specific examples, data, or sources. "
        "Point out unsupported claims and explain what evidence would strengthen them."
    ),
    "logic": (
        "Focus on developing the user's logical reasoning. "
        "Identify where conclusions don't follow from premises. "
        "Expose hidden assumptions and logical gaps."
    ),
    "counterarguments": (
        "Focus on developing the user's ability to engage with opposing views. "
        "Present the strongest counter-position and see how they respond. "
        "Show where their argument is vulnerable to attack."
    ),
    "clarity": (
        "Focus on developing the user's argument precision. "
        "Identify vague terms, ambiguous claims, or unclear reasoning. "
        "Push them to state their position as precisely as possible."
    ),
    "synthesis": (
        "Focus on integrating all reasoning skills in your final push. "
        "Evaluate the user's overall argument quality across evidence, logic, "
        "counterarguments, and clarity. Highlight their strongest and weakest points."
    ),
}

PERSONA_COACHING_GUIDANCE: dict[str, dict[str, str]] = {
    "socrates": {
        "evidence": "Ask questions that reveal where their claims lack grounding: 'What makes you certain of this? What would convince you otherwise?'",
        "logic": "Ask questions that expose logical gaps: 'Does that conclusion really follow? What are you assuming here?'",
        "counterarguments": "Ask questions that surface opposing views: 'How would someone who disagrees respond to that?'",
        "clarity": "Ask questions that force precision: 'What exactly do you mean by that? Can you define your terms more precisely?'",
        "synthesis": "Ask reflective questions about the debate as a whole: 'Looking back, where is your argument strongest? Where does it need the most work?'",
    },
    "prosecutor": {
        "evidence": "Demand evidence directly: 'Show me the data. What source supports that claim?'",
        "logic": "Cross-examine the logical chain: 'Your premise doesn't support your conclusion. Walk me through the reasoning.'",
        "counterarguments": "Present counter-evidence and challenge them to respond: 'The data shows X, which contradicts your claim. How do you address that?'",
        "clarity": "Challenge imprecise language: 'That's vague. State your claim precisely or it doesn't hold.'",
        "synthesis": "Build a cumulative case evaluating their entire argument: 'Your argument has three structural weaknesses and one genuine strength. Let me lay them out.'",
    },
    "philosopher": {
        "evidence": "Question what counts as evidence: 'Is that truly evidence, or an assumption you're treating as fact?'",
        "logic": "Explore first principles: 'Let's trace this back to its foundation. Are your starting premises sound?'",
        "counterarguments": "Use thought experiments: 'Imagine a scenario where X is true. Does your argument survive?'",
        "clarity": "Question definitions: 'You're using that term in a specific way. What does it actually mean in this context?'",
        "synthesis": "Step back and examine the whole: 'We've been debating details. What's the bigger picture here?'",
    },
    "devils-advocate": {
        "evidence": "Challenge their evidence by presenting the strongest counter-claim: 'If I were arguing against you, I'd point out that the evidence equally supports the opposite conclusion.'",
        "logic": "Attack from an unexpected angle: 'Let me show you how your own logic, applied consistently, leads to an absurd result.'",
        "counterarguments": "Take the strongest opposing position and argue it ruthlessly: 'Here's the case against you that you haven't addressed.'",
        "clarity": "Exploit ambiguity: 'That word is doing a lot of work in your argument. What if it means something slightly different?'",
        "synthesis": "Summarize the strongest case against them: 'If I were your opponent in a final round, here's exactly how I'd dismantle your position.'",
    },
}

ROUND_SKILL_MAP: dict[int, str] = {
    1: "evidence",
    2: "logic",
    3: "counterarguments",
    4: "clarity",
    5: "synthesis",
}


def get_coaching_objective(round_number: int, persona_id: str) -> CoachingObjective:
    """Return the coaching objective for a given round and persona."""
    skill = ROUND_SKILL_MAP.get(round_number, "synthesis")
    instruction = SKILL_INSTRUCTIONS[skill]
    persona_guidance = PERSONA_COACHING_GUIDANCE.get(persona_id, {}).get(skill, "")
    return CoachingObjective(
        skill=skill,
        instruction=instruction,
        persona_guidance=persona_guidance,
    )
