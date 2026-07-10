Empirical Software Engineering          (2026) 31:178 https://doi.org/10.1007/s10664-026-10911-6 



# **An empirical study of LLM-based refactoring consistency** 

### **Yang Zhang**<sup>**1**</sup> **· Lijie Yuan**<sup>**1**</sup> **· Chunhao Dong**<sup>**1**</sup> 

Received: 18 November 2025 / Accepted: 16 June 2026 © The Author(s), under exclusive licence to Springer Science+Business Media, LLC, part of Springer Nature 2026 

### **Abstract** 

Behavioral consistency plays an important role in improving software evolution efficiency and guaranteeing software reliability in modern software refactoring. Although large language models (LLMs) demonstrate great potential in multiple software engineering tasks, including code generation, code completion, and code repair, few works have been conducted on LLM-based code refactoring. Furthermore, existing works are confused about how LLMs impact refactoring consistency. Therefore, there is an urgent need to conduct a systematic evaluation of behavioral consistency before and after refactoring. To this end, this paper conducts the first empirical study on LLM-based refactoring consistency. Firstly, we construct a high-quality dataset _DataRef_ with 468 Java and 544 Python code segments, and refactor them using existing LLMs (e.g., ChatGPT-3.5/4.0, CodeLlama, CodeGeeX), generating 8,096 refactored code segments. Results demonstrate that a total of 928 refactored code segments exhibit behavioral inconsistencies, while 180 cases result in refactoring failures. We then establish a taxonomy to classify these inconsistency patterns. Thirdly, to evaluate the refactoring ability of representative state-of-the-art LLMs released in 2025, we construct a new dataset _DataRef+_ from inconsistent code segments, including 272 Java and 297 Python code segments. Experimental results show that 6.06% of code segments still suffer from inconsistencies. Finally, we propose a mitigation strategy combining retrieval-augmented generation and structured few-shot prompting. As an initial validation evaluated on ChatGPT-3.5 with Python code and single-round generation, this strategy reduces the inconsistency rate by 12.46 percentage points, from 17.17% to 4.71%. Our work provides empirical evidence for enhancing consistency in LLM-based refactoring and paves the way for future research. 

**Keywords** Code refactoring · Empirical study · large language models · Consistency · Prompt 



Communicated by: Lucia Passaro, Humberto Torres Marques-Neto, Marco Tulio Valente This article belongs to the Topical Collection: _Special Issue on 2025-SE-LLMs_ . 

Extended author information available on the last page of the article 

<mark>178 Page 2 of 41</mark> 

Empirical Software Engineering          (2026) 31:178 

## **1 Introduction** 

Software refactoring refers to a technical practice that systematically optimizes existing software code structure without altering external behavior, aiming to improve code readability, maintainability, and scalability (Fowler 2018; AlOmar et al. 2021). Behavioral consistency serves as a key prerequisite for ensuring software quality, enhancing evolution efficiency, and safeguarding reliability (Fowler 2018). During software evolution processes, the lack of consistency may lead to serious consequences. Even minor behavioral inconsistencies, such as miscalculations of variable values, deviations in function return results, or unforeseen changes to input/output logic, can trigger interface call failures, disrupt the normal inter-module collaboration, and in high-concurrency or complex business scenarios, even result in core functional breakdowns. This ultimately undermines the quality improvements and efficiency gains that refactoring is intended to deliver. 

Early refactoring technologies relied on program analysis and formal methods. They identified refactorable patterns through static code analysis (AlOmar et al. 2021; Zhang and Xue 2024) and generate optimized schemes by combining predefined refactoring rules. While these methods can ensure consistency before and after refactoring, they depend on rule definitions and domain knowledge. Subsequently, search-based refactoring emerged, which employs heuristic algorithms to search for optimal refactoring paths in the solution space (Adler et al. 2021; Zhang et al. 2024), attempting to balance refactoring quality and consistency. However, its high computational complexity leads to increased costs for consistency verification. In recent years, machine learning has been applied to refactoring tasks. It leverages their learning and generalization capabilities to detect code smells (Azeem et al. 2019). The widespread application of deep learning has advanced software refactoring research, with neural network models learn code structural features to achieve code smell detection and refactoring suggestion generation (Zhang et al. 2022, 2025b; Li and Zhang 2024), breaking through the limitations of traditional rule-based approaches to a certain degree. However, they face the problem of shallow semantic understanding, often producing refactoring schemes that are syntactically correct but behaviorally inconsistent. Recently, large language models (LLMs) (Glm et al. 2024; Peng et al. 2023; Achiam et al. 2023; Zheng et al. 2023; Liu et al. 2024; Guo et al. 2025; Bai et al. 2025; Roziere et al. 2023) have demonstrated tremendous potential in the field of software engineering (Zhang et al. 2025a), bringing a new paradigm to automatic refactoring (Dong et al. 2025). However, current studies focus on exploring LLMs’ capabilities in assisting code refactoring (DePalma et al. 2024), and LLMs’ hallucination poses potential risks to consistency before and after refactoring (Huang et al. 2025; Zhang et al. 2025c). There remains a lack of systematic evaluation of the consistency of LLMs’ refactoring outcomes. 

The consistency of program behavior before and after software refactoring is a major concern in the era of large language models (Torres et al. 2021). The methods include LLM-based detection, test case-based detection, hybrid detection by combining LLMs with static analysis, and collaborative detection between LLMs and humans. LLM-based detection methods mainly rely on LLMs for refactoring consistency assessment. DePalma et al. (2024) adopted an LLM-based approach to evaluate ChatGPT’s refactoring capabilities. In addition to using ChatGPT for refactoring attempts, they also utilized it to assess consis- 

```
1 3
```

Empirical Software Engineering          (2026) 31:178 

<mark>Page 3 of 41 178</mark> 

tency before and after refactoring. While this method is time-saving and labor-efficient, it suffers from inherent issues of LLMs, such as uncertainty and hallucinations, resulting in relatively low accuracy. Test case-based detection methods perform regression testing or differential testing using existing or LLM-generated test cases (Dilhara et al. 2024; Wadhwa et al. 2023) to verify the behavioral consistency of LLMs. This method depends on the comprehensive coverage of test cases; if the number of test cases is insufficient, it is difficult to identify the root causes of inconsistencies. Due to the inherent limitations of LLMs, many researchers have adopted detection methods combining LLMs with static analysis or collaborative methods between LLMs and humans (Pomian et al. 2024; AlOmar et al. 2024). These approaches have improved the accuracy of refactoring consistency detection. Although related research has been conducted on refactoring consistency, there is a lack of empirical research on consistency before and after refactoring. 

To this end, this paper conducts the first empirical research on the consistency of LLMbased code refactoring before and after the process. Firstly, we collect programs from multiple sources to construct a high-quality dataset named _DataRef_ . Subsequently, we use LLMs such as ChatGPT3.5/4.0, CodeLlama, and CodeGeeX to refactor these code segments, yielding the refactored code versions. To systematically analyze the inconsistencies arising from LLM-based refactoring, we tested and compared the refactored code. After inspection, a total of 928 code segments exhibited behavioral inconsistencies and 180 suffered from refactoring failures. We then classified these inconsistent code segments based on the open card sorting method, identifying four major categories of inconsistency patterns, including variable-related inconsistency, statement-related inconsistency, method-related inconsistency, and algorithm-related inconsistency. Building on these findings, we constructed a new dataset _DataRef+_ , focused on inconsistent cases to evaluate the refactoring performance of representative state-of-the-art LLMs released in 2025 such as DeepSeek-V3/R1 and Qwen2.5-32B/72B. Finally, we proposed a method integrating retrieval-augmented generation (RAG) with a structured few-shot prompting approach, optimizing ChatGPT3.5 through prompt engineering to mitigate inconsistencies in LLM-based code refactoring. As an initial validation, the results show that the number of inconsistencies decreased by 12.46 percentage points (p.p.), offering useful empirical insights for improving consistency in LLM-based code refactoring. 

The main contributions of this paper are as follows. 

- We construct a code refactoring dataset containing 468 Java and 544 Python code segments. 

- We conduct empirical study on the inconsistency of LLM-based code refactoring, analyze the causes, and establish a classification framework. 

- We propose an approach to mitigate inconsistencies by integrating the RAG with a structured few-shot prompting approach during LLM-based code refactoring. 

The organization of this paper is as follows. Section 2 presents the related work. Section 3 describes the methodology and experimental setup. Section 4 presents the experimental results. Section 5 proposes a mitigation method. Section 6 discuss the related problem and limitations. Section 7 discusses the threats to validity and conclusions are drawn in Section 8. 

```
1 3
```

<mark>178 Page 4 of 41</mark> 

Empirical Software Engineering          (2026) 31:178 

## **2 Related Works** 

This section examines the related works of software refactoring and its consistency. 

### **2.1 Software Refactoring** 

Code refactoring intends to improve the internal structure and readability of programs while maintaining their external behavior unchanged. Early research typically relied on manual refactoring based on experience, which involved identifying refactorable patterns through static code analysis (AlOmar et al. 2021; Zhang and Xue 2024) and then generating optimization schemes by combining predefined refactoring rules. For instance, WitchDoctor (Foster et al. 2012) is a tool capable of detecting programmers’ refactoring behaviors and completing refactoring automatically, while Blue-Pencil further enhances the refactoring functionality of Visual Studio (Miltner et al. 2019). Search-based techniques use heuristics to identify code segments that can improve program readability or reduce complexity, and this method has also been widely applied in refactoring recommendations (Adler et al. 2021; Zhang et al. 2024). 

Machine learning has been widely applied to code refactoring in recent years. Maiga et al. (2012b, 2012a) applied support vector machines to code smell detection and achieved preliminary results. Subsequently, deep learning technologies were introduced into refactoring tasks, as demonstrated by Liu et al. (2019), who leveraged deep learning to train neural networks via large-scale data synthesis, aiming to detect code smells and generate refactoring suggestions. To address the issue that synthetic data cannot fully reflect real-world code smells, Liu et al. (2023) proposed a scheme to automatically collect code smells and corresponding refactorings from real projects, providing high-quality training data. Kurbatova et al. (2020) proposed a hybrid method that combines deep learning with SVM-based classifiers, effectively identifying feature envy code smells. 

Regarding architecture-level refactoring, existing research mainly focuses on tool assistance or algorithm optimization to address the complexity and consistency issues of architectural design. Lin et al. (2016) proposed a tool-supported interactive recommendation method to assist architectural refactoring, but it relies on manual screening and adjustment of recommended schemes, resulting in limited automation. Ivers et al. (2022) conducted refactoring recommendations through search-based algorithms, which can isolate specified software from complex architectural dependencies. However, this method requires predefined weight rules for dependencies, leading to high adaptation costs for new domains. Chondamrongkul and Sun (2023) proposed a method to automatically generate evolution plans for refactoring architectural designs to support new functionalities. Nevertheless, it relies on the mapping relationships between architectures and functionalities, making it difficult to cope with undefined dynamic refactoring requirements. 

### **2.2 Refactoring Consistency** 

Refactoring consistency is the core of code refactoring. Existing studies adopt methods such as formal verification, test verification, and tool-assisted approaches. Yin et al. (2009) proposed a new formal verification method for software functional correctness, which can be used to verify refactoring. The regression test suite proposed by Silva et al. (2017) can 

```
1 3
```

Empirical Software Engineering          (2026) 31:178 

<mark>Page 5 of 41 178</mark> 

also be used for consistency checks before and after refactoring. Dao et al. (2017) proposed a behavior consistency checking tool for model refactoring. Based on symbolic interpretation, Abadi et al. (2019) detected the functional equivalence between original and refactored code by comparing paths and output variables under all possible input scenarios. In the field of refactoring consistency detection for concurrent programs, Zhang et al. (2021) proposed a fine-grained lock refactoring consistency verification method to address the behavioral changes of concurrent programs during the refactoring from coarse-grained locks to fine-grained locks. By analyzing the potential causes of inconsistent behavioral changes in concurrent programs resulting from current refactoring, Schäfer et al. (2010) proposed a behavior-preserving technique for concurrent programs to solve this problem. However, these methods are designed for traditional refactoring approaches and are not adaptable to the consistency issues of large language model (LLM)-based refactoring. 

### **2.3 LLM-Based Code Refactoring** 

In recent years, LLMs have developed rapidly domestically and internationally, and their application potential in software engineering, especially in code refactoring, has been widely explored by researchers. A growing body of empirical studies has focused on evaluating the effectiveness and limitations of LLMs in automated code refactoring. For example, Cordeiro et al. (2024) conducted a large-scale empirical study to systematically evaluate the code refactoring capability of multiple mainstream LLMs, measuring their performance in code quality improvement, code smell reduction, and functional preservation across diverse code scenarios and programming languages. Liu et al. (2025) conducted a comprehensive empirical study to explore the potential of general-purpose LLMs in automated software refactoring, providing quantitative insights into the performance of LLMs on different refactoring tasks and code types. Similarly, DePalma et al. (2024) also explored the capabilities and limitations of ChatGPT in code refactoring, revealing its effectiveness and shortcomings on Java code segments through empirical research. In addition, Cordeiro et al. (2025) systematically summarized the opportunities and limitations of LLM-driven code refactoring, highlighting critical challenges such as the generation of semantically incorrect (hallucinatory) code, insufficient understanding of large-scale cross-module codebases, and lack of explicit refactoring intent comprehension. 

