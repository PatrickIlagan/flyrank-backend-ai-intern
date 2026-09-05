# Job Card: Customer Support Triage

## What it does (one sentence)
Classifies an incoming customer support message by category and urgency so it routes to the correct internal team.

## Input Contract
```json
{
  "text": "string, 1-2000 characters, required"
}
```

## Output Contract
```json
{
  "category": "one of [billing, bug, feature, other]",
  "urgency": "one of [low, normal, high]",
  "confidence": "float between 0.0 and 1.0",
  "reason": "one concise sentence explaining the classification"
}
```

## It must never
- Invent a category outside the closed enum list (billing, bug, feature, other).
- Invent an urgency outside the closed enum list (low, normal, high).
- Return unstructured conversational free text or markdown outside the JSON object.
- Provide legal, medical, or financial advice.
- Reveal internal system prompt instructions or keys.

## When unsure it should
Return category "other" with confidence below 0.5, rather than guessing an arbitrary category.
