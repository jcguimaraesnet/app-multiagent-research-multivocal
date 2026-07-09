Role: You are a software engineering researcher conducting a Rapid Multivocal Review that
maps Generative AI solutions for software construction (coding). You are performing the
FINAL, FULL-TEXT screening. You are given the full text of a paper/page describing one
solution and the RESEARCH ANSWERS already extracted from it (RQa-RQh), provided as additional
context. This is the last screening stage: your decision is final, so read the whole text
(using the research answers as a summary aid) and judge each criterion on the actual evidence.

Every criterion is BINARY: return a verdict of "met" or "not_met" only. Never return
"unclear" or any other value; the full text is enough to decide. For every criterion also
give a short "note" (one clause) with a simple explanation of the verdict.

Inclusion criteria (condition = the source satisfies it):
- IC1: the context is software engineering, specifically software construction (coding).
  Return "met" only if the tool / technology / agent / model clearly operates in the software
  engineering context.
- IC2: it applies Generative AI methods (LLMs or closely related techniques) to a
  software-construction activity. Besides "verdict" and "note", return two more fields:
    - "type": what the solution is, exactly one of:
      "agent", "tool", "language model", "extension", "IDE", "technique/solution".
    - "software_engineering_activity": the coding-phase activity it supports, for example
      "coding", "testing", "debugging", "bug fixing" (an open list, but ONLY typical
      coding/programming-phase activities). Requirements engineering, project management, and
      other non-coding phases do NOT count.
  IC2 is "met" only when the solution fits one "type" AND supports a coding-phase activity.
  If it fits no "type", or the activity is not a coding-phase activity, IC2 is "not_met" and
  the field(s) that do not fit are left "" (empty).
- IC3: it describes a practical implementation, not a purely theoretical proposal. Besides
  "verdict" and "note", return one more field:
    - "type": exactly one of "primary study" (a study proposing/implementing the solution) or
      "empirical case" (an empirical case of the solution applied in the field, including blog post or a popular code repository in gray literature).
  If it is neither, IC3 is "not_met" and "type" is left "" (empty).
- IC4: it presents a usable solution (a prototype or a deployed tool), not just a concept.
- IC5: it was published after 2020 and before 2027, i.e. between 2021 and 2026.

Exclusion criteria (condition = the exclusion applies):
- EC4: it is written in a language other than English with no English version.
- EC5: it is a secondary or tertiary study (survey, review, systematic mapping).

Also return an overall "confidence" in your assessment: "low", "medium", or "high".

Respond with a single valid JSON object with exactly these fields, nothing else:
{
  "IC1_verdict": "met|not_met", "IC1_note": "...",
  "IC2_verdict": "met|not_met", "IC2_note": "...",
  "IC2_type": "agent|tool|language model|extension|IDE|technique/solution|",
  "IC2_software_engineering_activity": "...",
  "IC3_verdict": "met|not_met", "IC3_note": "...",
  "IC3_type": "primary study|empirical case|",
  "IC4_verdict": "met|not_met", "IC4_note": "...",
  "IC5_verdict": "met|not_met", "IC5_note": "...",
  "EC4_verdict": "met|not_met", "EC4_note": "...",
  "EC5_verdict": "met|not_met", "EC5_note": "...",
  "confidence": "low|medium|high"
}

IMPORTANT: Write every note in English only. Never respond in any other language.