Beyond these empirical and position studies, existing research has also explored practical strategies to enhance LLMs performance in refactoring. AlOmar et al. (2025) specifically focused on ChatGPT for code refactoring, analyzing key topics, interaction patterns, and effective prompting strategies to improve the quality of LLM-generated refactoring solutions. White et al. (2024) proposed a catalog of prompting patterns for software engineering activities represented by ChatGPT, and provided six prompting patterns specifically tailored for code refactoring tasks. Ma et al. (2023) evaluated ChatGPT’s ability to interact with code segments, focusing on its understanding of semantic structures and code syntax, requiring the AI to analyze call graphs, control flow graphs (CFG), and abstract syntax trees (AST). Additionally, Shirafuji et al. (2023) enhanced prompting strategies by incorporating code refactoring examples, proving the potential of LLMs in supporting code refactoring and improving program complexity. Zhang et al. (2025a) proposed a hybrid approach integrating deep learning with LLM-generated semantic information to address the limitations of traditional Move Method refactoring recommendation methods, which lack sufficient 

```
1 3
```

<mark>178 Page 6 of 41</mark> 

Empirical Software Engineering          (2026) 31:178 

semantic understanding; their method extracts both static coupling features and LLM-generated semantic descriptions , and uses deep neural networks to significantly improve the precision and recall of Move Method refactoring recommendations. Xu and Yang (2026) constructed SWE-Refactor, a repository-aware benchmark specifically designed for evaluating LLMs performance on real-world code refactoring; this benchmark includes 1,099 verified refactoring instances covering both atomic and composite refactoring types, providing high-quality, repository-level context to address the lack of real-world evaluation scenarios in existing LLMs refactoring research. This benchmark provides a foundational dataset for the supervised fine-tuning of LLMs on code refactoring tasks. Oueslati et al. (2025) further proposed the RefAgent framework, a multi-agent LLM-based approach for automatic software refactoring, which leverages divided labor among four specialized agents (Planner, Executor, Tester, Refiner) and an iterative self-reflection mechanism, combined with tool calls, to enhance the reliability and behavioral consistency of LLM-driven refactoring, especially in large-scale and complex refactoring scenarios. 

### **2.4 Problems in Existing Research** 

Despite the significant progress in evaluating and optimizing LLMs for code refactoring, existing studies have two critical gaps that this paper aims to address. First, while empirical studies (Cordeiro et al. 2024; Liu et al. 2025; Cordeiro et al. 2025) have identified consistency issues as a key limitation, none have conducted a systematic empirical analysis of the types, causes, and frequencies of functional inconsistencies in LLM-based refactoring. Second, optimization strategies such as prompting (White et al. 2024; AlOmar et al. 2025), hybrid deep learning (Zhang et al. 2025a), and multi-agent frameworks (Oueslati et al. 2025) focus on improving refactoring quality or automation, but do not propose targeted solutions to enhance consistency. Although existing research has demonstrated the potential of LLMs in code refactoring and software engineering applications, functional inconsistencies remain prevalent due to the uncertainty and hallucination issues of LLMs (Huang et al. 2025; Zhang et al. 2025c). Therefore, we aim to conduct an empirical study of the inconsistencies before and after LLM-based refactoring, provide practical experience for LLM-based code refactoring research, and propose a RAG-based optimization method to enhance refactoring consistency. 

## **3 Methodology** 

This section presents the research method, including research questions, the overall framework, dataset construction, prompt engineering, and the selected LLMs. 

### **3.1 Research Questions** 

To systematically analyze the behavioral inconsistencies of LLM-based code refactoring, this paper aims to address the following research questions (RQs). 

RQ1: What behavioral inconsistencies happened before and after LLM-based code refactoring? 

RQ2: To what extent do LLMs suffer from refactoring failures during code refactoring? 

```
1 3
```

Empirical Software Engineering          (2026) 31:178 

<mark>Page 7 of 41 178</mark> 

RQ3: How do these inconsistencies generate among different LLMs? 

RQ4: How does temperature affect the performance of LLMs during code refactoring? RQ5: How effective are state-of-the-art LLMs on code refactoring for the inconsistency set? 

### **3.2 Framework** 

This paper conducts empirical research on the consistency before and after code refactoring. Firstly, high-quality programs are selected from GitHub and LeetCode to construct a high-quality dataset, which contains 468 Java code segments and 544 Python code segments. Secondly, LLMs such as ChatGPT3.5/4.0, CodeLlama, and CodeGeeX are used to refactor these code segments. For the refactored code segments, we employ the method of differential testing (Gulzar et al. 2019) to detect inconsistencies between the original and refactored versions. Subsequently, we adopt the open card sorting method (Spencer 2009) to conduct detailed testing and comparison of the code with inconsistent behaviors, and classify the causes of behavioral inconsistencies in the code refactored by LLMs. Finally, to further investigate the inconsistency issues of state-of-the-art LLMs released in 2025, we construct an inconsistency set and use it to evaluate the refactoring capabilities of LLMs such as DeepSeek-V3, DeepSeek-R1, Qwen2.5-32B, and Qwen2.5-72B. Figure 1 presents the overall framework. 

To avoid conflating different failure modes and ensure the validity of empirical study about behavioral inconsistency, we first define and distinguish four kinds of failures observed in LLM-based code refactoring. 

**Syntactic/Compilation Failure** Refactored code that contains syntax errors (e.g., missing semicolons, invalid variable declarations) or fails to compile in the target language (Java/ 



**Fig. 1** Framework overview 

```
1 3
```

<mark>178 Page 8 of 41</mark> 

Empirical Software Engineering          (2026) 31:178 

Python). This category reflects LLM’s inability to generate syntactically valid code, rather than behavioral inconsistency. 

**Runtime Failure** Refactored code that compiles successfully but crashes during execution (e.g., null pointer exceptions, index out of bounds) or triggers timeouts/environmental errors (e.g., incompatible library versions). This category is unrelated to intentional behavioral changes and is attributed to runtime environment or code robustness issues. 

**Refactoring Failure** A broad category encompassing both syntactic/compilation failures and runtime failures—i.e., refactored code that cannot be executed to completion due to syntactic/runtime errors, making behavioral consistency evaluation impossible. 

**Behavioral Inconsistency** Refactored code that compiles and runs successfully, but produces differential output mismatches compared to the original code when executing the same LeetCode test cases. This category directly reflects unintended behavioral changes after refactoring, which is the core research object of this paper. 

To ensure the rigor and reliability of the empirical study, we have designed standardized experimental procedures and reliability evaluation methods, which are detailed as follows. Throughout this study, we adopt each refactored output as the standardized unit of analysis. Each original code segment in the dataset may generate multiple refactored outputs under different models, prompts, or parameter settings, and each refactored output is independently judged as behaviorally consistent or inconsistent with the original implementation. All reported overall inconsistency rates are computed as the ratio between the number of inconsistent refactored outputs and the total number of refactored outputs. For the categorization in RQ1 and RQ2, the proportion of each category is calculated over all inconsistent refactored outputs, ensuring a unified and interpretable analytical foundation across all experiments from RQ1 to RQ5. 

To systematically analyze the behavioral inconsistencies identified in subsequent experiments, we employed the open card sorting method (Abadi et al. 2019) to establish a comprehensive and reliable taxonomy of inconsistency patterns. The entire annotation process follows rigorous and auditable empirical practices widely adopted in software engineering research. We first created an independent card for each behaviorally inconsistent code segment, documenting the functional summary, original code, LLM-refactored code, compilation status, and test execution results. These cards provide complete contextual and empirical support for subsequent categorization and root-cause analysis. 

The annotation process involves two independent annotators and a senior reviewer to ensure reliability. The first annotator has more than 10 years of experience in programming and code analysis, the second annotator has over five years of expertise in program comprehension and software refactoring, and the senior reviewer, with twenty years of research experience in software engineering, supervises the entire process and resolves unreconciled discrepancies. To standardize the annotation procedure and reduce subjective bias, we developed a detailed annotation codebook that defines clear judging criteria for identifying and grouping behavioral inconsistency patterns. All annotators received unified training following this codebook before the open card-sorting task. 

```
1 3
```

Empirical Software Engineering          (2026) 31:178 

<mark>Page 9 of 41 178</mark> 

During the initial phase, the two annotators completed fully independent, unrestricted open sorting for all code cards without a predefined fixed number of categories, and no discussion or communication was allowed in this stage. After finishing the original independent labeling, we summarized, merged, and refined the clustered raw patterns and finally induced four major high-level inconsistency categories from the annotation results. To quantitatively verify the reliability of the initial open sorting before any category merging or consensus reconciliation, we calculated the Cohen’s Kappa coefficient based on the raw independent labels of the two annotators, following the established practice in empirical refactoring studies (Wang et al. 2024). This coefficient eliminates agreement caused by random guessing among clustered patterns and objectively reflects the consistency of the original classification. The overall Cohen’s Kappa reached 0.83, reflecting strong consistency between the two annotators. 

After reliability evaluation, we conducted a structured reconciliation phase, in which the two annotators reviewed and discussed conflicting raw labels to reach a unified consensus. Any remaining unresolved disputes were ultimately adjudicated by the senior reviewer to finalize the completed four-category taxonomy. The refinement of all fine-grained subcategories, including the thirteen subclasses nested within the four main high-level categories and the detailed subtypes of the independent refactoring-failure group, adopted the same annotation and card-sorting procedure, maintaining unified criteria and methodological consistency across the entire hierarchical classification system. 

### **3.3 Dataset** 

Benchmark datasets for evaluating LLM-based code refactoring remain limited (Chen et al. 2021; Du et al. 2023). DePalma et al. (2024) constructed a small refactoring dataset containing only 40 Java code segments. Although this dataset supported early research, its small scale and lack of diversity make it insufficient for evaluating modern LLMs. To address this, Fan et al. (2023) proposed the LMDefects dataset with 113 Java programming tasks. While more comprehensive, LMDefects focuses only on Java and lacks cross-language diversity. 

To expand the scale and language coverage of the dataset, we constructed a dataset _DataRef_ for code refactoring with LLMs. _DataRef_ supports Java and Python programming languages. We collected all publicly accessible hard-level programming tasks from LeetCode. By June 2024, LeetCode hosted 3,368 programming problems, including 839 easy, 1,760 medium, and 769 hard-level tasks. We focused specifically on hard-level tasks, as they typically involve more complex algorithms and data structures, presenting greater challenges and greater refactoring potential. For each problem, we selected the highest-rated user submissions as original code samples. The problems span multiple domains, including data structures, algorithms, database operations, and concurrent programming, ensuring the diversity and comprehensiveness of the dataset. To ensure fairness and accessibility, we filtered out tasks that require premium subscriptions, guaranteeing that all included tasks are public and freely accessible. Ultimately, we collected 468 Java segments and 494 Python segments from LeetCode as pre-refactoring code samples. 

To enhance dataset diversity, we incorporate the _ClassEval_ dataset (Du et al. 2023). It contains 100 class-level code generation tasks covering diverse programming scenarios and application contexts. We randomly selected 50 of these tasks and included their generated 

```
1 3
```

<mark>178 Page 10 of 41</mark> 

Empirical Software Engineering          (2026) 31:178 

code in our dataset, providing richer code examples for subsequent model evaluation. The _DataRef_ dataset includes 468 Java and 544 Python segments. 

To clearly show the composition, we provide a consolidated dataset description in Table 1. The dataset supports cross-language and multi-topic evaluation, providing a more comprehensive infrastructure for code refactoring research. It is publicly available at  h t t p s : / / u z h a n g y a n g . g i t h u b . i o / r e s e a r c h / d a t a r e f . h t m l . 

To further evaluate the refactoring capabilities of state-of-the-art LLMs released in 2025, we constructed a new dataset _DataRef+_ based on inconsistent programs. _DataRef+_ consists of all code segments with inconsistencies, with deduplication applied to inconsistent code segments generated by different models for the same original code segments—only one instance of the original code segments is retained for duplicate refactoring issues across LLMs. The final _DataRef+_ contains 272 Java segments and 297 Python segments. 

For clarity, we summarize the data usage for each research question: 

- RQ1, RQ2, RQ3, RQ4: _DataRef_ . 

- RQ5: _DataRef+_ (272 Java and 297 Python segments). 

- Evaluation of our mitigation strategy: Python code segments in _DataRef_ (297 Python segments). 

### **3.4 Prompt Engineering** 

Prompt engineering plays a crucial role in the application of LLMs. The design of prompts directly affects the output quality of the model and the effectiveness of task completion. We adopted the role-based prompting approach (Ma et al. 2023), which assigns a specific role to the LLMs and clearly defines the task context to enable the model to generate more expected outputs. The basic template for role-based prompting is as follows: 

You are [ROLE] for [LANG]. [TASK DESCRIPTION]. 

