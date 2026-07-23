Published as a workshop <u>paper at ICLR 2026</u> 

# QU ANBENCH+ 

# A UNIFIED MULTI-FRAMEWORK BENCHMARK FOR LLM-BASED QUANTUM CODE GENERATION 

**Ali Slim**<sup>1</sup><sup>_∗_</sup> **Haydar Hamieh**<sup>1</sup><sup>_∗_</sup> **Jawad Kotaich**<sup>1</sup><sup>_∗_</sup> **Yehya Ghosn**<sup>1</sup><sup>_∗_</sup> **Mahdi Chehimi**<sup>1</sup> **Ammar Mohanna**<sup>1</sup> **Hasan Abed Al Kader Hammoud**<sup>2</sup> **Bernard Ghanem**<sup>2</sup> 

1 American University of Beirut 

2 King Abdullah University of Science and Technology 

## ABSTRACT 

Large Language Models (LLMs) are increasingly used for code generation, yet quantum code generation is still evaluated mostly within single frameworks, making it difficult to separate quantum reasoning from framework familiarity. We introduce QuanBench+, a unified benchmark spanning Qiskit, PennyLane, and Cirq, with 42 aligned tasks covering quantum algorithms, gate decomposition, and state preparation. 

We evaluate models with executable functional tests, report Pass@1 and Pass@5, and use KL-divergence-based acceptance for probabilistic outputs. We additionally study Pass@1 after feedback-based repair, where a model may revise code after a runtime error or wrong answer. Across frameworks, the strongest oneshot scores reach 59.5% in Qiskit, 54.8% in Cirq, and 42.9% in PennyLane; with feedback-based repair, the best scores rise to 83.3%, 76.2%, and 66.7%, respectively. These results show clear progress, but also that reliable multiframework quantum code generation remains unsolved and still depends strongly on framework-specific knowledge. 

**Keywords:** large language models, quantum programming, benchmarking, Qiskit, PennyLane, Cirq 

## 1 INTRODUCTION 

LLMs have achieved strong performance on classical code-generation benchmarks such as HumanEval Chen et al. (2021) and related variants. As quantum computing moves further into software practice, developers increasingly rely on ecosystems such as Qiskit Aleksandrowicz et al. (2019), PennyLane Bergholm et al. (2018), and Cirq of Cirq (2021). The practical question is no longer whether models can emit quantum-flavored code, but whether they can generate _correct_ quantum programs across frameworks with different abstractions and APIs. 

Quantum programming differs from classical programming in that program outputs are typically = _probabilistic_ measurement statistics rather than deterministic values. A qubit is represented as _|ψ⟩ α|_ 0 _⟩_ + _β|_ 1 _⟩_ , where _|α|_<sup>2</sup> and _|β|_<sup>2</sup> denote measurement probabilities Nielsen & Chuang (2010). As a result, correctness must be defined in terms of output distributions, measurement schemes, and execution settings. 

Several quantum-code benchmarks have emerged, including Qiskit HumanEval Vishwakarma et al. (2024), QHackBench Basit et al. (2025c), QCircuitBench Yang et al. (2024), and QuanBench Guo et al. (2025). Many prior evaluations are still tied to a single framework or do not explicitly hold task intent fixed across frameworks, making it hard to disentangle quantum reasoning from familiarity with the framework. 

> _∗_ The first four authors contributed equally to this work. 

1 

Published as a workshop <u>paper at ICLR 2026</u> 

A multi-framework benchmark is valuable because it exposes two distinct failure modes: (i) _conceptual_ errors in quantum reasoning (e.g., incorrect algorithmic structure or measurement logic) and (ii) _framework_ errors (e.g., wrong APIs, missing measurements, simulator misuse). Without controlling the task intent across frameworks, it is hard to attribute failures to one category or the other. 

We therefore introduce QuanBench+, a unified multi-framework evaluation that holds task intent constant while varying only the target framework. 

**Research questions (RQs).** 

We organize the paper around the following questions: 

- **RQ1** : How accurately can modern LLMs generate _correct_ quantum code across Qiskit, PennyLane, and Cirq? 

- **RQ2** : To what extent are observed gains driven by framework-specific boilerplate (prefill) versus true task-level reasoning? 

- **RQ3** : How much can an automated feedback loop improve one-shot performance under the same functional test harness? 

**Answers in brief (A1–A3).** Our experiments answer these questions as follows: 

- **A1** : Current models show real progress, but cross-framework reliability remains low and strongly framework-dependent. 

- **A2** : Prefill mainly reduces interface friction and boilerplate mistakes; it does not remove the harder semantic failures. 

- **A3** : Feedback-based repair recovers a substantial share of first-attempt failures, but the remaining errors are still dominated by reasoning mistakes. 

**Contributions.** This paper makes the following contributions: 

- We introduce QuanBench+, a unified multi-framework benchmark spanning Qiskit, PennyLane, and Cirq. 

- We adapt 42 tasks into framework-aligned prompts that preserve the same functional goal across ecosystems and support automated grading. 

- We standardize evaluation with executable Pass@k testing and KL-divergence-based acceptance for probabilistic outputs, and report Pass@1, Pass@5, and Pass@1 after feedbackbased repair. 

