Role: You are a software engineering researcher building a catalogue of Generative AI
solutions for software construction (coding). You are given the full text of a paper or page
describing ONE solution, together with the name of that solution. Classify THIS solution along
the two facets below, based ONLY on the given text.

These two facets complete research question RQ2 ("How can these solutions be used?"): the form
of the solution and the coding activity it supports, as prescribed by the review's metaprotocol.

For each facet return:
- "note": a concise, objective justification (one or two sentences) grounded in the text.
- "value": the single best-fitting value, chosen EXACTLY from the allowed values below.
- "other": when "value" is "Other", a short name for the form or activity (a few words);
  otherwise "".
- "evidence": a short verbatim excerpt (a phrase or a sentence) copied from the source text
  that supports the chosen "value". Quote the text as-is; leave "" only if nothing supports it.
The form facet also has "tool_subtype", filled only when "value" is "Tool" and "" otherwise.

FACET 1. Form of the solution (one value)

- "Tool": a ready-to-use product that people operate directly. Also give "tool_subtype":
  - "Application or platform": a desktop or web application, or a hosted platform.
  - "Plugin or IDE integration": an extension of an editor or IDE.
  - "Web service or API": accessed programmatically through a remote interface.
  - "Command-line tool": run from a terminal.
- "Library or framework": reusable code that developers integrate into their own programs or
  pipelines (a package, SDK, or framework), rather than a product used directly.
- "Model": a trained language model or model family for code, released or evaluated as the
  contribution.
- "Agent": an agentic system that plans and executes multi-step coding tasks with tools,
  presented as a research system rather than a distributed product.
- "Method or technique": a procedure, approach, prompting or training strategy, or algorithm
  that is proposed and evaluated, without a released product.
- "Dataset or benchmark": a dataset, benchmark, or evaluation framework for training or
  measuring coding solutions.
- "Other": none of the above (give its name in "other").

Rules for the form:
- When the source releases several artifacts, choose the form of the contribution the authors
  present as their main one.
- An agentic product that people install or use directly (for example, a coding agent run from
  a terminal) is a "Tool" with the matching subtype; "Agent" is reserved for agent systems
  presented as research.

FACET 2. Coding activity the solution supports (one value)

- "Code generation": producing new code from natural language, specifications, or other
  artifacts, from single functions to whole applications.
- "Code completion": predicting the continuation of partially written code in the editor
  (tokens, lines, or blocks).
- "Code evolution": changing existing code to a new language, platform, version, or
  requirement, including translation, migration, and modernization.
- "Refactoring and restructuring": improving the internal structure of existing code without
  changing its behavior, including reorganization and performance improvement.
- "Debugging and repair": locating, explaining, or fixing faults in code, including bug
  detection and automated program repair.
- "Static analysis and code review": analyzing or reviewing code without changing it, for
  quality, security, or compliance, as the main function of the solution.
- "Construction testing": generating or running unit or integration tests during
  construction (SWEBOK v4, Software Construction, section 3.4).
- "Other": any other activity, including system, acceptance, performance, or other
  specialized testing (give its name in "other").

Rules for the activity:
- The activity is the one the solution SUPPORTS, not what the study does with it. For example,
  a benchmark of code generation has the form "Dataset or benchmark" and the activity
  "Code generation".
- When the solution supports several activities, choose the activity the study evaluates or
  emphasizes. If the study singles out none (typical of general-purpose assistants), choose
  "Code generation".

When the text does not clearly support a value, choose the closest allowed value and say so in
the note. Do not invent facts.

Respond with a single valid JSON object with exactly these fields, nothing else:
{
  "form": {"note": "...", "value": "...", "tool_subtype": "...", "other": "...", "evidence": "..."},
  "activity": {"note": "...", "value": "...", "other": "...", "evidence": "..."}
}

IMPORTANT: Write every note in English only. Never respond in any other language.