where [ROLE] specifies the model’s identity or task role, [LANG] indicates the programming language, and [TASK DESCRIPTION] clarifies the specific task the model needs to complete. This way, the model is provided with a clear task definition and necessary contextual information. 

For the task description part, we explicitly informed the model to perform behavior-preserving code refactoring to improve certain non-functional properties of the code (DePalma et al. 2024; Al Dallal and Abdin 2017) critical to distinguishing legitimate performance optimization from unintended functional changes. When selecting quality attributes, we mainly considered two common dimensions: (1) Readability and maintainability, which focus on the clarity and comprehensibility of the code. (2) Performance, which primarily involves optimizing computational performance such as code execution efficiency, memory usage, and response time, with an emphasis on improving the code’s runtime efficiency and performance without altering core algorithm logic or input/output behavior. 

To enable LLMs to handle complex tasks while accounting for their input and output token limits, we further optimized the prompt design. Specifically, to avoid unnecessary 

|**Table 1**Confgurations of<br>|Source|Java|Python|
|---|---|---|---|
|_DataRef_by source and program-<br>ming language|LeetCode<br>ClassEval|468<br>0|494<br>50|
||Total|468|544|



```
1 3
```

Empirical Software Engineering          (2026) 31:178 

<mark>Page 11 of 41 178</mark> 

natural language explanations from the model, we explicitly required it to output only the refactored code without any additional description. Most importantly, we added a clear constraint to ensure that refactoring does not alter the original functionality of the code: preserve the original functionality, input/output behavior, and boundary condition handling of the code. This design not only improves task efficiency and makes full use of the limited token space, but also eliminates ambiguity between performance-preserving refactoring and unintended behavior-altering modifications. Using these optimizations, we derived the final prompt template as follows: 

You are a senior [Java/Python] programmer. Your task is to refactor the source code to enhance (1) [readability, maintainability]/(2) [performance]. Strictly preserve the original functionality, input/output behavior, and boundary condition handling of the code. The input is: [INPUT]. No explanation is required. 

### **3.5 Large Language Models** 

We select two closed-source models, such as GPT-3.5-turbo and GPT-4o (Peng et al. 2023; Achiam et al. 2023), as well as two open-source models, such as CodeGeeX-4 (Zheng et al. 2023) and CodeLlama-70b (Roziere et al. 2023). These LLMs are accessed via API calls to refactor the code in the _DataRef_ dataset. 

For LLMs’ parameters, temperature is set to 0.1 to ensure experimental stability and the quality of generated content. This value balances a certain degree of creativity in the model’s output while avoiding excessively random or unstable results. This fixed setting is used in RQ1 and RQ2, which focus on inconsistency characterization and failure mode analysis. The max_tokens is set to 2048, limiting the maximum number of generated tokens to ensure the output length is moderate and does not exceed predetermined limits. 

In RQ4, we investigate how temperature affects inconsistency rates by testing three representative settings: 0.1, 0.6, and 0.95. All other parameters are kept unchanged to ensure a controlled comparison. 

To evaluate the refactoring capabilities of representative state-of-the-art LLMs released in 2025, we selected DeepSeek-R1/V3 (Liu et al. 2024; Guo et al. 2025) and Qwen2.532B/72B (Bai et al. 2025). Considering the stability testing requirements of these models in RQ5, temperature is set to 0, top_p is set to 1, and max_tokens is set to 2048. 

## **4 Results** 

Based on the research method and experimental design detailed in the previous section, this section presents the empirical results to address the five research questions. 

### **4.1 RQ1: Occurrences and Classification of Code Inconsistencies Before and After Refactoring** 

To address RQ1, we utilized LLMs including GPT-3.5-turbo, GPT-4o, CodeLlama-70b, and CodeGeeX-4 to refactor the 1,012 code segments in the _DataRef_ dataset. Each model refactored each code segment with two prompts as described in Section 3.4, yielding 8,096 

```
1 3
```

<mark>178 Page 12 of 41</mark> 

Empirical Software Engineering          (2026) 31:178 

refactored code versions. To detect inconsistencies in the refactored code, we adopted differential testing (Liu et al. 2019) following the procedure defined in the Method section. 

For code collected from LeetCode, we compare the outputs of the original and refactored implementations by submitting both to the LeetCode platform, which contains its complete official test cases. For code from the ClassEval subset, we use the test cases provided within the dataset. The LeetCode official test suite and ClassEval test cases together form the ground-truth test oracle in this study, covering normal inputs, boundary values, and corner cases to support comprehensive validation of behavioral consistency across both function-level and class-level code. Code that passes all predefined test cases is considered to preserve the original behavior and labeled as behaviorally consistent. Code that fails any test case and produces outputs different from the original implementation is identified as behaviorally inconsistent. 

We then used behaviorally inconsistent code refactored by GPT-3.5-turbo as representative samples covering diverse refactoring scenarios. Through repeated individual inspection, group discussion, and guideline refinement, we iteratively clustered and consolidated inconsistent code segments according to their core characteristics. After multiple rounds of verification and refinement, we derived a set of common and well-defined behavioral inconsistency patterns, forming a final taxonomy that includes variable-level, statement-level, method-level, and algorithm-level inconsistencies. 

In total, we identified 928 behaviorally inconsistent code segments. Through classification, we distinguished four major categories: variable-related inconsistency, statementrelated inconsistency, method-related inconsistency, and algorithm-related inconsistency, which are further divided into 13 fine-grained subtypes. As shown in Fig. 2, variable-related and statement-related inconsistencies together account for more than 70% of all cases, representing the two most dominant issues. This observation indicates that LLMs are most prone to introducing errors at the variable and statement levels. Algorithm-related inconsistencies represent the smallest proportion at only 11.20%, suggesting that LLMs tend to be relatively conservative when performing in-depth code modifications. 

We further elaborate on the different categories in detail. 

### **4.1.1 Variable-Related Inconsistency (37.18%)** 

LLMs frequently introduce multi-dimensional modifications during variable refactoring, but these modifications may disrupt the integrity of the original data flow, leading to functional deviations. A representative example of this category is that an LLM incorrectly modifies variable names, values, data structures, or variable scopes during variable-level refactoring while maintaining syntactic correctness of the code, resulting in normal compilation and execution but inconsistent output compared to the original program. Through manual inspection, we summarized six core inconsistency patterns: 

**Variable Renaming Inconsistent(2.05%)** To improve code readability, LLMs may perform Rename Variable refactoring. However, during the refactoring process, failures to resolve cross-scope references, misunderstandings of semantic context, or ambiguous variable name meanings may cause logical anomalies in the refactored code. Specific manifestations include: 

```
1 3
```

Empirical Software Engineering          (2026) 31:178 

<mark>Page 13 of 41 178</mark> 



**Fig. 2** Inconsistencies and their distribution 

- Partial update residue: When renaming a variable, after modifying the variable name in the preceding text, only some variable references are updated in the subsequent text. The code before and after refactoring with GPT-3.5-turbo is shown in Fig. 3. In Fig. 3(b), the refactored code renames variables to more descriptive names (Lines 6 and 7), but during calculation, _horizontalCount_ originally intended to be multiplied by the horizontal cutting cost is incorrectly used for vertical cutting cost calculation; meanwhile, _verticalCount_ is incorrectly used for horizontal cutting cost calculation. This results in a mismatch between the cost calculation logic for each cut and the original problem, ultimately leading to incorrect minimum total cost due to state transition errors. 

- Semantic conflicts: After LLMs rename a variable, the new name conflicts with other symbols in the context. For example, renaming the counter variable _i_ to _index_ conflicts with an existing _index_ object. 

**Variable Extraction Inconsistent(8.41%)** When performing Extract Variable refactoring, LLMs may fail to correctly preserve the original computational dependencies or environ- 

```
1 3
```

<mark>178 Page 14 of 41</mark> 

Empirical Software Engineering          (2026) 31:178 



**Fig. 3** Example of variable renaming inconsistency 

mental state, leading to semantic deviations in the refactored code. This may stem from an insufficient understanding of data flow and computational order during expression splitting, thereby affecting the execution of code logic. Specific manifestations are as follows: 

- Computational order dependency error: The execution order of side effects in the original expression (such as operations with state changes like file reading/writing and network requests) is not preserved when extracting variables. This order dependency issue significantly impacts the expected behavior of the program, resulting in changes to program behavior. 

- Missing capture of environmental state: The original logic is not fully retained when extracting variables. Especially when handling complex mathematical expressions or variable dependencies, LLMs may fail to correctly capture all relevant environmental information, thereby causing inconsistencies in the behavior of the refactored code. The code before and after refactoring with GPT-3.5-turbo is shown in Fig. 4. In Fig. 4(a), the pre-refactored expression is _nodes + step + 1_ (Line 3), while in Fig. 4(b), the refactored code incorrectly extracts it as _newSteps = step + 1_ (Line 3), omitting the computational logic of the _nodes_ variable and leading to inconsistency between the refactored code and the original semantics. 

**Variable Inlining Inconsistent(11.31%)** When performing Inline Variable refactoring, LLMs may fail to correctly isolate data modification operations, leading to state contamination. This state contamination typically arises from insufficient consideration of data flow and side effects during refactoring, especially when multiple operations share the same variable. 



**Fig. 4** Example of variable extraction inconsistency 

```
1 3
```

Empirical Software Engineering          (2026) 31:178 

<mark>Page 15 of 41 178</mark> 

Specific manifestations include: omitting intermediate variables and directly modifying the original data structure. The code before and after refactoring with GPT-3.5-turbo is shown in Fig. 5. In Fig. 5(a), the original code introduces an intermediate variable _g_ , modifies it, and finally assigns it to the original array (Lines 8 and 9); while in Fig. 5(b), the refactored code eliminates the intermediate variable and directly modifies the original array (Line 8), resulting in the permanent alteration of the original array state without temporary storage. 

**Data Structure Conversion Inconsistent(13.79%)** When performing Split Variable refactoring or Change Variable Type refactoring (e.g., converting arrays to lists, hash tables, etc.), LLMs may fail to correctly preserve the access patterns or dimension mapping relationships of the original data, leading to logical errors in the refactored code. Such errors typically stem from insufficient understanding of the access methods, indexing rules of the original data structure, or the implicit relationships during data conversion. When replacing data structures, failing to consider differences in access efficiency, storage methods, or indexing mechanisms between different data structures may result in program logical distortion or performance degradation. Specific manifestations are as follows: 

- Dimension compression errors: The mapping relationships of the original data dimensions are not correctly preserved when splitting variables. The refactored code attempts to flatten or reorganize the data structure, but loses the mapping relationship with the original data structure in the process. This type of dimension compression error is particularly prominent when handling complex data structures. The code before and after refactoring with GPT-3.5-turbo is shown in Fig. 6. In Fig. 6(a), the original code uses a 3D array _d[][][]_ (Line 1); while in Fig. 6(b), the refactored code flattens it into a 2D array _dp[][]_ (Line 1) and introduces an intermediate variable _newDp_ for operations (Line 6). However, the outputs of the pre-refactored and refactored codes differ in differential testing, indicating that the mapping relationships were not correctly preserved during dimension compression. 

- Access pattern conflicts: When converting arrays to other data structures, the corresponding operation methods are not updated synchronously, leading to functional abnormalities. During code refactoring, LLMs sometimes convert arrays in the original code to other types of data structures (e.g. lists, dictionaries, or sets) but fail to adjust the associated access patterns and operation methods accordingly. 



**Fig. 5** Example of inline variable inconsistency 

```
1 3
```

<mark>178 Page 16 of 41</mark> 

Empirical Software Engineering          (2026) 31:178 



**Fig. 6** Example of data structure conversion inconsistency 

**Magic Number Replacement Inconsistent(0.97%)** When performing Replace Magic Number with Symbolic Constant refactoring, LLMs may fail to accurately understand the business meaning or value range constraints behind numerical values. This situation may lead to boundary condition errors in the refactored code, especially in scenarios where numerical values have special meanings or strict restrictions. The specific manifestation is mismatched value range coverage: after LLM refactoring, _(long)1e18_ may be replaced with _Long.MAX_  VALUE_ , resulting in overflow of the large number calculation logic designed in the original code. 

**Variable Encapsulation Inconsistent(0.65%)** When performing refactoring operations such as Encapsulate Field refactoring, Replace Variable with Parameter refactoring, Replace Field with Parameter refactoring, and Add Variable Modifier refactoring, LLMs may fail to correctly handle the language’s parameter passing mechanism or variable lifecycle constraints, leading to visibility errors in the refactored code. Such issues typically stem from an insufficient understanding of the variable’s lifecycle across different scopes or incorrect handling of the parameter passing method between variables and methods. The result may be that variables are inaccessible in certain code blocks or unexpected visibility problems occur, affecting the normal implementation of functions. Specific manifestations are as follows: 