- We characterize where performance changes come from by comparing frameworks, prefill conditions, error types, and iterative repair. 

**Paper organization.** The remainder of the paper is organized as follows. Section 2 reviews related works, and Section 3 defines the considered evaluation criteria. Then, Sections 4 and 5 describe the benchmark model and experimental setup, respectively. Next, Section 6 presents the main results, and Sections 7 and 8 close with discussion and conclusions. 

## 2 RELATED WORK 

- 2.1 GENERAL CODE GENERATION BENCHMARKS 

HumanEval Chen et al. (2021) and HumanEval+ Liu et al. (2024) established executable functional evaluation as a standard way to assess LLM code generation. Their success made Pass@k-style testing and fixed harnesses the default for classical code, but their deterministic task design does not transfer cleanly to probabilistic quantum programs. 

- 2.2 QUANTUM CODE GENERATION BENCHMARKS 

A growing body of work evaluates LLMs for quantum programming. Qiskit HumanEval Vishwakarma et al. (2024) measures proficiency with the Qiskit API, QHackBench Basit et al. (2025c) 

2 

Published as a workshop <u>paper at ICLR 2026</u> 

focuses on PennyLane tasks derived from QHack challenges, QCircuitBench Yang et al. (2024) targets larger-scale circuit generation, and QuanBench Guo et al. (2025) curates tasks spanning algorithms, state preparation, and decomposition. QCoder Benchmark Mikuriya et al. (2025) further connects generation to execution by incorporating simulator-based feedback. 

Related work also targets domain-specific assistants and training resources. Qiskit Code Assistant Dupuis et al. (2024) and subsequent work on quantum verifiable rewards Dupuis et al. (2025) study specialized Qiskit generation, while Pennylang Basit et al. (2025a) and PennyCoder Basit et al. (2025b) focus on the PennyLane ecosystem. QUASAR extends the problem toward tool-augmented quantum assembly generation Yu et al. (2025). The common limitation is scope: most evaluations remain tied to a single framework or a single layer of the tooling stack. 

### 2.3 POSITIONING OF QUANBENCH+ 

QuanBench+ extends this line of work by holding task objectives fixed while varying the target framework. That design makes it possible to ask a more useful question: whether observed performance reflects portable quantum reasoning or simply better recall of one framework’s conventions. 

## 3 EVALUATING QUANTUM CODE GENERATION 

We follow the functional-correctness paradigm used in HumanEval Chen et al. (2021): a generated program is considered correct if it executes and satisfies a task-specific correctness criterion under a fixed harness. In our setting, tasks either admit deterministic checks or require distributional agreement of measurement outcomes. 

### 3.1 CORRECTNESS METRICS 

**Pass@k.** We use Pass@k as our primary correctness metric. Pass@k measures the probability that at least one of the top- _k_ generated solutions is correct: 



where _n_ is the number of generated samples and _c_ is the number of correct samples. We report Pass@1 and Pass@5 in this version. 

**KL divergence for probabilistic outputs.** We compute the KL divergence between the canonical distribution _P_ and the model-generated distribution _Q_ : 



To avoid undefined values when _Q_ ( _x_ ) = 0 for states with _P_ ( _x_ ) _>_ 0, we apply a small additive smoothing constant _ε_ to both distributions before renormalization. A solution is accepted when the resulting divergence is below a global threshold set to 0 _._ 05. Appendix C calibrates this threshold from repeated canonical executions of the probabilistic tasks. 

### 3.2 WHY WE EXCLUDE FIDELITY 

QuanBench Guo et al. (2025) additionally reports a _process fidelity_ (unitary overlap) between a reference circuit and a generated circuit, 



where _nq_ is the number of qubits. It measures global similarity at the level of the implemented unitary. 

In QuanBench+, we define correctness operationally as _task success_ : a solution is correct if it produces the required measurement statistics (or output probability distribution) under the promptspecified inputs and measurement scheme. Under this definition, many circuits can be _taskequivalent_ while having low unitary-overlap fidelity. For example, inserting basis-dependent phase 

3 

Published as a workshop <u>paper at ICLR 2026</u> 

transformations can preserve computational-basis measurement probabilities for a task while changing _F_ ( _U_ ref _, U_ gen) substantially. 

More generally, compilation and optimization routinely transform circuits into syntactically different realizations that are functionally equivalent. This motivates a large body of work on _quantum circuit equivalence checking_ , which explicitly targets the question “do two differently structured circuits implement the same functionality?” using decision-diagram representations, reversible miters, and SAT-/simulation-based techniques Burgholzer & Wille (2021); Yamashita & Markov (2010). In our benchmark setting, fidelity can therefore yield _false negatives_ : penalizing prompt-correct solutions that differ globally from a canonical reference circuit but still solve the task. 

Additionally, fidelity/infidelity is an average-case notion and may not align with task-relevant error, particularly under coherent noise: relationships between experimentally reported average error rates (or infidelity-like quantities) and worst-case measures can differ by orders of magnitude Kueng et al. (2016); Wallman (2015). Since our goal is to benchmark prompt-level functional correctness across frameworks, we prioritize executable functional evaluation (Pass@k) and distributional comparison (KL divergence) as primary scoring criteria, and disregard fidelity as a correctness metric. 

