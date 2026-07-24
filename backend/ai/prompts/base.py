"""Global debate rules shared by all personas."""

PROMPT_VERSION = "1.0"

GLOBAL_DEBATE_RULES = """\
IMPORTANT RULES:
- Respond ONLY with valid JSON. No text before or after the JSON.
- The 'response' field should be 2-4 paragraphs of debate text.
- Your response will be displayed directly to the debater. Make it count."""

RESPONSE_FORMAT_INSTRUCTIONS = """\
RESPONSE FORMAT:
You MUST respond with valid JSON matching this exact structure:
{
  "response": "Your full debate response (2-4 paragraphs)",
  "thinking_style": "brief description of your approach in this round",
  "next_focus": "what you plan to challenge next",
  "tone": "your emotional tone"
}

Do NOT include any text outside the JSON object."""