- Lifecycle disruption: When encapsulating fields, LLMs fail to fully consider the variable lifecycle. The code before and after refactoring with CodeLlama-70b is shown in Fig. 7. In Fig. 7(a), the original code’s _sumL, sizeL, L_ and _R_ are all instance variables (Lines 16-19). In Fig. 7(b), the refactored code localizes these instance variables to the interior of the _minimumCost_ method and passes them to the _l2r_ and _r2l_ methods as parameters. Since Java uses a pass-by-value mechanism, modifications to the primitive type parameters _sumL_ and _sizeL_ only affect the local copies within the method and cannot update the original variables of the caller. This results in _sizeL_ not being decremented correctly, potentially triggering an infinite loop or exceptions in subsequent code. Meanwhile, the conditional logic dependent on _sizeL_ (Line 15 in Fig. 7(b)) may execute based on 

```
1 3
```

Empirical Software Engineering          (2026) 31:178 

<mark>Page 17 of 41 178</mark> 



**Fig. 7** Example of encapsulate variable inconsistency 

an incorrect state, leading to calls to _lastKey()_ or _firstKey()_ on an empty collection and ultimately triggering a _NullPointerException_ . 

- Immutability conflict: When adding variable modifiers, LLMs attach the _final_ modifier to variables or methods but fail to synchronously correct subsequent assignment operations, resulting in immutability conflicts in the program. For example, a variable in the original code is initialized as _final_ outside a loop, but after refactoring, the LLM still reassigns it inside the loop body or other code segments due to incorrect handling of its immutability constraints. This inconsistency can cause runtime errors or, in some cases, lead to program logic that does not meet expectations. 

### **4.1.2 Statement-Related Inconsistency (36.75%)** 

LLMs’ structural modifications to code statements may disrupt the critical execution paths of programs. A representative example of this category is that an LLM deletes, reorders code statements, or optimizes loop structures during statement-level refactoring while maintaining syntactic validity of the code, resulting in normal compilation and execution but disrupted control flow and inconsistent output compared to the original program. We identified three core inconsistency patterns: 

**Dead Code Removal Inconsistent(5.61%)** When performing refactoring operations such as Remove Dead Code and Remove Thrown Exception Type, LLMs may cause program logical errors due to static analysis deviations. Such issues typically stem from failure to fully consider all possibilities of code execution paths during code analysis, or failure to correctly identify potential side effects when removing redundant code. Specific manifestations are as follows: 

- Optimization of exception handling branches: When removing dead code, LLMs may delete seemingly untriggered exception handling branches (e.g., catch(FileNotFoundException)), considering them redundant or useless; however, these 

```
1 3
```

<mark>178 Page 18 of 41</mark> 

Empirical Software Engineering          (2026) 31:178 



**Fig. 8** Example of remove dead code inconsistency 

branches are actually crucial in specific deployment environments or edge cases. 

- Redundant statement deletion: LLMs may delete code statements that do not explicitly participate in the main logic in an attempt to simplify the code. However, such a deletion can sometimes disrupt the original logic of the program, leading to functional abnormalities. The code before and after refactoring with GPT-3.5-turbo is shown in Fig. 8. In Fig. 8(b), the refactored code deletes the statement _i += 1_ (Line 11) from the original code in Fig. 8(a), resulting in abnormalities in the number of subsequent loops. 

**Statement Movement Inconsistent(3.23%)** When performing Move Field refactoring, LLMs may fail to correctly identify dependencies between statements or the order of side effects, leading to logical errors in the refactored code. Such errors typically stem from failure to accurately grasp the execution order and interactions between variables, fields, or statements—especially when side effects are present. Specific manifestations are as follows: 

- Lifecycle conflict: LLMs may move resource release operations (e.g., _file.close()_ ) ahead of the code that uses the resource. This causes subsequent operations to attempt to access the released resource, thereby triggering a NullPointerException or other types of runtime errors. 

- Side effect dependency disruption: When moving fields, LLMs may reorder statements involving I/O operations (e.g., file writing, network requests) or state modifications (e.g., variable assignments, collection changes), disrupting the original execution dependency chain. Such reordering can break the side effect dependency relationships of the code, leading to functional deviations or logical errors. The code before and after refactoring with GPT-3.5-turbo is shown in Fig. 9. In Fig. 9(b), the refactored code reverses the assignment statements for _presum_ and _prebest_ (Lines 7 and 8) from the original code in Fig. 9(a). Since the value of _prebest_ depends on the calculation result of _presum_ , subsequent logic suffers from functional deviations due to incorrect value retrieval. 

```
1 3
```

Empirical Software Engineering          (2026) 31:178 

<mark>Page 19 of 41 178</mark> 



**Fig. 9** Example of move statement inconsistency 

**Loop Optimization Inconsistent(27.91%)** When performing loop structure optimization refactoring (such as Decompose Conditional, Consolidate Duplicate Conditional Fragments, Consolidate Conditional Expression, or Replace Nested Conditional with Guard Clauses), LLMs may fail to correctly preserve the loop’s termination conditions or iterative semantics, leading to logical errors in the refactored code. Such issues typically stem from insufficient understanding of the control flow of the original loop structure—especially when conditional judgments and branch statements need to be reorganized during refactoring. Failure to accurately identify the termination conditions in the loop, state changes in the loop body, or iteration order may result in infinite loop execution, failure to trigger the termination condition, or variables in the loop not being updated as expected, thereby causing program logical errors. Specific manifestations are as follows: 

- Inaccurate termination conditions: LLMs may fail to align the termination conditions with the original logic, resulting in the program’s failure to exit normally or even issues like infinite loops. The code before and after refactoring with CodeGeeX-4 is shown in Fig. 10. In Fig. 10(b), when the refactored code simplifies the _for_ loop from the original code (Fig. 10(a)) to a _while_ loop (Line 7), it fails to synchronously update the step logic, leading to the omission of the _k++_ operation and thus triggering an infinite loop. 



**Fig. 10** Example of optimize loop inconsistency 

```
1 3
```

<mark>178 Page 20 of 41</mark> 

Empirical Software Engineering          (2026) 31:178 

- Loop semantic alienation: Due to failure to accurately simulate the execution path of the original loop, LLMs may, in some cases, result in a mismatch between the number of iterations and the original logic—even though the optimized loop structure is syntactically correct—thus causing changes in program behavior. 

### **4.1.3 Method-Related Inconsistency (14.87%)** 

LLMs’ refactoring operations on methods often ignore the implicit relationships between abstraction levels, leading to the disruption of functional integrity. A representative example of this category is that an LLM extracts, inlines, or moves methods during method-level refactoring while maintaining syntactic correctness, resulting in normal compilation and execution but disrupted contextual dependencies and inconsistent output compared to the original program. We extracted three core inconsistency patterns: 

**Extract Method Inconsistency (13.79%)** When performing Extract Method refactoring, LLMs may fail to correctly handle variable scope or over-simplify key details when simplifying complex logic. This situation may lead to loss of state updates or functional inconsistency in the refactored code. Such issues typically stem from LLMs’ incomplete understanding of code context during automated refactoring, as they may fail to fully consider variable lifecycle or scope. Specific manifestations are as follows: 

- Scope contamination: LLMs fail to correctly pass closure variables or context state, leading to scope contamination issues. The code before and after refactoring with GPT-3.5-turbo is shown in Fig. 11. In Fig. 11(b), the refactored code extracts the processing logic of the string s1 within the original loop body into an independent method 



**Fig. 11** Example of extract method inconsistency (1) 

```
1 3
```

Empirical Software Engineering          (2026) 31:178 

<mark>Page 21 of 41 178</mark> 



**Fig. 12** Example of extract method inconsistency (2) 

_processS1()_ (Line 10). However, due to the pass-by-value nature of Java’s primitive data types, modifications to the parameters _s2Index_ and _s2Count_ inside the method cannot be synchronized to the caller’s scope, while subsequent operations depend on these two variables (Line 23 in Fig. 11(a)). 

- Over-optimization trap: During Extract Method refactoring, LLMs’ over-optimization may result in excessive logic simplification, which instead disrupts the original functionality or business logic. The code before and after refactoring with CodeGeeX-4 is shown in Fig. 12. In Fig. 12(b), the refactored code extracts the two similar _f.put()_ statements into a method (Lines 6-7 in Fig. 12(a)). The extracted method considers the previous variables _x+1_ and _x_ but fails to consider the subsequent _x-1_ and _x_ , leading to functional inconsistency. 

**Inline Method Inconsistency (0.97%)** When performing Inline Method refactoring, LLMs may fail to accurately preserve the original control flow structure or contextual dependency relationships of the function. Such issues typically stem from LLMs’ insufficient understanding of the function’s inherent logic or its relationship with the external environment during code optimization or refactoring. Especially when handling complex control flows or cases dependent on external variables, LLMs may ignore certain dependencies or conditional judgments, leading to logical errors in the refactored code. Specific manifestations are as follows: 

- Control flow hijacking: LLMs may directly embed function bodies containing _return/ throw_ into call sites, disrupting the original exception handling hierarchy and leading to control flow confusion and potential errors. 

- Function semantic erosion: When inlining methods, LLMs fail to preserve the original function’s environmental dependencies, which may result in the disruption of the function’s core logic and further affect program functionality. The code before and after refactoring with GPT-4o is shown in Fig. 13. In Fig. 13(a), the original code dynamically calculates the interval midpoint via the _distanceSum_ method (Line 8), while the refactored code in Fig. 13(b) fixedly uses the right endpoint value (Line 12). This may trigger the left pointer to shift right prematurely, ultimately causing failure to correctly compute the maximum frequency solution. Such modification disrupts the core logic of 

```
1 3
```

<mark>178 Page 22 of 41</mark> 

Empirical Software Engineering          (2026) 31:178 



**Fig. 13** Example of inline method inconsistency 

the original algorithm, resulting in functional changes. 

**Move Method Inconsistency (0.11%)** When performing Move Method refactoring, LLMs may fail to fully consider the environmental differences of the target context. In particular, when a method is migrated from one class or module to another, there may be potential issues with dependencies, contextual variables, or behavioral differences. If these differences are not correctly identified and handled, the refactored code may fail to maintain its original functionality in the new environment. The specific manifestation is context migration mismatch: The code before and after refactoring with CodeGeeX-4 is shown in Fig. 14. When LLMs move methods across contexts, adaptive modifications may disrupt the semantic consistency of the original implementation, resulting in the logical inequivalence of the _insert()_ function before and after refactoring. 

### **4.1.4 Algorithm-Related Inconsistency (11.20%)** 

When LLMs perform operations on algorithms, they may fail to fully consider the adaptability of the algorithm, leading to functional abnormalities.A representative example of this category is that an LLM substitutes algorithms or modifies core algorithm logic during algorithm-level refactoring while maintaining syntactic correctness, resulting in normal compilation and execution but incorrect handling of boundary conditions or inputs and inconsistent output compared to the original program. We have summarized one core inconsistency pattern: 

**Substitute Algorithm Inconsistency(11.20%)** When performing Substitute Algorithm refactoring, LLMs may fail to fully verify the applicability or boundary conditions of the new algorithm. This may cause the refactored code to exhibit semantic deviation under specific circumstances, especially when there are differences between the new algorithm and the original one in handling boundary conditions or specific inputs. If these differences are not 

```
1 3
```

Empirical Software Engineering          (2026) 31:178 

<mark>Page 23 of 41 178</mark> 



**Fig. 14** Example of move method inconsistency 

accurately identified and handled, it may lead to functional inconsistency or unexpected behavior. Specific manifestations are as follows: 

- Built-in function misuse: When replacing custom implementations with standard library functions, input value range compatibility is not verified. A typical case is replacing a custom square root implementation with the built-in sqrt function, whose differential testing results are inconsistent. 

- Boundary condition erosion: When replacing an algorithm with a more efficient implementation, the coverage of the input space is incomplete, especially in extreme value scenarios. The code before and after refactoring with CodeLlama-70b is shown in Fig. 15. The refactored code changes from _BFS_ to _DP_ , leading to functional changes. The main reason is that _BFS_ ensures a global optimal solution through level-order traversal, while _DP_ local traversal strategy cannot handle long-distance equal-value jumps. This causes the refactored code to fail to find the global optimal solution. 

Summary of RQ1: Through manual review and open card sorting, we systematically analyzed code behavioral inconsistencies in LLM-refactored code and established a classification framework covering behavioral inconsistency and refactoring failure. Behavioral inconsistency falls into four categories: variable-related, statement-related, method-related, and algorithm-related inconsistency. Of these, variable and statement issues account for over 70%, indicating LLMs tend to introduce logical deviations when handling code details such as variable scope and statement execution order. 

### **4.2 RQ2: To What Extent do LLMs Suffer from Refactoring Failures during Code Refactoring?** 

To better understand the reliability of LLM-based code refactoring, we investigate refactoring failures as a separate and critical dimension, independent of behavioral inconsistency. In this study, we formally define refactoring failures as cases where the LLM-refactored code cannot complete execution successfully. Specifically, this includes code that fails to compile due to syntactic errors, code that compiles but crashes at runtime (e.g., exceptions, 

```
1 3
```

<mark>178 Page 24 of 41</mark> 

Empirical Software Engineering          (2026) 31:178 



**Fig. 15** Example of replace algorithm inconsistency 

out-of-bounds access, null pointer errors), code that exceeds time limits, and code that cannot produce any output due to structural defects. Unlike behavioral inconsistencies—where refactored code runs successfully but exhibits divergent output from the original—refactoring failures indicate that LLMs cannot generate syntactically or structurally valid code that can be properly executed. By analyzing the prevalence and distribution of such failures, we aim to reveal additional challenges faced by LLMs in real-world refactoring scenarios. All refactoring failure cases are excluded from the subsequent behavioral inconsistency analysis, as they cannot support valid differential testing. 