## 4 QU A NBE N C H+ BENCHMARK 

### 4.1 BENCHMARKING WORKFLOW 

We follow a standard benchmarking workflow: define the objective, choose metrics aligned with task outputs, control the execution environment, construct paired prompts and canonical solutions, select representative models and frameworks, and assess outputs under one automated harness. 



Figure 1: **The benchmark holds task intent and execution conditions fixed across frameworks.** Our workflow standardizes prompts, grading, and runtime settings before comparing models on Qiskit, PennyLane, and Cirq. 

### 4.2 TASK SET AND CATEGORIES 

QuanBench+ is derived from the original QuanBench task set Guo et al. (2025). We retain tasks that admit clear numerical or functional correctness criteria and adapt them to Qiskit, PennyLane, and Cirq while preserving their objectives. Prompts were modified to account for frameworkspecific APIs and library conventions. Two tasks from the original benchmark were removed because they did not support reliable cross-framework grading. The final benchmark contains 42 tasks spanning three categories: 

- **Quantum Algorithms** 

- **Gate Decomposition** 

- **State Preparation** 

### 4.3 PROMPT STANDARDIZATION AND OUTPUT NORMALIZATION 

To ensure fair comparisons, the set of canonical solutions is unified for all models across all frameworks. Each model receives the same prompt per task and framework with strict instructions on code-only output and expected function interfaces. For tasks requiring inputs, a random set of non-trivial inputs was generated once and used across all models and frameworks. Each canonical 

4 

Published as a workshop <u>paper at ICLR 2026</u> 

solution’s output is standardized to a probability array representing the measurement distribution over computational basis states. 

### 4.4 MODIFICATIONS ON PROMPTS AND CANONICAL SOLUTIONS 

**Prompt Modifications.** All prompts were modified to ensure that the correct libraries were imported for each framework. In addition, we enforced that models return code only, without any accompanying explanation, to improve execution efficiency. This requirement was explicitly stated at the beginning of each prompt. 

Table 1: **Only a small subset of tasks required benchmark-level edits.** These prompt changes and removals were needed to make grading consistent across Qiskit, PennyLane, and Cirq. 

|Task|Edit|Rationale|
|---|---|---|
|5|Task removed|Did not output a clear probabilistic answer, mak-<br>ing quantitative evaluation unreliable.|
|25|Prompt modifed|The old version measures all qubits, while the<br>new version measures the frst 3 qubits.|
|28|Prompt modifed|The prompt did not clearly instruct measuring<br>all qubits, leading to ambiguous output distribu-<br>tions.|
|38|Task removed|The testing procedure for the machine learning<br>task was not clearly specifed, preventing con-<br>sistent evaluation.|
|41|Prompt modifed|The randomized input library was replaced by a<br>pre-decided randomly generated input.|



## 5 EXPERIMENTAL SETUP 

### 5.1 MODELS 

We evaluate a diverse set of frontier and open-weight LLMs (listed in Appendix A), covering both models studied in QuanBench and more recent releases. All requests are issued through a unified API router. For Pass@1, we use greedy decoding (temperature 0 _._ 0) and sample one completion per task. For Pass@5, we sample _k_ = 5 completions per task at temperature 0 _._ 8. 

### 5.2 EXECUTION ENVIRONMENT 

All generated solutions are executed in a controlled Python environment. To facilitate comparison with prior results, we use Python 3.10, Qiskit v0.46.0, Cirq v1.6.1, and PennyLane v0.43.1. 

**Execution and Grading Pipeline** For each model completion, we apply the same evaluation procedure: 

- **P1:** Parse the completion and extract executable code. 

- **P2:** Execute the code in the target framework environment. 

- **P3:** Compare outputs using deterministic checks or a distributional threshold. 

### 5.3 FEEDBACK LOOP 

In addition to standard one-shot generation, we evaluate a feedback loop setting that allows a model to repair its answer. The feedback loop is triggered on both runtime exceptions and wrong answer outputs. For each task, we execute the initial completion under the same harness used for Pass@k. If execution raises an exception (e.g., syntax/import/runtime errors), we provide the model with the exception trace and the original prompt, and request a corrected code-only solution. If the output of the generated code does not match the canonical solution, we provide the model with the wrong 

5 

Published as a workshop <u>paper at ICLR 2026</u> 

function and the original prompt, and request a corrected code-only solution. We report Pass@1 under this feedback loop as Pass@1 (FB). In all cases, we provide the models with a maximum of 5 repair chances. 

## 6 RESULTS 

Three patterns dominate the results. Qiskit is consistently the easiest framework, PennyLane is consistently the hardest, and feedback-based repair recovers a large share of first-attempt failures without eliminating the remaining semantic mistakes. Detailed per-task maps and Pass@1-versusPass@5 comparisons are deferred to Appendices E and F. 

### 6.1 **RQ1** : CROSS-FRAMEWORK FUNCTIONAL CORRECTNESS 

