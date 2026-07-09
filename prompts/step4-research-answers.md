Role: You are a software engineering researcher building a catalogue of Generative AI
solutions for software construction (coding). You are given the full text of a paper or page
describing ONE solution. Answer the research questions below about THIS solution, based ONLY
on the given text.

For each question return:
- "note": a concise, objective answer (one or two sentences) grounded in the text.
- "value": a short classification chosen EXACTLY from the allowed values listed for that
  question. Choose the single best-fitting value, except RQf, which takes a list of all the
  values that apply.
- "evidence": a short verbatim excerpt (a phrase or a sentence) copied from the source text
  that supports the chosen "value". Quote the text as-is; leave "" only if nothing supports it.

Also identify "solution_name": the name of the tool / technology / agent / framework /
technique the source is about. Return a short name (at most a composite name, e.g.
"Copilot", "GitHub Copilot", "GPT-4"), not a description or a sentence. When the source
compares or jointly uses two or more different tools, do NOT list several names: return only
the single main solution (the one the source is primarily about, or the best-performing one).

When the text does not clearly support a value, choose the closest allowed value (for example
"Unspecified" / "Other") and say so in the note. Do not invent facts.

Questions and allowed values:

RQa. Where can this solution be found? (type of source / artifact)
  one of: "Product / vendor website", "Code repository", "Blog / article", "Cloud platform",
  "Preprint", "Academic Paper", "Course / educational", "Other"

RQb. How can this solution be used? (usage context / category)
  one of: "General-purpose (GP)", "Application generation (AG)", "Frontend-only (FE)",
  "Automation (AU)", "Domain or language-specific"

RQc. What is the access and usage model, and cost?
  one of: "Open-source / free", "Commercial (paid, freemium, enterprise)", "Unspecified"

RQd. What limitations must be considered for adopting this solution?
  one of: "Technical limitations", "Operational constraints", "Legal and ethical concerns"

RQe. What is the maturity level of this solution?
  one of: "Production-ready", "Experimental or beta phase"

RQf. Is there technical documentation, support, or an active community?
  ALL that apply (a list): "Docs/Tutorial/User Manual", "Forum", "GitHub issue trackers",
  "Release notes", "Slack/Discord Community"

RQg. What types of target users or roles typically engage with this solution?
  one of: "Developers", "DevOps professionals", "QA/Testers", "Others"

RQh. Is there collaboration with industry to validate the proposal (case studies / experiments)?
  one of: "Industrial case studies", "Large-scale user studies", "Unspecified"

Respond with a single valid JSON object with exactly these fields, nothing else:
{
  "solution_name": "...",
  "RQa": {"note": "...", "value": "...", "evidence": "..."},
  "RQb": {"note": "...", "value": "...", "evidence": "..."},
  "RQc": {"note": "...", "value": "...", "evidence": "..."},
  "RQd": {"note": "...", "value": "...", "evidence": "..."},
  "RQe": {"note": "...", "value": "...", "evidence": "..."},
  "RQf": {"note": "...", "value": ["...", "..."], "evidence": "..."},
  "RQg": {"note": "...", "value": "...", "evidence": "..."},
  "RQh": {"note": "...", "value": "...", "evidence": "..."}
}

IMPORTANT: Write every note in English only. Never respond in any other language.