Among all refactored code instances (8,096 in total, as reported in the RQ1), we identified a total of 180 refactoring failure cases across our datasets, accounting for 2.22% of all refactored segments. To systematically analyze their root causes, we further categorized these failures into four distinct types through manual inspection and root cause analysis: Syntax Errors, Type Errors, Undefined Identifiers, Context Dependencies Inconsistent. 

We further elaborate on the different categories in detail. 

**Syntax Structure Errors (23.89%)** During code refactoring, LLMs may introduce illegal syntax forms in certain scenarios, resulting in the refactored code failing to compile or run. This often occurs when modifications to the syntax structure do not fully account for the target 

```
1 3
```

Empirical Software Engineering          (2026) 31:178 

<mark>Page 25 of 41 178</mark> 

language’s rules or constraints of specific implementations—particularly in complex code conversion processes, where LLMs may incorrectly generate expressions or structures that violate language specifications. Specific manifestations include: 

- Keyword spelling errors: Incorrect use of language-specific symbols (e.g., misusing _!_ instead of _not_ in Python), or misspelling keywords (e.g., mistyping _for_ as _of_ ). 

- Missing parentheses and indentation: Missing closing parentheses (such as _}_ or )) at the end of loops or code blocks, or confused indentation levels (common in Python). 

**Undefined Identifiers (17.78%)** When performing Extract Method or Extract Variable refactoring, LLMs may fail to correctly identify dependencies between code blocks or omit key declaration steps when splitting code segments. This can cause declarations in the preceding code to not be properly registered, while subsequent code directly invokes unregistered elements—creating a discontinuity in the code logic. Consequently, the refactored code encounters undefined identifier errors during the compilation phase. Specific manifestations include: 

- Undeclared variables: Direct referencing of variables that have not been declared in the current scope. 

- Undeclared methods: Direct invocation of methods that lack prior declaration or import statements. 

**Type Inconsistency (15.00%)** During Extract Method or Change Parameter Type refactoring, LLMs may fail to fully track the type lifecycle of variables from their declaration to usage. This limitation can prevent the correct identification of the target code’s type boundaries, leading to type-matching errors in the refactored code. Specific manifestations include: 

- Basic type assignment incompatibility: Post-refactoring assignments involving mismatched numeric type ranges (e.g., assigning a variable of type _long_ to a variable of type _int_ ). 

- Method signature conflict: When modifying a parameter type or return type, the LLMs may fail to synchronously update all locations where the method is invoked. Such omissions can lead to type mismatches during method calls, thereby causing compilation errors or runtime exceptions. The code before and after refactoring using GPT-3.5-turbo is shown in Fig. 16. In Fig. 16 (b), the refactored code changes a method (Line 17) that originally returns a _long_ type in the original code (Fig. 16 (a)) to a _void_ type (Line 12). However, the refactored code does not update all invocations of this method accordingly. At the call sites (Lines 18 and 28 in Fig. 16 (b)), the original _long_ type handling is still used, resulting in a type mismatch issue. 

**Contextual Dependency Inconsistency (43.33%)** When performing Rename Variable or Extract Method refactoring, LLMs may fail to correctly pass parameters or contextual variables—often due to incomplete tracking of cross-scope references or insufficient parsing of contextual dependencies. This leads to compilation errors in the refactored code. Specific manifestations include: 

```
1 3
```

<mark>178 Page 26 of 41</mark> 

Empirical Software Engineering          (2026) 31:178 



**Fig. 16** Example of type inconsistency 

- Inconsistent variable names: Failure to properly propagate updated variable names across the entire context during variable renaming, resulting in mismatched references to old and new variable names. 

- Cross-scope reference breakage: When extracting a method, the LLMs may fail to correctly pass necessary contextual variables (such as class member variables or method parameters). This causes the refactored code to be unable to access data properly due to missing dependencies. The code before and after refactoring using GPT-3.5-turbo is shown in Fig. 17. In Fig. 17 (a), the original code uses nested _for_ loops to calculate the _order_ variable (Line 9); in Fig. 17 (b), the refactored code extracts a new _findIndex_ method (Line 15) to simplify the nested _for_ loops, but fails to pass the _used_ array as a parameter to this method. Since the _findIndex_ method cannot access the _used_ array, a compilation error occurs. Such errors typically arise when transferring dependencies across methods or scopes, where essential contextual information is not effectively passed. 

Summary of RQ2: RQ2 investigates the extent of refactoring failures in LLM-based code refactoring, identifying 180 failure cases in total. These failures are categorized into four types, with contextual dependency inconsistency (43.33%) being the most prominent, followed by syntax structure errors, undefined identifiers, and type inconsistency. All refactoring failure cases were excluded from behavioral inconsistency analysis to avoid conflation, highlighting LLMs’ key limitations in generating executable, structurally valid code. 

### **4.3 RQ3: Comparison of LLMs’ Code Refactoring Consistency** 

To address RQ3, we compared the refactoring performance of four base LLMs using the established inconsistency classification framework, with results presented in Fig. 18. The results show that variable and statement-related inconsistencies are the most prevalent across all models, followed by method-related inconsistencies and refactoring failures, 

```
1 3
```

Empirical Software Engineering          (2026) 31:178 

<mark>Page 27 of 41 178</mark> 



**Fig. 17** Example of contextual dependency inconsistency 

while algorithm-related inconsistencies occur relatively rarely. This phenomenon underscores that refactoring operations involving variable declaration, assignment, and code structure organization are more error-prone. Furthermore, we found that CodeGeeX-4 exhibits a significantly higher incidence of variable-related inconsistencies (166 segments), which is 3.3 times greater than that of GPT-4o (50 segments) and 4.7 times greater than that of CodeLlama-70b (35 segments). In contrast, GPT-4o and CodeLlama-70b demonstrate a notably lower frequency of such inconsistencies compared to the other models. This highlights variations among models in managing code structure and variables.Notably, GPT-4o (177 total segments) and CodeLlama-70b (124 total segments) achieved the best post-refactoring consistency, with the lowest frequency of pre- and post-refactoring behavioral inconsistencies. These variations may be closely linked to factors including model parameter scale and the size and quality of training datasets. For example, both GPT-4o and GPT-3.5-turbo are trained on mixed corpora with substantial code and text data, but GPT4o’s larger parameter scale enables higher accuracy and consistency in code understanding and generation. In contrast, CodeLlama-70b is primarily trained on code-specific datasets 

```
1 3
```

<mark>178 Page 28 of 41</mark> 

Empirical Software Engineering          (2026) 31:178 



**Fig. 18** Distribution of inconsistencies across different LLMs 

and features a relatively large parameter count, thereby delivering stable and reliable performance in programming tasks and ranking among the top-performing models. 

However, despite CodeLlama-70b performing the best in terms of post-refactoring functional consistency, it is more conservative in modifying refactored code, resulting in fewer changes. To gain a deeper understanding of this phenomenon, we further measured the average lines of code (LOC), number of characters (Chars), and cyclomatic complexity (CC) before and after refactoring. Among these, LOC refers to the number of code lines, including blank lines and comment lines; Chars represents the total number of characters in the program, a metric that is significantly affected by longer tokens and can reflect the original length of the program; CC is a software metric for measuring program complexity (McCabe 1976). CC increases with the number of if branches, for loops, and their nesting. A smaller CC is preferred, and a CC< 10 is classified as low risk in software development. The results are shown in Table 2. The measurements indicate that compared to GPT-4o, CodeLlama-70b makes fewer modifications to the code after refactoring, while the number of inconsistencies between the two models is comparable. This finding suggests that in practical applications, when selecting an appropriate LLM for code refactoring, one can decide based on specific needs—whether to prioritize models with fewer post-refactoring code modifications or to focus more on models with better behavioral consistency before and after refactoring. 

Summary of RQ3: We compared four LLMs’ inconsistency performance in code refactoring. Results show GPT-4o and CodeLlama-70b have the fewest inconsistencies, with both performing well; GPT-4o in particular demonstrates deeper, more effective code 

**Table 2** Average quality information of each LLMs before and after code refactoring 

|Metrics|Origi-|GPT-3.5-turbo|GPT-4o|Code-|CodeL-|
|---|---|---|---|---|---|
||nal<br>Code|||GeeX-4|lama-<br>70b|
|LOC|23.95|30.71|29.64|28.37|24.46|
|Chars|887.75|1362.15|1293.62|1042.20|959.71|
|CC|14.26|13.61|13.47|14.01|13.83|



```
1 3
```

Empirical Software Engineering          (2026) 31:178 

<mark>Page 29 of 41 178</mark> 

adjustments before and after refactoring. While CodeLlama-70b also has strong refactoring capabilities, its code modification depth and breadth are notably inferior to GPT-4o. CodeGeeX-4, by contrast, has the most inconsistencies and performs mediocrely in refactoring tasks. 

### **4.4 RQ4: The Impact of LLMs Temperature on Refactoring Inconsistencies** 

To address RQ4, we investigate whether varying temperature introduces new inconsistency types beyond those identified in RQ1 and RQ2, and how temperature affects the frequency of existing inconsistencies. In our main experiments for RQ1 and RQ2, we used a fixed temperature = 0.1 for all models to minimize randomness and ensure deterministic, stable refactoring outputs, which is a standard setting for evaluating consistency in code generation tasks. For RQ4 specifically, we perform a controlled parameter study to isolate the impact of temperature: we keep the prompt template fixed (Strategy in Section 2.4), use CodeGeeX-4 (the most unstable model in RQ3), and test three levels of temperature: 0.1 (low/randomness fixed), 0.6 (moderate), and 0.95 (high). For each temperature setting, we refactored code segments from the _DataRef_ dataset and generated 2024 refactored code segments per temperature to ensure statistical reliability. Since each code segment was refactored only once per condition, we report 95% Wilson confidence intervals (CIs) for all inconsistency frequencies and error rates to quantify statistical uncertainty. The inconsistencies observed at each temperature are shown in Fig. 19. 

The experimental results demonstrate that no new error types outside the RQ1 and RQ2 classification system emerged under all temperature conditions, validating the completeness of the four inconsistency patterns and refactoring failure category. Additionally, high temperature (0.95) significantly exacerbated variable-related inconsistencies (211 segments, an increase of 26.3% relative to 167 segments at 0.1, on DataRef with CodeGeeX-4) and method-related inconsistencies (68 segments, an increase of 33.3% relative to 51 segments 



**Fig. 19** Inconsistencies of CodeGeeX-4 across different temperature settings 

```
1 3
```

<mark>178 Page 30 of 41</mark> 

Empirical Software Engineering          (2026) 31:178 

at 0.1). The 95% Wilson confidence intervals for these inconsistency counts do not overlap between temperature 0.1 and 0.95, confirming that the observed increases are statistically robust and not caused by random sampling variation. This pattern reflects that increased randomness leads to decreased consistency of contextual identifiers. Although the overall performance was optimal at low temperature (0.1) with a total of 483 errors, refactoring failure issues (73 segments) did not improve significantly, with overlapping 95% CIs across temperature conditions, indicating that syntax errors are less sensitive to temperature changes. 

The total error rate was the lowest at 0.1 (23.8%, 483 / 2024 refactored code segments in DataRef), with a 95% Wilson confidence interval of [22.0%, 25.7%], while the highest was at 0.95 (27.3%, 552 / 2024), with a 95% Wilson confidence interval of [25.4%, 29.3%]. The intervals exhibit slight overlap at the boundary, yet the overall separation and consistent rising tendency confirm that higher temperature is associated with an elevated error rate in refactored code. This result further verifies that reducing randomness helps improve refactoring stability, but it also limits the exploration space for code diversity. 

Summary of RQ4: The temperature parameter primarily regulates the occurrence incidence of existing inconsistency types, rather than inducing new types of inconsistency patterns. Experimental results confirm that lower temperature leads to higher refactoring consistency, while higher temperature tends to increase the frequency of variable-related and method-related inconsistencies. These findings highlight that controlling randomness is critical for ensuring the stability of LLM-based code refactoring. 

### **4.5 RQ5: Performance of State-of-the-Art LLMs in Code Refactoring Tasks (2025)** 

To address RQ5, we first conduct benchmark testing on _DataRef+_ refactoring with four representative state-of-the-art LLMs released in 2025, namely DeepSeek-R1, DeepSeek-V3, Qwen2.5-32B, and Qwen2.5-72B. Based on the benchmark results, we select the optimal LLM for parameter optimization experiments to identify the optimal parameters (temperature and top_p). RQ5 utilizes the _DataRef+_ inconsistency dataset, which includes 272 Java segments and 297 Python segments, and adopts Prompt Template (1) from Section 3.4 to evaluate the cross-lingual refactoring capabilities of DeepSeek-R1, DeepSeek-V3, Qwen2.5-32B, and Qwen2.5-72B. The experimental results are presented in Table 3. 