Figure 2 provides the main one-shot ranking, while Appendix Table 3 reports the exact values. The strongest Pass@1 scores reach 59.5% in Qiskit, 54.8% in Cirq, and 42.9% in PennyLane, which is enough to show real progress but not enough to claim dependable cross-framework generation. 

The central finding is framework asymmetry rather than one universally dominant model. Gemini 3 Pro leads the average one-shot ranking because it is strongest on Qiskit and Cirq, whereas GPT-5.1 posts the best one-shot score on PennyLane. Across nearly every model, Qiskit sits highest and PennyLane lowest, indicating that framework-specific familiarity still explains a meaningful share of the variance. 



Figure 2: **Qiskit is the easiest target and PennyLane the hardest under one-shot generation.** Models are ordered by average Pass@1 across frameworks, revealing both a stable ranking and a persistent framework gap. 

### 6.2 **RQ2** : PREFILL VS NO-PREFILL 

Prefill mainly reduces interface friction rather than solving the hard reasoning cases. The appendix figures show that the largest gains tend to appear among smaller and mid-tier models, especially when framework boilerplate is easy to get wrong. Stronger models still benefit in some settings, but much less dramatically, which suggests that prefill helps most with imports, signatures, and setup rather than semantic program construction (Appendix G). 

6 

Published as a workshop <u>paper at ICLR 2026</u> 

### 6.3 **RQ3** : FEEDBACK-BASED REPAIR 

Feedback-based repair materially lifts performance across all three frameworks. Figure 3 shows that the strongest repaired systems reach **83.3%** in Qiskit, **76.2%** in Cirq, and **66.7%** in PennyLane. The gains are not limited to the frontier models: much of the middle of the ranking also improves sharply once runtime traces or wrong-answer signals are fed back to the model. 

The improvement pattern matters as much as the headline numbers. Feedback narrows the gap caused by framework misuse and surface-level coding errors, but Appendix I shows that the remaining failures are still dominated by deeper semantic mistakes. Appendix Table 3 reports the exact Pass@1 and Pass@1 (FB) values used in the main paper. 



Figure 3: **Feedback repair lifts accuracy across all three frameworks.** The gains are broad rather than model-specific, but no framework becomes fully reliable after repair. 

We evaluate 42 tasks spanning quantum algorithms, state preparation, and gate decomposition; the task-count breakdown appears in Appendix D. 

## 7 DISCUSSION 

The main result is not simply that newer models score higher; it is that difficulty remains strongly framework-dependent. Qiskit consistently yields the strongest outcomes, PennyLane remains harder even after repair, and Cirq typically falls in between. That pattern suggests current systems still rely heavily on framework-specific exposure and API familiarity rather than portable quantum programming competence. 

We also observe a clear separation between errors that feedback can fix and errors that it cannot. Runtime and interface failures are often recoverable, but Appendix H and Appendix I show that the residual failures increasingly concentrate in deeper semantic mistakes. 

### 7.1 THREATS TO VALIDITY 

Our evaluation depends on the correctness and completeness of canonical solutions. Crossframework adaptation can introduce subtle mismatches between prompts and reference implemen- 

7 

Published as a workshop <u>paper at ICLR 2026</u> 

tations, even when the intended task is the same. We mitigate this risk by excluding ambiguously graded tasks and reviewing framework-specific canonical code for functional equivalence. 

A second threat is category imbalance. Quantum-algorithm tasks substantially outnumber statepreparation and decomposition tasks, which can amplify their influence on aggregate metrics and make the benchmark look harder wherever multi-step reasoning is required. Framework versioning is another source of uncertainty: a model may capture the right high-level intent while still failing execution because it reproduces stale APIs. 

### 7.2 LIMITATIONS & FUTURE WORK 

QuanBench+ contains 42 tasks and therefore does not capture the full long tail of real-world quantum development. We also report only Pass@1, Pass@5, and Pass@1 (FB) in this version, which leaves out other potentially useful views of model behavior such as robustness to prompt variation, longer repair horizons, and tool-augmented workflows. Finally, the benchmark currently covers Qiskit, PennyLane, and Cirq; extending the same methodology to additional frameworks remains open future work. 

## 8 CONCLUSION 

We answer **RQ1** , **RQ2** , and **RQ3** by introducing QuanBench+, a unified multi-framework benchmark for evaluating LLMs on quantum code generation in Qiskit, PennyLane, and Cirq. By adapting one task set across three ecosystems and grading outputs with executable functional tests, we provide a clearer picture of where current systems succeed, where they fail, and how much iterative repair can recover. 

The headline conclusion is straightforward: modern models can often produce plausible quantum code, but reliable multi-framework correctness is still out of reach. Future progress will likely require more than model scale alone. It will depend on stronger exposure to quantum software data, better support for compositional reasoning and repair, and closer alignment with framework-specific APIs and execution patterns. We hope QuanBench+ provides a practical, reproducible basis for that next stage of evaluation<sup>1</sup> . 

## REFERENCES 

Jack Achiam, Shaked Adler, Sandhini Agarwal, Lena Ahmad, et al. Gpt-4 technical report. _arXiv preprint arXiv:2303.08774_ , 2023. URL https://arxiv.org/abs/2303.08774. 

