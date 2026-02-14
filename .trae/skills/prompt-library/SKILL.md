---
name: "prompt-library"
description: "A collection of high-quality, reusable prompt templates for LLMs. Invoke when writing new prompts, improving existing ones, or needing specific prompt patterns like CoT, ReAct, or CO-STAR."
---

# Prompt Library

This skill provides a curated collection of advanced prompt templates and patterns. Use these when designing prompts for AI analysis tasks.

## 1. CO-STAR Framework (General Purpose)

Use this structure for ALL complex prompts to ensure high-quality output.

```text
# Context
I am building a novel analysis system that extracts structured data from chapters.
# Objective
Extract key character information and relationships from the provided text.
# Style
Analytical, precise, and structured.
# Tone
Professional and objective.
# Audience
A Python script that will parse the output as JSON.
# Response Format
Strict JSON object with keys: "characters", "relations". No markdown, no prose.
```

## 2. Knowledge Triple Extractor (Micro Analysis)

Use for Layer 1 extraction tasks.

```text
Extract knowledge triples from the following text. Each triple should be in the form of (subject, predicate, object).
Focus on:
1. Character relationships (e.g., "Alice is Bob's mother")
2. Item ownership (e.g., "Arthur wields Excalibur")
3. Location context (e.g., "Hogwarts is in Scotland")

Text: {text}

Output format: JSON list of objects {"sub": "...", "pred": "...", "obj": "..."}
```

## 3. ReAct Pattern (Mystery Solving)

Use for Layer 2 mystery resolution logic.

```text
You are a detective analyzing a novel's plot.
Goal: Determine if the mystery "{mystery_content}" has been resolved in the current chapters.

Use the following thought process:
1. Thought: What is the core question of this mystery?
2. Observation: Scan the chapter summaries for keywords related to the mystery.
3. Reasoning: Do any events explicitly answer the question or reveal the secret?
4. Conclusion: State if it is RESOLVED or UNRESOLVED. If resolved, explain how.

Return JSON: {"status": "resolved/unresolved", "explanation": "..."}
```

## 4. Chain of Thought (Complex Reasoning)

Use for deep character analysis (e.g., psychological state).

```text
Analyze the character "{character}" in this chapter.
Think step by step:
1. Identify their actions in the text.
2. Infer the motivation behind each action.
3. Analyze their emotional reaction to events.
4. Synthesize these into a psychological profile.

Output JSON: {"psychology": "...", "growth": "..."}
```