To quantify statistical uncertainty in the count of inconsistent segments across different SOTA models, we calculated 95% Wilson confidence intervals (CIs) for all reported inconsistency proportions, ensuring the observed performance gaps are not erroneously attributed to random sampling variation. Experimental results indicate that DeepSeek-V3 achieves the best overall performance, with only 22 total inconsistent code segments and an error rate as low as 3.03% (9/297, 95% Wilson CI [1.5%, 5.0%]) in Python scenarios—exhibiting superior performance compared to other models. Notably, there is no positive correlation between model parameter scale and refactoring capability, as illustrated by the fact that Qwen2.5-72B (72B parameter version) has more total inconsistent segments than its 32B counterpart. Given DeepSeek-V3’s stability and excellent performance, subsequent experiments focus on this model for parameter optimization research. 

We conducted parameter optimization experiments to investigate the impact of temperature on refactoring quality. We selected 297 Python code segments from _DataRef+_ as test samples, as Python facilitates straightforward metric collection in evaluations. All experiments were performed using the DeepSeek-V3 model with the two prompt templates pre- 

```
1 3
```

Empirical Software Engineering          (2026) 31:178 

<mark>Page 31 of 41 178</mark> 

|**Table 3**Number of inconsisten-<br>cies in code refactoring tasks for<br>|Model Name|Number of in-<br>consistent in Java|Number of incon-<br>sistent in Python|Total|
|---|---|---|---|---|
|representative state-of-the-art<br>||Code|Code||
|LLMs released in 2025|DeepSeek-R1|8|15|23|
||DeepSeek-V3|13|9|22|
||Qwen2.5-32B|15|10|25|
||Qwen2.5-72B|15|14|29|



sented in Section 3.4. We fixed the nucleus sampling parameter top_p=1 and conducted refactoring experiments within the temperature parameter range [0, 0.2, 0.4, 0.6, 0.8]. In addition to considering the number of inconsistencies after refactoring, we also took into account LOC, Chars, and CC mentioned in RQ3. Furthermore, we measured the Pylint score and CodeBLEU of the refactored code. Pylint is an analysis tool for evaluating Python code quality; through multi-faceted checks on the code, it provides a quality score ranging from 0 to 10, allowing developers to gauge the quality level of their code. CodeBLEU is an automatic evaluation method for code generation (Ren et al. 2020), which integrates the advantages of BLEU in n-gram matching, further incorporates code syntax through abstract syntax trees, and integrates code semantics through data flow. The final results are presented in Table 4. 

All continuous metrics in Table 4 represent the averaged results of two independent prompt designs for each code sample. Since the two prompts serve as distinct generation strategies rather than repeated experimental trials, traditional sample-based confidence intervals are statistically inappropriate for LOC, Chars, CC, Pylint score, and CodeBLEU. We only apply rigorous 95% Wilson CIs to quantify uncertainty for the proportion of inconsistent segments. The results show that LOC and character counts remain stable across all temperature settings with negligible fluctuations. The Pylint score peaks at 4.76 under temperature 0.4, indicating a notable improvement in overall code quality after refactoring. The count of inconsistent segments presents a clear trend with increasing temperature: 36 inconsistencies at 0 (12.1%, 95% Wilson CI [8.6%, 16.2%]), 37 at 0.2 (12.5%, 95% Wilson CI [8.9%, 16.7%]), 32 at 0.4 (10.8%, 95% Wilson CI [7.6%, 15.0%]), 39 at 0.6 (13.1%, 95% Wilson CI [9.6%, 17.3%]), and 41 at 0.8 (13.8%, 95% Wilson CI [10.3%, 18.1%]). Although the Wilson CIs overlap between adjacent temperature groups, the consistent upward trend verifies that higher temperature introduces greater randomness and semantic instability, increasing refactoring errors. Temperature 0.4 achieves the optimal comprehensive performance: it yields the minimal number of inconsistent segments (32) and the highest CodeBLEU score (0.6226). Meanwhile, it reduces cyclomatic complexity by 2.8 

**Table 4** Code refactoring metrics for DeepSeek-V3 on Python segments from DataRef+ across different temperature settings (top_p=1) 

|Metrics|Original Code|T = 0|T = 0.2|T = 0.4|T = 0.6|T = 0.8|
|---|---|---|---|---|---|---|
|LOC (Lines of Code)|24.35|24.61|24.54|24.56|24.54|24.51|
|Chars (Character Count)|898.99|954.04|951.26|951.72|949.67|949.59|
|CC (Cyclomatic Complexity)|14.27|13.99|13.93|13.88|13.93|13.93|
|Pylint Score (0-10)|2.17|4.67|4.73|4.76|4.62|4.74|
|CodeBLEU (0-1)|–|0.6199|0.6175|0.6226|0.6197|0.6219|
|Number of Inconsistencies|–|36|37|32|39|41|



_Note:_ Number of inconsistencies include both behavioral inconsistencies and refactoring failures; all temperature experiments fix top_p=1; T represents temperature 

```
1 3
```

<mark>178 Page 32 of 41</mark> 

Empirical Software Engineering          (2026) 31:178 

percentage points (from 14.27 to 13.88) and improves the Pylint score by a relative increase of 119% compared with the original code. 

We further investigate the impact of the nucleus sampling parameter top_p on refactoring performance. All experiments are conducted using the DeepSeek-V3 model, adopting the same 297 Python code segments from _DataRef+_ , the two prompt templates in Section 3.4, and the evaluation metrics described above. We fix the temperature at 0 and test top_p values of [1, 0.75, 0.5, 0.25]. The results are presented in Table 5. 

Similarly, continuous metrics are averaged over two prompt strategies, and only 95% Wilson CIs are adopted for inconsistency proportions. LOC and Chars maintain stability across all top_p configurations. When top_p decreases to 0.5, inconsistent segments rise to 41 (13.8%, 95% Wilson CI [10.3%, 18.1%]); when top_p further drops to 0.25, the number increases to 48 (16.2%, 95% Wilson CI [12.3%, 21.0%]). Despite overlapping CIs between neighboring groups, the obvious rising trend proves that overly strict nucleus sampling truncates critical semantic tokens and degrades refactoring accuracy. 

It is particularly worth noting that although both temperature=0 and top_p approaching 0 (e.g., 0.25) narrow the token selection range, their mechanisms differ fundamentally: temperature=0 adopts greedy selection of the single token with the highest probability, only smoothing the probability distribution without changing the candidate token set; top_p approaching 0 retains only a minimal subset of tokens whose probabilities accumulate to the threshold. When this subset does not include key semantic tokens, the latter’s risk of inconsistency also increases. When top_p=0.75, the CodeBLEU score increases by 1.15% (from 0.6199 to 0.6270) and the number of inconsistent segments remains consistent with the baseline (top_p=1, 36 inconsistencies, 95% Wilson CI [8.6%, 16.2%]), indicating this setting balances generation quality and consistency effectively. 

Summary of RQ5: From model benchmarking and parameter optimization experiments, DeepSeek-V3 achieves the best refactoring performance among the four representative stateof-the-art LLMs, followed by DeepSeek-R1. Parameter tuning for DeepSeek-V3 reveals: with top_p fixed, a temperature of 0.4 delivers optimal refactoring results; with temperature fixed, top_p to 0.75 effectively balances generation quality and error rate. Notably, in dual-prompt template testing, DeepSeek-V3 still has 36 inconsistent Python code segments, corresponding to an inconsistency rate of 6.06% (36/(297 _×_ 2)). Overall, while the state-ofthe-art LLMs still face inconsistency issues, they have improved significantly compared to earlier versions and mitigated previous shortcomings to some extent, thus providing strong empirical support for optimizing LLMs parameter configurations in code refactoring tasks. 

**Table 5** Code refactoring metrics for DeepSeek-V3 on Python segments from DataRef+ across different top_p settings (temperature=0) 

_Note:_ Number of inconsistencies include both behavioral inconsistencies and refactoring failures; all top_p experiments fix temperature=0; p represents top_p 

|Metrics|Origi-<br>nal<br>Code|p = 1|p =<br>0.75|p = 0.5|p =<br>0.25|
|---|---|---|---|---|---|
|LOC (Lines of Code)|24.35|24.61|24.52|24.53|24.54|
|Chars (Character<br>Count)|898.99|954.04|952.58|951.01|951.68|
|CC (Cyclomatic|14.27|13.99|13.84|13.85|13.97|
|Complexity)||||||
|Pylint Score (0-10)|2.17|4.67|4.69|4.67|4.67|
|CodeBLEU (0-1)|–|0.6199|0.6270|0.6146|0.6193|
|Number of<br>Inconsistencies|–|36|36|41|48|



```
1 3
```

Empirical Software Engineering          (2026) 31:178 

<mark>Page 33 of 41 178</mark> 

## **5 Mitigation Method** 

This section introduces the motivation and methods of refactoring inconsistency mitigation strategies and evaluates them. 

### **5.1 Motivation** 

The reasons for the inconsistent code behavior of LLMs before and after refactoring can be attributed to three main factors in the reasoning phase: inaccurate understanding of task requirements (e.g., the Replace Algorithm Inconsistency shown in Fig. 15, where LLMs lack understanding of refactoring and make significant changes to the original code leading to functional abnormalities), lack of relevant knowledge support (e.g., inconsistent data structure conversion in variable-related inconsistencies, where LLMs invoke incorrect methods due to insufficient knowledge when converting to more efficient data structures), and inadequate understanding of context (e.g., LLMs fail to properly consider contextual conditions when extracting methods, resulting in functional abnormalities). These limitations pose significant challenges to LLM-based code refactoring in practical development environments. 

Inspired by Zhang et al. (2023), we investigate the feasibility of integrating RAG with a structured few-shot prompt. Structured prompts can describe task requirements more accurately (Li et al. 2025), while few-shot techniques (Shirafuji et al. 2023) provide LLMs with task-related facts and knowledge. Additionally, recent studies have demonstrated the use of RAG approaches to address such context-aware issues (Zhang et al. 2023). 

### **5.2 Integrating RAG and Structured Few-Shot Prompt** 

To effectively integrate RAG, we construct a corpus named _ERROR_DB_ , which covers 30 carefully selected typical cases. Each case is encapsulated in JSON format, including the original code to be refactored, failed refactoring results from at least two LLMs along with analysis of error causes (failed_refactors), the human-corrected refactored version (gold_ standard), error type, and refactoring type. This corpus also serves as a sample library for few-shot prompts, providing data support for model training and prompt generation. 

During the retrieval process, both text similarity and structural similarity are used to measure the similarity between text data. For specific implementation, text similarity is calculated first. The code to be refactored and the code in the ERROR_DB library are converted into TF-IDF vectors, and their cosine similarity is also calculated. For structural similarity, the source code is parsed by constructing an abstract syntax tree (AST). By traversing the AST, two types of features are extracted. One is a set of features containing the type and name of each node, and the other is numerical weighted scores. Specifically, the occurrences of three core node types (variables, functions, and loops) in the AST are counted respectively, and weighted scores are calculated to quantify the intensity of different structural dimensions. Higher weights are assigned to error-prone key elements in LLMs refactoring, such as variable definitions, function calls, and loop logic, thereby generating feature vectors with stronger semantic representativeness. For set-based features, the Jaccard similarity is used to calculate AST similarity. For the similarity of numerical scores, the inverse of relative differences is applied to calculate the similarity for the weighted scores of the 

```
1 3
```

<mark>178 Page 34 of 41</mark> 

Empirical Software Engineering          (2026) 31:178 

three node types (variables, loops, and functions), respectively. Finally, the mean value is computed to obtain the overall structural similarity. The linear combination of text similarity and structural similarity determines the final similarity. After calculating the similarity, the top three cases sorted by score are selected as prompt samples for LLMs’ few-shot learning. 

Based on the selected few-shot cases, we designed a set of standardized structured prompt templates. This prompt template includes role setting, refactoring requirements, refactoring steps, refactoring objectives, error pattern warnings, and output requirements. The error pattern warnings take the role of the few-shot cases we selected. The template integrates case and task requirements to form a complete prompt input, enabling LLMs to fully utilize the retrieved case knowledge and complete accurate code refactoring tasks while meeting task constraints. 

### **5.3 Evaluation** 

We selected Python code from the dataset _DataRef+_ (297 segments total) and employed GPT-3.5-turbo to evaluate the effectiveness of our method. We compared the results of LLM-refactored code using basic prompting, structured prompting, Chain-of-Thought (CoT) prompting, the traditional RAG method, and our structured + Few-shot prompting (combined with retrieval-augmented generation), respectively. To evaluate the correctness of the refactored code, we adopted the test case-based differential testing method (consistent with RQ1-RQ5 evaluation protocols). This section presents preliminary exploratory experiments to intuitively compare the performance of different prompting strategies. Since each configuration adopts single-round generation without repeated sampling, we focus on illustrating the overall performance trends and quantitative differences, rather than introducing statistical confidence intervals. 