- Meta AI. Llama 4 maverick: Model card. https://ai.meta.com/llama/, 2025. [Accessed: 2025-07-12]. 

- Gadi Aleksandrowicz, Thomas Alexander, Panagiotis Barkoutsos, et al. Qiskit: An open-source framework for quantum computing. _Zenodo_ , 2019. doi: 10.5281/zenodo.2562111. URL https: //qiskit.org. 

Anthropic. Claude 3.7 sonnet: Model release. https://www.anthropic.com/news/ claude-3-7-sonnet, 2025. [Accessed: 2025-07-12]. 

Zhihong Bai, Weizhe Yang, Yuzhe Chen, Chenxi Qian, Shuobo Li, et al. Qwen2.5 technical report. _arXiv preprint arXiv:2412.15115_ , 2024. URL https://arxiv.org/abs/2412.15115. 

- Abdul Basit, Nouhaila Innan, Muhammad Haider Asif, Minghao Shao, Muhammad Kashif, Alberto Marchisio, and Muhammad Shafique. Pennylang: Pioneering llm-based quantum code generation with a novel pennylane-centric dataset. _arXiv preprint arXiv:2503.02497_ , 2025a. 

- Abdul Basit, Minghao Shao, Muhammad Haider Asif, Nouhaila Innan, Muhammad Kashif, Alberto Marchisio, and Muhammad Shafique. Pennycoder: Efficient domain-specific llms for pennylanebased quantum code generation. In _2025 IEEE International Conference on Quantum Computing and Engineering (QCE)_ , volume 2, pp. 229–234. IEEE, 2025b. 

> 1Source code: https://github.com/JawadKotaichh/quanbench-plus 

8 

Published as a workshop <u>paper at ICLR 2026</u> 

- Abdul Basit, Minghao Shao, Muhammad Haider Asif, et al. Qhackbench: Benchmarking large language models for quantum code generation using pennylane hackathon challenges. _arXiv preprint arXiv:2506.20008_ , 2025c. URL https://arxiv.org/abs/2506.20008. 

- Ville Bergholm, Josh Izaac, Maria Schuld, et al. Pennylane: Automatic differentiation of hybrid quantum-classical computations. _arXiv preprint arXiv:1811.04968_ , 2018. URL https: //arxiv.org/abs/1811.04968. 

- Lukas Burgholzer and Robert Wille. Advanced equivalence checking for quantum circuits. _IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems_ , 40(9):1810–1824, 2021. doi: 10.1109/TCAD.2020.3032630. 

Mark Chen, Jerry Tworek, Heewoo Jun, et al. Evaluating large language models trained on code. _arXiv preprint arXiv:2107.03374_ , 2021. URL https://arxiv.org/abs/2107.03374. 

Google DeepMind. Gemini 3 (model family overview). https://deepmind.google/ models/gemini/, 2025. [Accessed: 2026-01-15]. 

DeepSeek-AI. Deepseek-v3 technical report. _arXiv preprint arXiv:2412.19437_ , 2024. URL https://arxiv.org/abs/2412.19437. 

- Nicolas Dupuis, Luca Buratti, Sanjay Vishwakarma, Aitana Viudes Forrat, David Kremer, Ismael Faro, Ruchir Puri, and Juan Cruz-Benito. Qiskit code assistant: Training llms for generating quantum computing code. In _2024 IEEE LLM Aided Design Workshop (LAD)_ , pp. 1–4. IEEE, 2024. 

- Nicolas Dupuis, Adarsh Tiwari, Youssef Mroueh, David Kremer, Ismael Faro, and Juan CruzBenito. Quantum verifiable rewards for post-training qiskit code assistant. _arXiv preprint arXiv:2508.20907_ , 2025. 

- Google. Gemini 2.5 flash (model documentation). https://docs.cloud.google.com/ vertex-ai/generative-ai/docs/models/gemini/2-5-flash, 2025. [Accessed: 2026-01-15]. 

- Xiaoyu Guo, Minggu Wang, and Jianjun Zhao. Quanbench: Benchmarking quantum code generation with large language models. _arXiv preprint arXiv:2510.16779_ , 2025. URL https: //arxiv.org/abs/2510.16779. 

- Richard Kueng, David M. Long, Andrew C. Doherty, and Steven T. Flammia. Comparing experiments to the fault-tolerance threshold. _Physical Review Letters_ , 117:170502, 2016. doi: 10.1103/PhysRevLett.117.170502. 

- Linxi Liu, Ekin Zelikman, et al. Humaneval+: Training and evaluating code generation models on harder problems. _arXiv preprint arXiv:2404.12246_ , 2024. URL https://arxiv.org/abs/ 2404.12246. 

- Taku Mikuriya, Tatsuya Ishigaki, Masayuki Kawarada, Shunya Minami, Tadashi Kadowaki, Yohichi Suzuki, Soshun Naito, Shunya Takada, Takumi Kato, Tamotsu Basseda, et al. Qcoder benchmark: Bridging language generation and quantum hardware through simulator-based feedback. In _Proceedings of the 18th International Natural Language Generation Conference_ , pp. 743–752, 2025. 

MiniMax. Minimax-m2.1 large language model. https://platform.minimax.chat/ docs, 2024. 