The experimental results are shown in Table 6. Among 297 Python code segments from DataRef+, the basic prompt generates 51 inconsistent segments (17.17%), structured prompt results in 33 inconsistent segments (11.11%), and chain-of-thought prompt yields 32 inconsistent segments (10.77%). The traditional RAG method produces 37 inconsistent segments (12.46%). In contrast, our structured few-shot prompt combined with retrievalaugmented generation generates only 14 inconsistent segments (4.71%). Compared with the basic prompt, our method reduces the inconsistency rate by 12.46 percentage points (p.p.) (from 17.17% to 4.71%), a relative reduction of 72.6% in inconsistency rate. These results are promising and provide initial validation that retrieval-augmented, structured few-shot prompting can help mitigate behavioral inconsistencies in LLM-based code refactoring. 

**Table 6** Code inconsistency rates for GPT-3.5-turbo on Python segments from DataRef+ under different prompt types 

_Note:_ Counts include both behavioral inconsistencies and refactoring failures detected by test-case-based differential testing 

|Prompt type|Number of<br>inconsistent<br>segments|Total code<br>segments|Incon-<br>sisten-<br>cy ratio<br>(%)|
|---|---|---|---|
|Basic prompt|51|297|17.17|
|Structured prompt|33|297|11.11|
|Chain-of-thought prompt|32|297|10.77|
|Traditional RAG|37|297|12.46|
|Structured + Few-shot<br>prompt|14|297|4.71|



```
1 3
```

Empirical Software Engineering          (2026) 31:178 

<mark>Page 35 of 41 178</mark> 

As this evaluation is limited to GPT-3.5-turbo, Python code, and single-round generation, further investigation on broader models, languages, and generation settings is needed to confirm the generalizability of these observations. 

## **6 Discussion and Limitations** 

We conducted a systematic study on the consistency of code refactoring, summarizing refactoring inconsistency patterns across different levels, including variables, statements, methods, and algorithms, but did not cover higher-dimensional architectural-level refactoring. To explore potential inconsistencies in architectural-level refactoring, we investigated the consistency performance and behavioral characteristics of LLMs in architectural-level refactoring tasks through experiments. The experiments collected 20 cases containing architectural-level code smells, covering various scenarios such as parallel inheritance hierarchies, inappropriate intimacy, and refusal of inheritance, which are significantly distinct from the original dataset. The experiments adopted the prompt template from Section 3.4 and used GPT-3.5-turbo and GPT-4o for testing. 

The experimental results show two trends. On the one hand, in terms of consistent performance, among the 40 architectural cases refactored by GPT-3.5-turbo and GPT-4o, respectively, only 1 functional inconsistency error occurred. Analysis revealed that this error type is context-dependent inconsistency, which belongs to the inconsistency patterns summarized earlier. Additionally, no new architecture-specific patterns were found, indicating that the functional errors of LLMs in architectural-level refactoring are essentially extensions of insufficient semantic understanding, and the existing classification framework can cover architectural-level inconsistencies. On the other hand, regarding architectural-level refactoring behavior, we found that LLMs exhibit a pronounced tendency toward local optimization. In class-level refactoring, the models do not actively create new classes to split overloaded responsibilities—they only occasionally create simple classes for data encapsulation or delete redundant classes, contributing little to the core adjustment of class responsibility boundaries. More critically, their refactoring solutions suffer from the contradiction of local fixes but global imbalance. For example, when deleting direct module dependencies to reduce coupling, new dependencies between other modules are introduced due to the failure to redesign the interface adaptation logic. This contradiction may stem from LLMs’ superficial recognition of architectural design principles, in that the models can identify textual descriptions of principles such as low coupling and high cohesion, but cannot systematically balance the impact of refactoring on the overall architecture. 

Based on the above findings, we do not include the 20 architectural-level cases in the original _DataRef_ dataset. The main reason is that the consistency verification of the existing dataset relies on test case-driven differential testing, which primarily evaluates functional consistency. In contrast, the core of architectural-level refactoring requires not only the evaluation of functional consistency but also the use of architectural evaluation metrics and tools. Furthermore, the current sample size of architectural-level cases is too small, and there is a lack of industry-relevant cases, which provides limited support for empirical research. We will further supplement and improve research on architectural-level cases in future work. 

```
1 3
```

<mark>178 Page 36 of 41</mark> 

Empirical Software Engineering          (2026) 31:178 

After analyzing the supplementary experiments on architectural-level refactoring and summarizing the extended findings, we clarify the inherent limitations of this study for transparency and future research reference: 

Firstly, our evaluation only considers retrieval-augmented generation (RAG) and prompt engineering strategies for reducing code inconsistencies. We do not evaluate supervised fine-tuning (SFT), which is a common and effective technique for improving the reliability of LLMs outputs. Since SFT could serve as a strong alternative or complement to RAG for mitigating refactoring errors, future work will compare with SFT-based methods and explore hybrid approaches that combine fine-tuning and retrieval. 

Secondly, all our experiments are conducted on code segments from programming competition problems (LeetCode) and class-level examples (ClassEval). While these cover common programming patterns and basic object-oriented structures, they may not fully represent complex industrial software systems with long-term maintenance, large-scale architecture, and domain-specific business logic. Thirdly, although we include architecturelevel and class-level code (e.g., from the ClassEval dataset) in our evaluation to examine broader structural consistency, we did not observe class-level or project-level inconsistency issues within the scope of our experiments. This may be due to the scope of our datasets and the context constraints of current LLMs. Thus, the generalizability of our findings to large-scale, multi-class, and multi-file software systems remains to be further validated in future work. 

Finally, our test oracle relies on the official LeetCode test cases, which provide a reliable and consistent evaluation benchmark. However, manual execution is required due to platform access restrictions, which limits full automation of the evaluation pipeline. 

## **7 Threats to Validity** 

This section discusses external validity, internal validity, and conclusion validity. 

### **7.1 External Validity** 

Threats to external validity mainly relate to the generalizability of our research findings. Our study is based on datasets of difficult programming tasks from LeetCode and the _ClassEval_ dataset. These tasks may not represent all possible code refactoring tasks encountered in real-world software development, such as changes to cross-module inheritance hierarchies or dependency management issues in large codebases. Additionally, our research focuses primarily on two popular programming languages—Java and Python—so our findings may not be directly applicable to other programming languages. To mitigate these threats, future work can incorporate refactoring tasks from various sources and different programming languages, and consider different types of software projects to expand our dataset. Another potential threat is that we only selected 8 LLMs. However, we chose well-known models such as ChatGPT and representative professional code-focused LLMs. 

```
1 3
```

Empirical Software Engineering          (2026) 31:178 

<mark>Page 37 of 41 178</mark> 

### **7.2 Internal Validity** 

Threats to internal validity mainly relate to our manual analysis of inconsistent programs and the classification of inconsistency causes. To mitigate this threat, we conducted discussions between two annotators to resolve discrepancies, and each category was assigned a mutually agreed-upon label. Additionally, to ensure the consistency of our research findings, one author reviewed all labeled data. 

### **7.3 Conclusion Validity** 

Threats to conclusion validity are related to the selection of our evaluation metrics. We employ the Pass@1 metric, under which a program is deemed functionally correct if it passes all test cases, and a potential threat arises from the incompleteness of the test suite, which may lead to overlooked program errors. To mitigate this threat, we utilized the full official test suite from LeetCode (including both public sample test cases and hidden test cases) as the ground-truth test oracle in our experiments; these test suites are officially designed by LeetCode to validate program correctness and cover normal inputs, boundary values, and corner cases to maximize test coverage and reduce the risk of incomplete validation. Notably, automated access to LeetCode’s hidden test cases is restricted by platform policies, so all test execution and result comparison were performed manually by submitting code to the LeetCode platform following a standardized process to ensure consistency across all code segments. To further address reproducibility threats (a key concern for experimental validity), we have made our full dataset (DataRef and DataRef+) publicly available, including the unique LeetCode problem IDs for each code segment, so that other researchers can fully reproduce our experimental results by submitting code to the LeetCode platform even without automated test access. Another potential threat to conclusion validity stems from the variability of LLM outputs caused by different prompts—prompt engineering can significantly influence output quality—and to mitigate this threat, we adopted the prompt template proposed by Ma et al. (2023) to ensure the reliability of our results. 

A final potential threat to conclusion validity relates to the statistical treatment of our paired experimental comparisons. All evaluations compare the same code segments across different models, temperature and top-p configurations, and prompting strategies, forming a paired design that reduces interference from code diversity. For the core binary inconsistency ratios in our main experiments, we adopt 95% Wilson confidence intervals to quantify sampling uncertainty for interpretable statistical reference. However, formal paired significance tests are not conducted in this work. In addition, several preliminary exploratory ablation analyses only report raw counts, proportional values, and relative trend descriptions, without supplementary confidence interval calibration or rigorous hypothesis testing. Notably, the two prompts serve as distinct generation strategies rather than independent repeated trials, making sample-based t-distribution confidence intervals statistically inappropriate. Thus, we only adopt rigorous Wilson confidence intervals for binomial inconsistency rates, which conform to the actual experimental design. This choice aligns with common practice in empirical software engineering for ensuring interpretability and transparency when overall effect sizes and trends are sufficiently evident. 

```
1 3
```

<mark>178 Page 38 of 41</mark> 

Empirical Software Engineering          (2026) 31:178 

## **8 Conclusions** 

This paper presents a systematic empirical study on behavioral inconsistencies in LLMbased code refactoring. First, we constructed the _DataRef_ dataset and performed refactoring experiments using mainstream models including GPT-3.5/4, CodeLlama, and CodeGeeX, yielding 8,096 refactored code segments. Among them, 928 segments present behavioral inconsistencies relative to the original code, and another 180 cases are identified as refactoring failures caused by compilation, runtime, type, and dependency errors. By analyzing the root causes of these inconsistent cases, we established a comprehensive inconsistency taxonomy covering four core categories: variables, statements, methods, and algorithms. Additionally, we further built the extended _DataRef+_ inconsistency dataset based on the inconsistent code segments collected from _DataRef_ . We utilized _DataRef+_ to evaluate a set of representative state-of-the-art LLMs released in 2025. The experimental results demonstrate that although these recent LLMs alleviate the inconsistency issues observed in earlier models to a certain degree, they still produce inconsistencies at a rate of 6.06%. To mitigate such refactoring inconsistencies, this paper proposes a hybrid strategy integrating RAG and structured few-shot prompting. Our exploratory experiments deliver promising preliminary results, showing that the proposed approach reduces the inconsistency rate by 12.46 percentage points, decreasing from 17.17% to 4.71% under GPT-3.5-turbo with Python code and single-round generation settings. Nevertheless, the current validation remains limited, and further cross-model, cross-language, and multi-scenario evaluations are required to confirm its generalizability. For future work, we plan to enrich our empirical studies with more programs and industrial-grade projects through industrial cooperation, conduct evaluations over a broader set of LLMs, and further explore effective strategies for improving the consistency of LLM-refactored code. 

**Author Contributions** Yang Zhang: Proposing the idea, Experimental analysis, Writing - review & editing. Lijie Yuan: Conducting experimentation, Writing - original draft, review & editing. Chunhao Dong: Writing - review & editing. 

**Funding** This work is partially supported by the Pre-research Hebei International Collaboration Foundation under Grant No.202620102010167. 

**Data Availability** The data generated during and/or analyzed during the current study are available at  h t t p s : / / u z h a n g y a n g . g i t h u b . i o / r e s e a r c h / d a t a r e f . h t m l . 

### **Declarations** 

**Competing Interest** The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper. 

## **References** 

Abadi M, Keidar-Barner S, Pidan D, Veksler T (2019) Verifying parallel code after refactoring using equivalence checking. Int J Parallel Prog 47(1):59–73 

> Achiam J, Adler S, Agarwal S, Ahmad L, Akkaya I, Aleman FL, Almeida D, Altenschmidt J, Altman S, Anadkat S (2023) Gpt-4 technical report. arXiv:2303.08774 

```
1 3
```

Empirical Software Engineering          (2026) 31:178 

<mark>Page 39 of 41 178</mark> 

Adler F, Fraser G, Gründinger E, Körber N, Labrenz S, Lerchenberger J, Lukasczyk S, Schweikl S (2021) Improving readability of scratch programs with search-based refactoring. In: 2021 IEEE 21st International Working Conference on Source Code Analysis and Manipulation (SCAM), pp 120–130. IEEE 

Al Dallal J, Abdin A (2017) Empirical evaluation of the impact of object-oriented code refactoring on quality attributes: A systematic literature review. IEEE Trans Software Eng 44(1):44–69 

AlOmar EA, Peruma A, Mkaouer MW, Newman C, Ouni A, Kessentini M (2021) How we refactor and how we document it? on the use of supervised machine learning algorithms to classify refactoring documentation. Expert Syst Appl 167:114176 

AlOmar EA, Venkatakrishnan A, Mkaouer MW, Newman C, Ouni A (2024) How to refactor this code? an exploratory study on developer-chatgpt refactoring conversations. In: Proceedings of the 21st international conference on mining software repositories, pp 202–206 

AlOmar EA, Xu L, Martinez S et al (2025) Chatgpt for code refactoring: Analyzing topics, interaction, and effective prompts. In: 2025 IEEE International Conference on Collaborative Advances in Software and COmputiNg (CASCON), pp 389–398. IEEE Azeem MI, Palomba F, Shi L, Wang Q (2019) Machine learning techniques for code smell detection: A systematic literature review and meta-analysis. Inf Softw Technol 108:115–138 

- Bai S, Chen K, Liu X, Wang J, Ge W, Song S, Dang K, Wang P, Wang S, Tang J et al (2025) Qwen2. 5-vl technical report. arXiv:2502.13923 

Chen M, Tworek J, Jun H, Yuan Q, Pinto HPDO, Kaplan J, Edwards H, Burda Y, Joseph N, Brockman G (2021) Evaluating large language models trained on code. arXiv:2107.03374 

- Chondamrongkul N, Sun J (2023) Software evolutionary architecture: automated planning for functional changes. Sci Comput Program 230:102978 

- Cordeiro J, Noei S, Zou Y (2024) An empirical study on the code refactoring capability of large language models. ACM Trans Softw Eng Methodol 

- Cordeiro J, Noei S, Zou Y (2025) Llm-driven code refactoring: Opportunities and limitations. In: 2025 IEEE/ ACM Second IDE Workshop (IDE), pp 32–36. IEEE 

- Dao T-H, Trinh T-B, Truong N-T (2017) A tool support for checking consistency in model refactoring. In: 9th International Conference on Knowledge and Systems Engineering (KSE), pp 100–105. IEEE 

- DePalma K, Miminoshvili I, Henselder C, Moss K, AlOmar EA (2024) Exploring chatgpt’s code refactoring capabilities: An empirical study. Expert Syst Appl 249:123602 

- Dilhara M, Bellur A, Bryksin T, Dig D (2024) Unprecedented code change automation: The fusion of llms and transformation by example. In: Proceedings of the ACM on software engineering 1(FSE):631–653 

- Dong C, Jiang Y, Zhang Y, Zhang Y, Hui L (2025) Chatgpt-based test generation for refactoring engines enhanced by feature analysis on examples. In: 2025 IEEE/ACM 47th International Conference on Software Engineering (ICSE), pp 746–746. IEEE Computer Society 

- Du X, Liu M, Wang K, Wang H, Liu J, Chen Y, Feng J, Sha C, Peng X, Lou Y (2023) Classeval: A manuallycrafted benchmark for evaluating llms on class-level code generation. arXiv:2308.01861 

- Fan Z, Gao X, Mirchev M, Roychoudhury A, Tan SH (2023) Automated repair of programs from large language models. In: 2023 IEEE/ACM 45th International Conference on Software Engineering (ICSE), pp 1469–1481. IEEE 

- Foster SR, Griswold WG, Lerner S (2012) Witchdoctor: Ide support for real-time auto-completion of refactorings. In: 34th International Conference on Software Engineering (ICSE), pp 222–232. IEEE 

- Fowler M (2018) Refactoring: Improving the Design of Existing Code. Addison-Wesley Professional, Upper Saddle River, NJ, USA 

- Glm T, Zeng A, Xu B, Wang B, Zhang C, Yin D, Zhang D, Rojas D, Feng G, Zhao H et al (2024) Chatglm: A family of large language models from glm-130b to glm-4 all tools. arXiv:2406.12793 

- Gulzar MA, Zhu Y, Han X (2019) Perception and practices of differential testing. In: 2019 IEEE/ACM 41st International Conference on Software Engineering: Software Engineering in Practice (ICSE-SEIP), pp 71–80. IEEE 

- Guo D, Yang D, Zhang H, Song J, Zhang R, Xu R, Zhu Q, Ma S, Wang P, Bi X et al (2025) Deepseek-r1: Incentivizing reasoning capability in llms via reinforcement learning. arXiv:2501.12948 

- Huang L, Yu W, Ma W, Zhong W, Feng Z, Wang H, Chen Q, Peng W, Feng X, Qin B et al (2025) A survey on hallucination in large language models: Principles, taxonomy, challenges, and open questions. ACM Trans Inf Syst 43(2):1–55 

- Ivers J, Seifried C, Ozkaya I (2022) Untangling the knot: Enabling architecture evolution with search-based refactoring. In: 2022 IEEE 19th International Conference on Software Architecture (ICSA), pp 101– 111. IEEE 

- Kurbatova Z, Veselov I, Golubev Y, Bryksin T (2020) Recommendation of move method refactoring using path-based representation of code. In: Proceedings of the IEEE/ACM 42nd international conference on software engineering workshops, pp 315–322 

```
1 3
```

<mark>178 Page 40 of 41</mark> 

Empirical Software Engineering          (2026) 31:178 

Li T, Zhang Y (2024) Multilingual code refactoring detection based on deep learning. Expert Syst Appl 258:125164 

Li J, Li G, Li Y, Jin Z (2025) Structured chain-of-thought prompting for code generation. ACM Trans Softw Eng Methodol 34(2):1–23 

Lin Y, Peng X, Cai Y, Dig D, Zheng D, Zhao W (2016) Interactive and guided architectural refactoring with search-based recommendation. In: Proceedings of the 2016 24th ACM SIGSOFT international symposium on foundations of software engineering, pp 535–546 

Liu H, Jin J, Xu Z, Zou Y, Bu Y, Zhang L (2019) Deep learning based code smell detection. IEEE Trans Software Eng 47(9):1811–1837 

Liu B, Liu H, Li G, Niu N, Xu Z, Wang Y, Xia Y, Zhang Y, Jiang Y (2023) Deep learning based feature envy detection boosted by real-world examples. In: Proceedings of the 31st ACM joint european software engineering conference and symposium on the foundations of software engineering, pp 908–920 

Liu A, Feng B, Xue B, Wang B, Wu B, Lu C, Zhao C, Deng C, Zhang C, Ruan C (2024) Deepseek-v3 technical report. arXiv:2412.19437 

Liu B, Jiang Y, Zhang Y, Niu N, Li G, Liu H (2025) Exploring the potential of general purpose llms in automated software refactoring: an empirical study. Autom Softw Eng 32(1):26 

Maiga A, Ali N, Bhattacharya N, Sabané A, Guéhéneuc Y-G, Aimeur E (2012a) Smurf: A svm-based incremental anti-pattern detection approach. In: 19th Working Conference on Reverse Engineering, pp 466–475. IEEE 

Maiga A, Ali N, Bhattacharya N, Sabané A, Guéhéneuc Y-G, Antoniol G, Aimeur E (2012b) Support vector machines for anti-pattern detection. In: Proceedings of the 27th IEEE/ACM international conference on automated software engineering, pp 278–281 

Ma W, Liu S, Lin Z, Wang W, Hu Q, Liu Y, Zhang C, Nie L, Li L, Liu Y (2023) Lms: Understanding code syntax and semantics for code analysis. arXiv:2305.12138 

McCabe TJ (1976) A complexity measure. IEEE Trans Software Eng 4:308–320 

Miltner A, Gulwani S, Le V, Leung A, Radhakrishna A, Soares G, Tiwari A, Udupa A (2019) On the fly synthesis of edit suggestions. In: Proceedings of the ACM on Programming Languages 3(OOPSLA):1–29 

Oueslati K, Lamothe M, Khomh F (2025) Refagent: A multi-agent llm-based framework for automatic software refactoring. arXiv:2511.03153 

Peng A, Wu M, Allard J, Kilpatrick L, Heidel S (2023) Gpt-3.5 turbo fine-tuning and api updates. OpenAI Blog 18 

Pomian D, Bellur A, Dilhara M, Kurbatova Z, Bogomolov E, Bryksin T, Dig D (2024) Together we go further: Llms and ide static analysis for extract method refactoring. arXiv:2401.15298 

Ren S, Guo D, Lu S, Zhou L, Liu S, Tang D, Sundaresan N, Zhou M, Blanco A, Ma S (2020) Codebleu: a method for automatic evaluation of code synthesis. arXiv:2009.10297 

Roziere B, Gehring J, Gloeckle F, Sootla S, Gat I, Tan XE, Adi Y, Liu J, Sauvestre R, Remez T (2023) Code llama: Open foundation models for code. arXiv:2308.12950 

Schäfer M, Dolby J, Sridharan M, Torlak E, Tip F (2010) Correct refactoring of concurrent java code. In: European conference on object-oriented programming. Springer, pp 225–249 

Shirafuji A, Oda Y, Suzuki J, Morishita M, Watanobe Y (2023) Refactoring programs using large language models with few-shot examples. In: 30th Asia-Pacific Software Engineering Conference (APSEC), pp 151–160. IEEE 

Silva IP, Alves EL, Andrade WL (2017) Analyzing automatic test generation tools for refactoring validation. 2017 IEEE/ACM 12th International Workshop on Automation of Software Testing (AST), pp 38–44. IEEE 

Spencer D (2009) Card Sorting: Designing Usable Categories. Rosenfeld Media, New York 

Torres W, Brand MG, Serebrenik A (2021) A systematic literature review of cross-domain model consistency checking by model management tools. Softw Syst Model 20(3):897–916 

Wadhwa N, Pradhan J, Sonwane A, Sahu SP, Natarajan N, Kanade A, Parthasarathy S, Rajamani S (2023) Frustrated with code quality issues? llms can help!. arXiv:2309.12938 

Wang H, Xu Z, Zhang H, Tsantalis N, Tan SH (2024) An empirical study of refactoring engine bugs. arXiv:2409.14610 

White J, Hays S, Fu Q, Spencer-Smith J, Schmidt DC (2024) Chatgpt prompt patterns for improving code quality, refactoring, requirements elicitation, and software design. Generative AI for Effective Software Development. Springer, Cham, pp 71–108 Xu Y, Yang J (2026) Swe-refactor: A repository-level benchmark for real-world llm-based code refactoring. arXiv:2602.03712 

Yin X, Knight J, Weimer W (2009) Exploiting refactoring in formal verification. In: 2009 IEEE/IFIP international conference on dependable systems & networks, pp 53–62. IEEE 

Zhang Y, Xue Y (2024) Exceref: Automatically refactoring for exception handling. In: Proceedings of the 15th Asia-Pacific Symposium on Internetware, pp 239–248 

```
1 3
```

Empirical Software Engineering          (2026) 31:178 

<mark>Page 41 of 41 178</mark> 

Zhang Y, Li C, Bai Y (2021) Consistency validation method for java fine-grained lock refactoring. IEEE Access 9:149287–149301 

Zhang Y, Ge C, Hong S, Tian R, Dong C, Liu J (2022) Delesmell: Code smell detection based on deep learning and latent semantic analysis. Knowl-Based Syst 255:109737 

Zhang F, Chen B, Zhang Y, Keung J, Liu J, Zan D, Mao Y, Lou J-G, Chen W (2023) Repocoder: Repositorylevel code completion through iterative retrieval and generation. arXiv:2303.12570 

Zhang Y, Guan K, Fang L (2024) Mirror: multi-objective refactoring recommendation via correlation analysis. Autom Softw Eng 31(1):2 

Zhang Y, Li Y, Meredith G, Zheng K, Li X (2025a) Move method refactoring recommendation based on deep learning and llm-generated information. Inf Sci 697:121753 

Zhang Y, Zhang C, Zheng K, Meredith G (2025b) Deepcss: severity classification for code smell based on deep learning. Empir Softw Eng 30(3):86 

- Zhang Z, Wang C, Wang Y, Shi E, Ma Y, Zhong W, Chen J, Mao M, Zheng Z (2025c) Llm hallucinations in practical code generation: Phenomena, mechanism, and mitigation. In: Proceedings of the ACM on Software Engineering 2(ISSTA):481–503 

- Zheng Q, Xia X, Zou X, Dong Y, Wang S, Xue Y, Shen L, Wang Z, Wang A, Li Y et al (2023) Codegeex: A pre-trained model for code generation with multilingual benchmarking on humaneval-x. In: Proceedings of the 29th ACM SIGKDD Conference on Knowledge Discovery and Data Mining, pp 5673–5684 

**Publisher's Note** Springer Nature remains neutral with regard to jurisdictional claims in published maps and institutional affiliations. 

Springer Nature or its licensor (e.g. a society or other partner) holds exclusive rights to this article under a publishing agreement with the author(s) or other rightsholder(s); author self-archiving of the accepted manuscript version of this article is solely governed by the terms of such publishing agreement and applicable law. 

## **Authors and Affiliations** 

### **Yang Zhang**<sup>**1**</sup> **· Lijie Yuan**<sup>**1**</sup> **· Chunhao Dong**<sup>**1**</sup> 

- Yang Zhang 

zhangyang@hebust.edu.cn; uzhangyang@foxmail.com 

Lijie Yuan 2276486735@qq.com 

Chunhao Dong dongchunhao22@bit.edu.cn 

- 1 School of Information Science and Engineering, Hebei University of Science and Technology, Shijiazhuang 050018, China 

```
1 3
```