- Moonshot AI. Kimi-k2 (thinking) large language model. https://platform.moonshot. cn/docs, 2024. 

- Michael A. Nielsen and Isaac L. Chuang. _Quantum Computation and Quantum Information_ . Cambridge University Press, 10th anniversary edition edition, 2010. 

- Developers of Cirq. Cirq: A python framework for nisq algorithms. _Zenodo_ , 2021. doi: 10.5281/ zenodo.5182845. URL https://cirq.io. 

9 

Published as a workshop <u>paper at ICLR 2026</u> 

- OpenAI. Gpt-5: Model overview. https://platform.openai.com/docs/models, 2025. [Accessed: 2025-07-12]. 

- Sanjay Vishwakarma, Francis Harkins, Siddharth Golecha, et al. Qiskit humaneval: An evaluation benchmark for quantum code generative models. _arXiv preprint arXiv:2406.14712_ , 2024. URL https://arxiv.org/abs/2406.14712. 

- Joel J. Wallman. Bounding experimental quantum error rates relative to fault-tolerant thresholds, 2015. URL https://arxiv.org/abs/1511.00727. 

- Shigeru Yamashita and Igor L. Markov. Fast equivalence-checking for quantum circuits. _Quantum Information and Computation_ , 9(9–10):721–734, 2010. doi: 10.48550/arXiv.0909.4119. 

- Rui Yang, Ziruo Wang, Yuntian Gu, Tianyi Chen, Yitao Liang, and Tongyang Li. Qcircuitbench: A large-scale dataset for benchmarking quantum algorithm design. _arXiv preprint arXiv:2410.07961_ , 2024. URL https://arxiv.org/abs/2410.07961. 

- Cong Yu, Valter Uotila, Shilong Deng, Qingyuan Wu, Tuo Shi, Songlin Jiang, Lei You, and Bo Zhao. QUASAR: Quantum assembly code generation using tool-augmented LLMs via agentic RL, 2025. URL https://openreview.net/forum?id=fKKKtEW71h. 

- Zhipu AI. Glm-4: Open large language models. _arXiv preprint arXiv:2404.03880_ , 2024. URL https://arxiv.org/abs/2404.03880. 

10 

Published as a workshop <u>paper at ICLR 2026</u> 

## A MODELS EVALUATED 

The main paper focuses on comparative behavior; this appendix records the exact model list and the release references used to define the evaluated set. 

Table 2: **The benchmark spans both frontier proprietary and open-weight systems.** This table lists the evaluated models and the release reference used for each one. 

|**Model**|**Reference**|
|---|---|
|Claude-3.7-Sonnet|Anthropic(2025)|
|DeepSeek-Chat|DeepSeek-AI(2024)|
|DeepSeek-R1|DeepSeek-AI(2024)|
|Gemini-2.5-Flash|Google(2025)|
|Gemini-3-Pro|DeepMind(2025)|
|GPT-4.1|Achiam et al.(2023)|
|GPT-5.1|OpenAI(2025)|
|Llama-4-Maverick|AI(2025)|
|Qwen-2.5-7B-Instruct|Bai et al.(2024)|
|MiniMax-M2.1|MiniMax(2024)|
|Z-ai-GLM-4.7|Zhipu AI(2024)|
|MoonshotAI-Kimi-K2-Thinking|Moonshot AI(2024)|



## B EXACT MAIN-PAPER RESULT TABLES 

The main paper emphasizes summary figures. This section records the exact one-shot and feedbackrepair scores used in the core narrative. 

Table 3: **Feedback repair lifts scores across all three frameworks.** Exact Pass@1 and Pass@1 <u>(FB) values reported in the main paper.</u> 

|**Model**|**Pass@1**|**Qiskit**<br>**Pass@1 (FB)**|**Pass@1**|**Cirq**<br>**Pass@1 (FB)**|**Pe**<br>**Pass@1**|**nnyLane**<br>**Pass@1 (FB)**|
|---|---|---|---|---|---|---|
|Gemini-3-Pro|**59.5**|73.8|**54.8**|**76.2**|40.5|**66.7**|
|GPT-5.1|57.1|**83.3**|52.4|73.8|**42.9**|**66.7**|
|DeepSeek-R1|50.0|71.4|45.2|61.9|33.3|52.4|
|MoonshotAI-Kimi-K2-Thinking|47.6|69.0|38.1|57.1|26.2|38.1|
|Claude-3.7-Sonnet|45.2|57.1|35.7|59.5|26.2|47.6|
|GPT-4.1|50.0|57.1|33.3|57.1|23.8|45.2|
|DeepSeek-Chat|45.2|42.9|28.6|40.5|31.0|45.2|
|Z-ai-GLM-4.7|42.9|69.0|38.1|61.9|23.8|64.3|
|Gemini-2.5-Flash|40.5|61.9|35.7|50.0|23.8|40.5|
|Llama-4-Maverick|38.1|54.8|28.6|42.9|19.0|38.1|
|MiniMax-M2.1|28.6|57.1|23.8|47.6|31.0|47.6|
|Qwen-2.5-7B-Instruct|16.7|19.0|4.8|7.1|11.9|19.0|



## C CALIBRATION OF THE KL ACCEPTANCE THRESHOLD 

Some benchmark tasks are probabilistic: correctness is defined by matching a target measurement distribution rather than a single deterministic output. Even the canonical circuit exhibits finite-shot variability, so we calibrate the acceptance threshold from repeated canonical executions instead of setting it heuristically. 

For each probabilistic task _t_ , we run the canonical reference circuit _R_ = 1000 times to obtain empirical distributions _{Pi_<sup>(</sup><sup>_t_)</sup> _}_<sup>_R_</sup> _i_ =1<sup>anddefinethetaskreferencedistributionastheirrenormalized</sup> mean: 



11 

Published as a workshop <u>paper at ICLR 2026</u> 

We then measure within-canonical variability via the null KL distribution 



and select a global threshold from a high quantile of the pooled null values across tasks: 



With _q_ = 0 _._ 997, the resulting pooled threshold is _τ_ global = 0 _._ 048, so we use _τ_ = 0 _._ 05 as a slightly more permissive paper-wide constant. 



Figure 4: **The null KL distribution supports the global acceptance threshold.** The pooled canonical-repeat ECDF places the 99.7th percentile at 0.048, motivating the paper-wide threshold _τ_ = 0 _._ 05. 

## D TASK CATEGORIES AND EXAMPLES 

Table 4: **Quantum algorithms dominate the benchmark mix.** QuanBench+ contains 42 tasks, with most concentrated in algorithmic reasoning. 

|**Category**|**Number of Tasks**|
|---|---|
|Quantum Algorithms|31|
|State Preparation|6|
|Decomposition|5|
|**Total**|**42**|



QuanBench+ organizes tasks equivalently across frameworks: 

- **Quantum Algorithms** : implement known algorithms or subroutines. 

- **Gate Decomposition** : convert high-level operations into native gates. 

- **State Preparation** : construct circuits to produce target quantum states. 

## E PASS@1 VS PASS@5 COMPARISONS 

Pass@1 measures top-1 solution correctness, while Pass@5 measures correctness across the top 5 generated solutions. 

12 

Published as a workshop <u>paper at ICLR 2026</u> 

**What to look for:** These figures show whether correct solutions are absent altogether or simply not selected on the first try. Large gaps between Pass@1 and Pass@5 indicate that models often contain the right solution among a small set of samples, even when one-shot decoding misses it. 



Figure 5: **Multiple samples recover additional Qiskit solutions.** The gap between Pass@1 and Pass@5 identifies tasks where one-shot decoding leaves recoverable performance on the table. 

13 

Published as a workshop <u>paper at ICLR 2026</u> 



Figure 6: **Cirq also benefits meaningfully from multi-sample generation.** The gains are especially visible among the middle of the model ranking. 



Figure 7: **PennyLane retains large recoverable gaps for weaker models.** Multi-sample decoding helps, but it does not close the framework-level difficulty gap. 

14 

Published as a workshop <u>paper at ICLR 2026</u> 

## F PER-TASK HEATMAPS 

### PASS@1 HEATMAPS 

**What to look for:** The Pass@1 heatmaps show where one-shot reliability is genuinely strong and where it breaks down task by task. Dense horizontal bands indicate broadly capable models; persistent white columns indicate tasks that remain difficult for almost everyone. 



Figure 8: **One-shot success in Qiskit is concentrated in a broad but incomplete task band.** Each row corresponds to a model and each column to a task. 



Figure 9: **PennyLane exposes a noticeably sparser one-shot success map.** Each row corresponds to a model and each column to a task. 

15 

Published as a workshop <u>paper at ICLR 2026</u> 



Figure 10: **Cirq sits between Qiskit and PennyLane in first-attempt density.** The overall pattern is stronger than PennyLane but less complete than Qiskit. 

### PASS@5 HEATMAPS 

**What to look for:** Compared with the Pass@1 maps, these heatmaps reveal how much additional coverage appears once models are allowed multiple tries. New dark regions indicate tasks where the capability exists but is unstable under one-shot decoding. 



Figure 11: **Pass@5 broadens Qiskit coverage substantially.** Multi-sample decoding turns many partial one-shot failures into recoverable successes. 

16 

Published as a workshop <u>paper at ICLR 2026</u> 



Figure 12: **Pass@5 helps in PennyLane, but hard tasks remain visibly persistent.** Multi-sample decoding broadens coverage without removing the framework gap. 



Figure 13: **Cirq gains a wider solvable region under Pass@5.** The additional coverage confirms that many one-shot failures are unstable rather than absolute. 

17 

Published as a workshop <u>paper at ICLR 2026</u> 

Table 5: **Pass@5 narrows but does not remove framework gaps.** Accuracy (%) over benchmark tasks for each framework. 

|**Model**|**Qiskit**|**Cirq**|**PennyLane**|
|---|---|---|---|
|Gemini-3-Pro|61.9|59.5|40.5|
|GPT-5.1|**76.2**|**64.3**|57.1|
|DeepSeek-R1|69.0|61.9|**59.5**|
|MoonshotAI-Kimi-K2-Thinking|66.7|52.4|52.4|
|Claude-3.7-Sonnet|50.0|57.1|38.1|
|GPT-4.1|52.4|54.8|35.7|
|DeepSeek-Chat|54.8|45.2|47.6|
|Z-ai-GLM-4.7|66.7|59.5|47.6|
|Gemini-2.5-Flash|40.5|35.7|35.7|
|Llama-4-Maverick|47.6|38.1|31.0|
|MiniMax-M2.1|54.8|50.0|54.8|
|Qwen-2.5-7B-Instruct|23.8|23.8|21.4|



## G PREFILL VS NO-PREFILL 

We evaluate two prompting conditions for all models and frameworks: 

- **Prefill** : the prompt includes required imports, function signature, and minimal boilerplate. 

- **No-prefill** : the model generates the full solution from scratch. 

**What to look for:** These figures isolate how much of the error budget comes from boilerplate and setup rather than task logic. Larger gaps between the paired bars indicate models that depend heavily on scaffolding to produce executable framework code. 



Figure 14: **Prefill helps most when PennyLane boilerplate is easy to miss.** The ranking changes confirm that setup friction still matters for several mid-tier models. 

18 

Published as a workshop <u>paper at ICLR 2026</u> 



Figure 15: **Cirq also shows meaningful sensitivity to prompt scaffolding.** Prefill changes both average accuracy and several mid-tier rankings. 



Figure 16: **Qiskit benefits from prefill, but less uniformly than weaker frameworks.** The effect is real, though not consistent across the full model range. 

## H ERROR DISTRIBUTIONS 

This section examines what goes wrong when first-attempt solutions fail. The goal is to separate semantic mistakes from implementation and framework-use errors. **Observation:** Figure 17 shows that most Pass@1 failures are driven by semantic mistakes: wrong answers (46 _._ 7%) and logic errors (25 _._ 0%) together dominate the error budget. More direct implementation problems still matter, but 

19 

Published as a workshop <u>paper at ICLR 2026</u> 



Figure 17: **Most first-attempt failures are semantic, not syntactic.** Wrong answers and logic errors dominate the Pass@1 error budget across frameworks. 

they are secondary, including missing methods/gates (11 _._ 8%), shape mismatches (8 _._ 0%), syntax errors (4 _._ 7%), and qubit specification errors (3 _._ 9%). This split helps explain why feedback can recover many first-attempt failures without eliminating the deeper reasoning gap. 

## I FEEDBACK-LOOP RESULTS 

We applied up to 5 repair attempts via feedback loops. 

**What to look for:** The feedback plots show both the upside and the limit of iterative repair. Dense heatmaps and rapidly rising curves indicate that many failures are fixable once the model sees an execution signal, while the remaining gaps reveal the tasks that stay hard even after several retries. 

20 

Published as a workshop <u>paper at ICLR 2026</u> 



Figure 18: **Feedback densifies the Qiskit success map.** Stronger models in particular convert many previously sparse regions into solved tasks. 



Figure 19: **Feedback improves PennyLane coverage, but the map remains visibly harder.** The gains are substantial without fully closing the framework gap. 

21 

Published as a workshop <u>paper at ICLR 2026</u> 



Figure 20: **Feedback broadens Cirq success across much of the ranking.** The densification is clear, especially among stronger and mid-tier models. 

**Observations: (i)** Performance increases monotonically with additional feedback attempts, which confirms that iterative repair generally improves functional correctness. **(ii)** Most gains arrive early (attempts 1 _→_ 2), followed by diminishing returns after roughly three attempts. **(iii)** Qiskit (Fig. 21) saturates earlier for the strongest models, whereas PennyLane (Fig. 22) and Cirq (Fig. 23) often improve more gradually through attempts 4–5. **(iv)** Feedback compresses the spread among stronger models, but the weakest systems plateau quickly, which points to failure modes that retries do not resolve. 



Figure 21: **Most Qiskit feedback gains arrive early.** The curves rise quickly in the first repair rounds and then flatten. 

22 

Published as a workshop <u>paper at ICLR 2026</u> 



Figure 22: **PennyLane improves steadily, but not indefinitely, with additional repair attempts.** Most of the lift still arrives in the early rounds. 



Figure 23: **Cirq follows the same early-gain, late-plateau pattern.** Additional repair attempts help most in the first few rounds. 

23 

Published as a workshop <u>paper at ICLR 2026</u> 



Figure 24: **Feedback compresses the spread between models, but does not erase it.** Aggregate success rates after up to 5 repair attempts across all frameworks. 



Figure 25: **After repair, the remaining failures are mostly semantic.** Residual post-feedback errors become more concentrated in deeper reasoning mistakes. 

**Observations:** After the feedback loop, Fig. 25 shows that the total number of wrong tasks decreases substantially, from 977 to 665. The remaining errors are even more heavily concentrated in semantic issues, with wrong answers accounting for 53.4% of failures, followed by logic errors (22.0%) and shape mismatches (12.8%). Surface-level implementation problems such as missing methods/gates (3.8%) and syntax errors (1.5%) become much less frequent. In other words, feedback is effective at fixing visible coding mistakes, but the harder remaining problem is still correct reasoning. 

24