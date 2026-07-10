Science of Computer Programming 254 (2026) 103512 



Contents lists available at ScienceDirect 

# Science of Computer Programming 

journal homepage: www.elsevier.com/locate/scico 



## DecIR: Enhancing LLM-based LLVM IR decompilation through program analysis 



### Yuzhang Li a,∗, Xi Zhang a, Tao Xu b, Chunlu Wang a 

a _School of Cyberspace Security, Beijing University of Posts and Telecommunications, Beijing, China_ b _Department of Computer Science and Technology, Tsinghua University, Beijing, China_ 

|a r t i c l e i n f o|a b s t r a c t|
|---|---|
|_Keywords:_<br>|Decompilation serves as a fundamental technique in software reverse engineering by reconstruct-|
|Neural decompilation<br>Large language models<br>LLVM IR<br>Symbolic execution|ing source code from compiled binaries. Although extensively studied, traditional rule-based de-<br>compilers often produce outputs with limited readability due to inherent algorithmic constraints.<br>Recent advances in large language models (LLMs) have demonstrated promising potential for<br>code generation tasks, leading to their adoption in decompilation. However, while LLM-based<br>decompilation shows notable efectiveness, it introduces new reliability challenges concerning<br>compilation feasibility and semantic consistency with the original program behavior. This study<br>investigates how to enhance the reliability of LLM-based decompilation through systematic inte-<br>gration with program analysis techniques. We present DecIR, a novel decompilation framework<br>that targets LLVM IR (Low-Level Virtual Machine Intermediate Representation). Our methodol-<br>ogy follows a three-phase approach: (1) initial decompilation using LLMs, (2) automated compila-<br>tion error correction through iterative repair mechanisms, and (3) semantic consistency verifca-<br>tion via symbolic execution. Experimental results demonstrate that DecIR signifcantly improves<br>both compilation success rates and semantic preservation compared to baseline decompilation<br>approaches. The fndings confrm that combining LLMs with formal program analysis techniques<br>efectively mitigates reliability issues in neural decompilation. This hybrid paradigm not only en-<br>hances the practical viability of LLM-based decompilation but also suggests broader applicability<br>for software engineering tasks that require reliable code transformation.|



#### **1. Introduction** 

Decompilation denotes the process of converting low-level machine code into high-level programming languages such as C/C++. As a fundamental technique in software reverse engineering, decompilation has been extensively utilized in security-critical applications including bug analysis [1,2] and malware detection [3,4]. While decompilation represents the inverse operation of compilation, its principal technical challenge involves reconstructing high-level semantic information that is inherently lost during compilation [5–9]. For example, human-readable programming constructs like complex control flows and data structures are typically transformed into machine-oriented instruction sequences through unconditional jumps, conditional branches, and memory layouts during compilation. Although mature decompilers [10–12] implement numerous heuristic rules to bridge this semantic gap, even state-of-the-art solutions frequently generate outputs containing either unintelligible control flows and type information or semantic inaccuracies. As 

##### ∗ Corresponding author. 

_E-mail addresses:_ yzlee@bupt.edu.cn (Y. Li), zhangx@bupt.edu.cn (X. Zhang), xtao@tsinghua.edu.cn (T. Xu), wangcl@bupt.edu.cn (C. Wang). 

https://doi.org/10.1016/j.scico.2026.103512 

Received 9 July 2025; Received in revised form 3 March 2026; Accepted 21 May 2026 Available online 25 May 2026 

0167-6423/© 2026 Elsevier B.V. All rights are reserved, including those for text and data mining, AI training, and similar technologies. 

_Science of Computer Programming 254 (2026) 103512_ 

_Y. Li, X. Zhang, T. Xu et al._ 

a result, decompilers have primarily served as supplementary tools for reverse engineers, necessitating significant manual intervention where domain experts must verify and refine the decompiled code based on their specialized knowledge. 

Recent advancements in natural language processing have facilitated the emergence of neural decompilers [13,14], which leverage sequence-to-sequence neural machine translation models trained on large-scale decompilation datasets. These data-driven approaches obviate the need for manually engineered heuristic rules that limit conventional decompilers. Whereas traditional decompilers depend on finite sets of transformation rules, neural decompilers can learn comprehensive high-level language patterns from extensive training corpora, thereby enabling more precise reconstruction of human-readable program semantics. The incorporation of large language models (LLMs) has further enhanced decompilation techniques through prompt-based learning methodologies [15,16]. These approaches refine unoptimized decompiled code from conventional decompilers using carefully designed prompts, eliminating the requirement for model pre-training. However, the probabilistic nature of neural decompilers introduces interpretability challenges since their outputs lack the transparent traceability characteristic of rule-based transformations. Additionally, incomplete training data coverage may cause robustness issues where slight variations in binary code yield unpredictable semantic deviations in the reconstructed output. 

To mitigate these challenges, researchers have developed modular frameworks that partition the decompilation process into sequential stages, integrating multiple models with formal verification techniques [17]. Although promising, current approaches exhibit three major limitations. First, they typically process entire decompiled files as monolithic units, which introduces scalability issues when dealing with large software systems due to memory constraints and computational inefficiency. Second, existing methods [15,16] rely on the C code generated by traditional decompilers as input to LLMs. However, because such inputs are restricted to C and often suffer from poor code quality, the code generation potential of LLMs remains underutilized. Third, current methodologies lack an automated framework for verifying decompilation reliability, as demonstrated by the impracticality of applying unit testing to unknown code. These limitations highlight the necessity for more robust solutions that can ensure both the accuracy and scalability of decompilation while fully leveraging the code generation capabilities of LLMs. 

In this paper, we present DecIR, a novel neural decompilation framework that operates on LLVM [18] IR (Low-Level Virtual Machine Intermediate Representation, henceforth referred to as IR). The key idea of our approach lies in its ability to process IR as input and utilize LLMs to transform it into high-level programming language code. The framework features an iterative optimization mechanism that systematically incorporates recompilation error feedback into the LLM, which progressively refines the decompiled code until it becomes compilable. Moreover, DecIR employs a comprehensive formal verification process to guarantee semantic equivalence between the decompilation output and the original IR. This verification mechanism integrates symbolic execution with SMT (Satisfiability Modulo Theories) [19] solver-based techniques to mathematically demonstrate the equivalence between the IR regenerated from the decompiled high-level code and the input IR. This formal verification process is essential for preserving semantic integrity throughout decompilation and for validating the correctness of outputs generated by LLMs. The framework specifically tackles three fundamental challenges in neural decompilation: 

- Context Management: DecIR operates at function granularity, processing individual functions independently. This design decision stems from practical considerations, as function-level decomposition naturally constrains the context size for LLMs while preserving sufficient semantic information. This approach mitigates the accuracy degradation typically observed in larger-scale decompilation attempts. 

- Input Representation: DecIR employs the intermediate representation commonly used during compilation and decompilation as input (specifically LLVM IR). As a platform- and language-independent intermediate representation that bridges high-level and low-level languages, IR serves as an optimal abstraction layer for systematically assessing LLM performance in decompilation tasks. 

- Semantic Verification: DecIR introduces a formal analysis method based on symbolic execution and SMT solving. This approach provides substantially stronger completeness guarantees than existing validation techniques in neural decompilation systems. 

We perform a comprehensive evaluation of DecIR using both the Exebench [20] and Decompile-Eval [21] datasets. The experimental results demonstrate that, with the assistance of symbolic execution-based semantic verification method, our framework achieves a 10% improvement in both compilability and executability compared to purely LLM-driven decompilation workflows. Moreover, our proposed symbolic execution-based semantic verification method attains precision and recall of 92.79% and 98.26% respectively, which confirms its effectiveness in maintaining semantic equivalence throughout the decompilation process. The contributions of this paper can be summarized as follows: 

- We present DecIR, a novel LLM-based decompilation framework that is specifically designed for IR code. 

- We introduce an iterative prompt learning methodology that generates compilable decompiled code through progressive refinement. 

- We propose a program analysis-based verification method that ensures semantic equivalence between decompiled code and the original IR code. 

- We implement DecIR and conduct a comprehensive evaluation, including detailed analysis of the framework’s performance and effectiveness. 

The remainder of this paper is organized as follows: Section 2 provides an overview of relevant background information. Section 3 reviews related work in the field. Section 4 presents our proposed methodology in detail. Section 5 describes the experimental setup, including research questions, datasets, baseline methods, evaluation metrics, and implementation details. Section 6 reports 

2 

_Science of Computer Programming 254 (2026) 103512_ 

_Y. Li, X. Zhang, T. Xu et al._ 





**Fig. 2.** The overall workflow of RetDec. 

and analyzes the experimental results. Section 7 discusses the limitations of our approach and potential threats to validity. Finally, Section 8 concludes the paper and outlines directions for future research. 

#### **2. Background** 

To establish a comprehensive foundation for understanding our methodology, this section systematically introduces the fundamental processes, core concepts, and representative tools in compilation and decompilation. 

The compilation process begins with lexical and syntactic analysis of high-level source code, transforming the textual input into structured data that computers can efficiently process. This structured data is commonly represented as an Abstract Syntax Tree (AST). The AST is then converted into an intermediate representation (IR) that is independent of the underlying hardware architecture. This IR provides an architecture-neutral representation that preserves program semantics while eliminating language-specific features. As a unified intermediate form, the IR provides a critical abstraction layer in modern compiler design, enabling multiple optimization passes to be applied in an architecture-agnostic manner. LLVM<sup>1</sup> [18] represents one of the most prominent and widely adopted compiler frameworks, featuring an exemplary modular architecture. Through various frontends such as Clang [22] for C/C++ and Gollvm for Go, LLVM converts multiple high-level programming languages into its intermediate representation (i.e. LLVM IR). The framework processes this LLVM IR through multiple optimization phases in its middle-end before the backend generates target-specific code. The backend can produce either conventional machine code or alternative targets including WebAssembly (WASM). Fig. 1 illustrates the overall LLVM workflow. LLVM IR provides a language-agnostic abstraction that effectively balances high-level program structure with low-level implementation details. It surpasses traditional assembly languages in sophistication while maintaining sufficient low-level characteristics to support code optimization and transformation. 

Decompilation is the process of reconstructing high-level source code from low-level program representations (e.g., ELF-format binary executables) while maintaining both functional equivalence and code readability. While decompilation and compilation are inverse processes, they share significant similarities in their workflows. Both fundamentally depend on intermediate representations and employ heuristic rules to enable code transformation. RetDec [12] serves as a prominent example of an open-source decompiler built on the LLVM framework. It implements a two-phase decompilation process: first lifting binary code to LLVM IR, then decompiling this IR into high-level source code, as shown in Fig. 2. Ghidra [11], another notable decompiler, uses its own intermediate representation called P-code. Its workflow similarly involves lifting binary code to P-code, performing optimizations, and finally decompiling the optimized P-code into high-level language constructs. The use of intermediate representations in decompilers follows the same rationale as in compilers: to reduce the inherent challenges in bridging the semantic gap between low-level and high-level languages. This approach effectively applies a divide-and-conquer strategy to manage the complex transformation problem. 

In this study, we focus specifically on utilizing LLMs to decompile LLVM IR into high-level source code. The selection of LLVM IR as our input representation, rather than architecture-specific assembly code such as X86_64 or AArch64, provides significant research advantages. LLVM IR represents a more generalized problem formulation that enables us to draw conclusions with wider applicability across various instruction set architectures. From an engineering perspective, using LLVM IR as the foundation for neural decompilation facilitates seamless integration with the existing LLVM toolchain. This design decision allows us to effectively leverage the substantial achievements of mature compilation frameworks. For example, our proposed decompilation approach can 

> 1 LLVM stands for Low-Level Virtual Machine, but its current functionality has expanded beyond its literal meaning. It is now a comprehensive and feature-rich foundational framework for compilation. 

3 

_Science of Computer Programming 254 (2026) 103512_ 

_Y. Li, X. Zhang, T. Xu et al._ 

be conveniently integrated with RetDec’s lifter component, where binary code is first lifted to LLVM IR using RetDec’s established infrastructure before our neural decompilation method completes the transformation to high-level code. This modular design not only enhances practical implementation but also illustrates how innovative techniques can build upon well-established systems within the compilation and decompilation ecosystem. It is worth noting that IRs such as P-code (used in Ghidra) and VEX IR (used in angr) serve a purpose similar to that of LLVM IR and also support symbolic execution. This suggests that these IRs could also be adapted to our decompilation methodology. However, in this work, we select LLVM IR over alternative IRs due to the broader adoption of the LLVM infrastructure, whereas P-code and VEX IR are largely confined to specific decompilation tools. Furthermore, the wider application of LLVM IR implies the availability of more public corpora for training LLMs, thereby enhancing their comprehension of LLVM IR. 

#### **3. Related work** 

In this section, we present related work relevant to our study. We first review rule-based decompilation methods and subsequently outline recent advances in neural decompilation research (Section 3.1). We then review LLM-based software engineering techniques, with a focus on approaches that incorporate auxiliary assurance mechanisms (Section 3.2). Finally, we introduce the application of symbolic execution techniques in the context of code semantic similarity analysis (Section 3.3). 

#### _3.1. Decompilation and neural decompilation_ 

We categorize decompilation techniques into traditional decompilation and neural decompilation. The former refers to rule-based methods employed in mainstream decompilers, while the latter encompasses research on decompilation utilizing neural networks. Furthermore, neural decompilation can be subdivided into models trained under conventional paradigms and LLM-based decompilation approaches [15,23]. 

Traditional decompilation approaches predominantly rely on rule-based techniques that incorporate pattern matching and controlflow analysis to reconstruct code structures and variables. Widely-used decompilers including IDA Pro [10], Ghidra [11], and RetDec [12] employ recursive traversal algorithms and heuristic methods; however, they demonstrate significant limitations when processing optimized binaries. These tools often cannot recover critical semantic information such as variable names and comments, and frequently produce output that fails to recompile successfully [16]. While structural analysis techniques have shown improved performance in control-flow recovery [24], their effectiveness and generalizability remain limited by two key factors: the manual design of transformation rules and their inherent platform-specific dependencies. 

Neural network methods have emerged as a promising solution to address these challenges by learning implicit mappings between binaries and source code. Early research efforts, including neural machine translation (NMT) models [25,26], demonstrate the feasibility of translating assembly/IR to source code. For example, Katz et al., katztowards2019 propose an NMT-based framework that decompiles x86 assembly to C with 88% accuracy. Coda [14] is the first end-to-end neural-based decompiler, which also uses NMT model. Subsequent studies [27,28] have improved performance by leveraging pre-trained language models [29,30]. Recent approaches incorporate domain-specific optimizations: SLaDe [23] combines Transformer models with type inference to produce more readable and correct outputs, while Nova+ [31] introduces pre-training tasks such as optimization generation to align binaries across different ISAs. The field has further advanced with the application of LLMs. DeGPT [15] employs a three-role mechanism consisting of referee, advisor, and operator components to refine decompiler outputs, reducing code complexity [32] by 24.4%, which in turn improves code readability. Similarly, LLM4Decompile [33] trains models on 4 billion tokens of C-source pairs and achieves 21% re-executability through recompilation-guided error correction. 

Despite recent progress, several limitations remain in current approaches. First, methods such as DeGPT [15] and DecGPT [16] primarily optimize existing decompiler outputs, which inherently ties their performance to the quality of underlying decompilation tools. For instance, their effectiveness is constrained by known limitations in tools like IDA Pro [10], particularly regarding incomplete type recovery [34,35]. This dependency makes it difficult to draw definitive conclusions about the standalone capabilities of neural decompilation techniques. Second, current validation methods remain insufficient. Most existing work [28,31,36] relies on metrics like BLEU [37] or recompilation success rates [16], without providing robust verification of functional equivalence. Although BINSUM [36] introduces semantic similarity metrics, this approach encounters challenges in accurately aligning fuzzy textual summaries of binary code. Third, LLM-based approaches [15,17] face significant challenges with error propagation and contextual constraints, particularly due to limited token windows. 

To address these challenges, this study proposes a novel approach that directly employs LLMs for decompiling LLVM IR, as opposed to optimizing the often unreadable C code generated by existing decompilers. Our methodology strategically partitions the LLVM IR at the function level, which effectively constrains the context length for each LLM query, thereby mitigating performance degradation associated with extensive context processing. Furthermore, we introduce a formally verified symbolic model that rigorously guarantees semantic equivalence between the decompiled code and the original input, ensuring the reliability of our decompilation results through mathematical precision. This approach not only enhances the readability of decompiled output but also establishes a verifiable foundation for semantic preservation throughout the decompilation process. 

#### _3.2. Assured LLM-based software engineering_ 

Recent advances in LLMs have demonstrated remarkable success across various software engineering tasks, including code generation and optimization [38–41], program repair [42–44], and software testing [45–47]. For example, state-of-the-art LLMs such as 

4 

_Science of Computer Programming 254 (2026) 103512_ 

_Y. Li, X. Zhang, T. Xu et al._ 

ChatGPT [48] and Codex [49] exhibit strong capabilities in synthesizing functional code from natural language specifications [39,41] while generating test cases that maintain human-readable quality [47]. Furthermore, autonomous agent frameworks utilize multiLLM collaboration to decompose complex software engineering tasks into subtasks (e.g., requirements analysis, implementation, and verification), thereby emulating human team dynamics to improve code quality [38,39,50]. However, despite these significant advancements, ensuring the correctness, reliability, and verifiability of LLM-generated outputs remains a critical research challenge. Current models frequently produce code that, while syntactically correct, contains semantic errors or violates temporal and domainspecific constraints [51–53]. 

To address these challenges, researchers have developed two principal strategies. The first strategy involves multi-LLM collaboration frameworks, which mitigate reliability risks through iterative refinement and cross-verification mechanisms. For instance, self-iteration methods [38] utilize analyst, developer, and tester roles to iteratively refine requirements and validate outputs against predefined test cases. Similarly, self-collaboration approaches [39] decompose tasks into specialized subtasks that are processed by distinct LLM agents, whereas structured chain-of-thought prompting [54] enforces program logic constraints during code generation. These methods capitalize on the emergent reasoning capabilities of LLMs to minimize errors via stepwise planning [41] and semantic filtering [51]. The second strategy integrates program analysis techniques to enhance assurance by combining LLMs with formal verification, static analysis, or execution feedback. For example, SynCode [53] ensures syntactic correctness by augmenting LLM decoding with grammar-based constraints, while InferFix [43] incorporates static analyzer outputs (e.g., bug reports) to guide LLM-based repair. Tools such as CODAMOSA [45] leverage test execution diagnostics to direct LLMs toward coverage-critical code paths, and SelfAPR [55] employs self-supervised learning on project-specific perturbations to refine fault localization. Furthermore, NLP-driven techniques [52,56] extract temporal constraints from documentation to generate valid test sequences, and quality-aware frameworks [57] couple LLMs with static analyzers to verify code revisions against both functional and non-functional requirements. 

These efforts underscore an emerging consensus that reliable LLM-based software engineering necessitates a synergistic integration of LLM flexibility with rigorous validation mechanisms. Such integration can be achieved either through multi-agent collaboration or hybrid methodologies that combine generative AI with traditional program analysis techniques [44,46,51]. Aligned with this methodological perspective, our research aims to establish reliable LLM-based decompilation through formal guarantees rather than relying on opaque probabilistic outputs. This approach shifts the paradigm from black-box generation to verifiable correctness, ensuring the trustworthiness of decompilation results while maintaining the adaptability inherent to LLM-based solutions. The proposed framework bridges the gap between the generative power of large language models and the precision requirements of mission-critical software engineering tasks. 

#### _3.3. Symbolic execution for semantic similarity analysis_ 

Symbolic execution has emerged as a powerful technique for semantic similarity analysis of code, particularly when comparing binaries for which source code is unavailable. Unlike syntactic approaches that rely on superficial code features, symbolic execution reasons about program semantics by modeling variable values as symbolic expressions and deriving path constraints that characterize program behavior [58]. 

A number of studies have adopted symbolic execution for code diffing and similarity detection. For example, SigmaDiff [59] represents binaries as inter-procedural program dependency graphs at the intermediate representation level and applies a deep graph matching consensus model to identify correspondences among IR statements. By integrating lightweight symbolic analysis to generate semantic features and adopting semi-supervised learning, SigmaDiff achieves accurate pseudocode diffing under varying compiler optimizations, architectures, and versions. PASDA [60] employs a partition-based strategy for semantic differencing, using differential symbolic execution to prove equivalence or non-equivalence between program pairs. For cases where conclusive proofs are infeasible, it provides best-effort classifications ( `MAYBE_EQ` or `MAYBE_NEQ` ) based on partial proofs, thereby yielding more informative results than conventional unknown outcomes. This method integrates symbolic execution with iterative abstraction refinement and uses uninterpreted functions to handle unchanged code regions. BinSim [61] adopts a hybrid methodology that integrates dynamic analysis with symbolic execution. It employs system call sliced segment equivalence checking, in which backward slicing from system call arguments locates instruction segments that influence observable behavior. The approach then checks the semantic equivalence of these segments via weakest precondition computation and constraint solving, thereby identifying similarities that extend across multiple basic blocks. 

D-Helix [62] is the first work to apply differential symbolic execution to the domain of decompilation. It builds an automated evaluation framework for decompilers that identifies code defects which cause semantic inconsistencies in decompiled outputs. In this paper, we adapt this methodology to LLM-based decompilation workflow. Unlike D-Helix, we integrate symbolic execution as a component within the decompilation process itself. This integration leverages the strengths of symbolic execution in code similarity analysis to perform reliability verification on the decompiled code generated by LLMs. 

#### **4. Methodology** 

We present the technical details of DecIR in this section, including the overall workflow (Section 4.1) and detailed descriptions of its core components (Sections 4.2–4.4). 

5 

_Science of Computer Programming 254 (2026) 103512_ 

_Y. Li, X. Zhang, T. Xu et al._ 



**Fig. 3.** The overall workflow of DecIR. 

#### _4.1. Overall workflow_ 

The overall workflow of DecIR is shown in Fig. 3. The core idea is to employ the LLM to propose candidate decompiled code, while the decision to adopt any candidate is contingent upon its successful passage through a formal verification process using program analysis methods, thereby guaranteeing reliability. First, DecIR analyzes the input IR code (snippet _a_ in Fig. 3) to extract individual function snippets (snippet _b_ ). For each function, DecIR constructs specialized prompts that guide the LLM to perform IR-to-high-level-language decompilation (step _2_ in Fig. 3). After the LLM generates the decompiled code (snippet _c_ ), DecIR invokes the compiler to verify its recompilability (step _3_ ). If compilation errors occur, DecIR dynamically generates repair prompts that incorporate compiler error messages and feeds them back to the LLM for iterative correction (step _4_ ). The iterative process primarily terminates upon successful compilation, but may be subject to early termination or rollback depending on constraint conditions (detailed in Section 4.3). 

For successfully compiled high-level code, DecIR performs semantic equivalence checking through a structured process. The system first recompiles the decompiled code into LLVM IR (snippet _d_ ). It then constructs symbolic models (SymDiff in Fig. 3) that incorporate both the regenerated IR and the original input (snippet _b_ ), which are subsequently analyzed by an SMT solver to verify formal equivalence (step _5_ ). If the equivalence check fails, DecIR initiates an improved decompilation cycle by generating enhanced prompts that include previous LLM outputs as contextual references, thereby iteratively refining the decompilation quality (step _6_ ). 

DecIR accepts LLVM IR code as input and generates decompiled high-level language code that has passed semantic equivalence checking. The core innovation of DecIR lies in its methodology which integrates LLM-based text transformation for code processing (comprising both IR decompilation and decompiled code repair) with symbolic execution techniques for program semantic equivalence checking. Notably, we perform the formal verification at the IR level, which facilitates direct comparison between the LLMgenerated output and the original input code. 

#### _4.2. Function-level IR extraction_ 

The effective application of LLMs to decompilation tasks critically depends on the appropriate representation of target code when constructing prompt inputs. Since LLMs typically operate under context window constraints, where their performance degrades with excessive input length, careful consideration must be given to input size limitations. Through statistical analysis of prominent opensource software projects, we observe that although individual source files often span hundreds to thousands of lines, the majority of functions maintain a more manageable scale, typically below 200 lines. Current research practices that feed entire code files into LLMs inevitably lead to context overflow or suboptimal performance due to excessive input length. To address this limitation, our methodology proposes function-level decompilation, in which each IR file is decomposed into individual function snippets, with separate prompts constructed for each functional unit. 

6 

_Science of Computer Programming 254 (2026) 103512_ 

_Y. Li, X. Zhang, T. Xu et al._ 



**Fig. 4.** An example of C++ code and its generated LLVM IR. 



**Fig. 5.** The DAG constructed from code snippet _a_ in Fig. 3. 

From a modular design standpoint, an LLVM IR file encapsulates a complete compilation unit (Module) that contains three principal elements: (1) global variable declarations with their initialization rules ( `@c` in snippet _b_ in Fig. 3), (2) function definitions composed of basic block structures ( `f2` in snippet _b_ ), and (3) external symbol declarations ( `f1` in snippet _b_ ). A notable observation reveals a substantial scale disparity between the IR content and the original source code. This discrepancy becomes particularly pronounced in C++ code that involves extensive template instantiation, as the IR must explicitly declare all external dependencies, including standard library function signatures, that could be implicitly referenced in the source code (as shown in Fig. 4). 

The extraction of function-level IR snippets presents two fundamental technical challenges: the resolution of references to global variables and external functions, and the management of inter-procedural call dependencies. To address these challenges, we develop a specialized IR static analysis tool that employs a directed acyclic graph (DAG) for dependency analysis. Our solution guarantees that each extracted code snippet contains precisely the necessary dependency declarations while maintaining functional independence. The analysis pipeline operates through three sequential phases. First, the tool constructs a dependency graph for the entire IR module, in which nodes represent functions or global variables and edges indicate either call relationships or data dependencies. The tool then applies a reverse topological sort to the function nodes in the graph to produce an ordered sequence of functions. In this sequence, functions that do not call other functions are positioned earlier, thereby ensuring that each function appears only after all of its dependencies have been satisfied. Following the topological ordering phase, the tool traverses the sequence to generate functionlevel IR snippets. For each function, it outputs the corresponding function definition together with the definitions of any global variables on which it depends, which are extracted directly from the original IR module. To ensure correct compilation and linking, forward declarations for any functions called by the current function are also inserted. Taking the snippet _a_ in Fig. 3 as an example, the DAG constructed from it is depicted in Fig. 5. A reverse topological ordering of this DAG yields the function sequence { `f1` _,_ `f2` }. For function `f2` , which depends on function `f1` and the global variable `@c` , it is necessary to include a forward declaration of `f1` and duplicate the definition of the global variable `@c` when generating the corresponding function-level snippet (snippet _b_ in Fig. 3). 

The proposed tool maintains semantic integrity while respecting the practical constraints of LLM context windows, enabling effective processing of complex codebases. By preserving the independence of extracted function snippets, our approach naturally supports parallel processing capabilities, thereby improving analysis scalability. The maintained topological ordering ensures that decompiled high-level language snippets can be faithfully reassembled into complete source files, demonstrating robust reconstruction capability. Furthermore, the DAG-based analysis provides formal guarantees about the completeness of extracted function contexts, ensuring no critical reference information is lost during decomposition. 

7 

_Science of Computer Programming 254 (2026) 103512_ 

_Y. Li, X. Zhang, T. Xu et al._ 

#### _4.3. Prompt engineering for compilation-guaranteed LLM-based IR decompilation_ 

DecIR employs a hybrid approach to reliably decompile IR into compilable high-level code by combining the generative capabilities of LLMs with a compiler-guided iterative refinement process, as detailed in Section 4.1. From the perspective of prompt engineering, DecIR’s LLM query process consists of two distinct stages: the initial decompilation phase and the compilation error correction phase. The performance of LLM-based decompilation fundamentally relies on meticulously designed prompts that direct the model to generate both syntactically valid and semantically equivalent code. Based on thorough empirical analysis of prevalent decompilation challenges, including type inference inaccuracies, undefined variable references, and control-flow reconstruction ambiguities, we develop a systematic prompting strategy. The overall LLM query process is illustrated in Algorithm 1. 

**Algorithm 1** The pseudo code of DecIR’s LLM query process. 

**Input:** The original IR code _𝐼𝑅_<sup>_𝑖𝑛_</sup> , max times of iterations _𝑇_ . **Output:** The decompiled C code _𝐶_<sup>_𝑜𝑢𝑡_</sup> , recompiled IR code _𝐼𝑅_<sup>_𝑜𝑢𝑡_</sup> or compilation error. 1: _𝐶_ 0<sup>_𝑜𝑢𝑡_</sup> ← _𝑑𝑒𝑐𝑜𝑚𝑝𝑖𝑙𝑒_  𝑏𝑦_  𝑙𝑙𝑚_ ( _𝐼𝑅_<sup>_𝑖𝑛_</sup> ) 2: _𝐶_ 0<sup>_𝑜𝑢𝑡_</sup> ← _𝑓𝑜𝑟𝑚𝑎𝑡_  𝑎𝑛𝑑_  𝑐𝑙𝑒𝑎𝑛_ ( _𝐶_ 0<sup>_𝑜𝑢𝑡_)</sup> 3: ( _𝐼𝑅_<sup>_𝑜𝑢𝑡_</sup> 0<sup>_, 𝑒𝑟𝑟𝑜𝑟_0) ←</sup><sup>_𝑐𝑜𝑚𝑝𝑖𝑙𝑒_(</sup><sup>_𝐶_</sup> 0<sup>_𝑜𝑢𝑡_)</sup> 4: **if** _𝑒𝑟𝑟𝑜𝑟_ 0 is empty **then** 5: **return** ( _𝐶_ 0<sup>_𝑜𝑢𝑡, 𝐼𝑅𝑜𝑢𝑡_</sup> 0<sup>)</sup> _⊳𝐶_ 0<sup>_𝑜𝑢𝑡_iscompilable.</sup> 6: **end if** 7: 8: _𝑡_ ← 1 9: **while** _𝑡_ ≤ _𝑇_ **do** 10: _𝐶𝑡_<sup>_𝑜𝑢𝑡_</sup> ← _𝑓𝑖𝑥_  𝑒𝑟𝑟𝑜𝑟_  𝑏𝑦_  𝑙𝑙𝑚_ ( _𝐼𝑅_<sup>_𝑖𝑛_</sup> _𝑡_ −1<sup>_, 𝐶_</sup> _𝑡_<sup>_𝑜𝑢𝑡_</sup> −1<sup>_, 𝑒𝑟𝑟𝑜𝑟𝑡_−1)</sup> 11: _𝐶𝑡_<sup>_𝑜𝑢𝑡_</sup> ← _𝑓𝑜𝑟𝑚𝑎𝑡_  𝑎𝑛𝑑_  𝑐𝑙𝑒𝑎𝑛_ ( _𝐶𝑡_<sup>_𝑜𝑢𝑡_</sup> ) 12: ( _𝐼𝑅_<sup>_𝑜𝑢𝑡_</sup> _𝑡_<sup>_, 𝑒𝑟𝑟𝑜𝑟𝑡_) ←</sup><sup>_𝑐𝑜𝑚𝑝𝑖𝑙𝑒_(</sup><sup>_𝐶_</sup> _𝑡_<sup>_𝑜𝑢𝑡_</sup> ) 13: **if** _𝑒𝑟𝑟𝑜𝑟𝑡_ is empty **then** _⊳𝐶𝑡_<sup>_𝑜𝑢𝑡_iscompilable.</sup> 14: **return** ( _𝐶𝑡_<sup>_𝑜𝑢𝑡_</sup> _, 𝐼𝑅_<sup>_𝑜𝑢𝑡_</sup> _𝑡_<sup>)</sup> 15: **else if** _𝑡_ ≥ 3 **and** _𝑒𝑟𝑟𝑜𝑟𝑡_ == _𝑒𝑟𝑟𝑜𝑟𝑡_ −1 == _𝑒𝑟𝑟𝑜𝑟𝑡_ −2 **then** _⊳_ Early termination. 16: **break** 17: **else if** | _𝑒𝑟𝑟𝑜𝑟𝑡_ | _>_ | _𝑒𝑟𝑟𝑜𝑟𝑡_ −1| **then** _⊳𝐶𝑡_<sup>_𝑜𝑢𝑡_hasmoreerrorsthan</sup><sup>_𝐶_</sup> _𝑡_<sup>_𝑜𝑢𝑡_</sup> −1<sup>.</sup> 18: _𝐶𝑡_<sup>_𝑜𝑢𝑡_</sup> ← _𝐶𝑡_<sup>_𝑜𝑢𝑡_</sup> −1 19: _𝐼𝑅_<sup>_𝑜𝑢𝑡_</sup> _𝑡_ ← _𝐼𝑅_<sup>_𝑜𝑢𝑡_</sup> _𝑡_ −1 20: _𝑒𝑟𝑟𝑜𝑟𝑡_ ← _𝑒𝑟𝑟𝑜𝑟𝑡_ −1 21: **end if** 22: **end while** 23: 24: **return** ( _𝐶𝑡_<sup>_𝑜𝑢𝑡_</sup> _, 𝑒𝑟𝑟𝑜𝑟𝑡_ ) _⊳_ The max number of iterations is exceeded. 

During the initial decompilation phase (Line 1 in Algorithm 1), the instruction explicitly constrains the LLM to produce compilable C/C++ code with the following specification: 

Decompile the following LLVM IR to functionally equivalent C/C++ code. 

- Input LLVM IR: {IR} 

- Requirements: 

- Output only the decompiled code 

- No explanations, comments or additional text 

- Preserve all original functionality 

- Ensure the output is valid, compilable code (no explanations or additional text) 

This prompt design incorporates several critical considerations identified through our decompilation research. First, explicitly prohibiting explanatory text prevents the model from generating non-code output that might disrupt automated compilation processes. Second, the emphasis on functional equivalence directly addresses the prevalent challenge of semantic drift during decompilation. Third, the compilability requirement establishes a concrete, objective criterion for evaluating output quality. These carefully designed constraints collectively optimize the model’s performance for production-quality decompilation tasks. 

Following the initial decompilation phase, the generated code is immediately validated using Clang [22] compiler (Line 3 or 12 in Algorithm 1). When the compilation fails, we analyze the error logs to extract semantic error messages. To ensure the LLM focuses on the essential logic, we perform code sanitation on the generated outputs (Line 2 or 11). This process, as illustrated in the before-and-after comparison of Fig. 6 ( _𝑎_ → _𝑐_ for code, _𝑏_ → _𝑑_ for error messages), involves three key operations: (1) formatting the code to standardize indentation and spacing, thereby eliminating noise for consistent parsing; (2) removing redundant or 

8 

_Science of Computer Programming 254 (2026) 103512_ 

_Y. Li, X. Zhang, T. Xu et al._ 



**Fig. 6.** An example of C code and its compilation errors. 

non-algorithmic comments that do not contribute to functional understanding; and (3) stripping extraneous details from error messages, such as project-specific file paths and line numbers, to prevent the model from learning irrelevant environmental artifacts. This sanitation step enhances the generality of the code snippets and reduces noise in the LLM’s subsequent processing. The distilled error information, when combined with the faulty code snippet, constitutes the input for the subsequent repair iteration (Line 10). We dynamically construct specialized prompts that incorporate the compiler feedback: 

I need to fix compilation errors in decompiled C/C++ code that was generated from LLVM IR. Here are the inputs: 

- Original LLVM IR: {IR} 

- Decompiled code with errors: {SRC} 

- Compiler error messages: {ERROR} 

- Requirements: 

- Correct the code to resolve all compilation errors 

- Preserve exact functionality from the original LLVM IR 

- Output ONLY the corrected code (no explanations or additional text) 

This iterative process continues until either successful compilation is achieved or a predefined iteration threshold is reached. To enhance the robustness of the iterative repair process, we implement two additional safeguards that focus on error messages. First, to prevent the LLM from generating invalid fixes, such as repeatedly producing the same error, we log and track the error message from each iteration. The iterative repair loop is terminated early if the same compilation error occurs three times consecutively (Line 15 in Algorithm 1). Second, we monitor the number of compilation errors. If the output of the current iteration introduces more compilation errors than the previous one, the current output is discarded, and the next iteration proceeds based on the prior output (Line 17). This mechanism helps prevent the repair process from diverging. For code snippets that remain erroneous after reaching the maximum iteration limit or after an early termination of the repair process, we flag them as corner cases and present both the faulty code and the corresponding error messages to the user (Line 24). This enables the user to either switch to a different LLM or manually correct the errors. Such human intervention is often unavoidable in traditional decompilers as well [14]. 

In general, our approach to prompt engineering focuses on dynamically constructing prompts that leverage compiler-generated error messages. These messages guide the LLM to iteratively repair defects in the code until it becomes compilable. This process resembles the way human developers debug compilation errors: they first attempt to compile the code and then resolve issues incrementally based on compiler feedback. It is important to note that we do not employ advanced prompting strategies such as chain-of-thought 

9 

_Science of Computer Programming 254 (2026) 103512_ 

_Y. Li, X. Zhang, T. Xu et al._ 

(CoT) reasoning [63]. The rationale for this design decision is that most compilation errors in practice arise from localized and relatively minor oversights in the code. Sophisticated prompt engineering techniques often fail to systematically prevent such errors and can substantially increase computational costs due to the larger number of tokens processed in both input and output. In contrast, compilers provide precise and targeted diagnostics for these common mistakes. As a result, our method achieves a favorable balance between efficiency and cost-effectiveness. 

#### _4.4. Symbolic model based code semantic equivalence checking_ 

The DecIR framework encounters a fundamental challenge in that LLMs cannot ensure the semantic correctness of decompilation outputs. While the proposed decompilation process utilizes a compiler to verify the syntactic validity of decompiled code, it currently lacks mechanisms for tracking and verifying semantic equivalence. Maintaining semantic consistency between decompiled code and the original intermediate representation is crucial, as semantic discrepancies may compromise the accuracy of subsequent reverse engineering tasks. To address this limitation, we propose a formal verification approach based on symbolic execution to check semantic equivalence in LLM-generated decompilation results. 

To verify the semantic equivalence between decompiled code and the original IR, we employ symbolic execution and SMT solving at the IR level. First, the decompiled code is recompiled into an IR ( _𝐼𝑅𝑑𝑒𝑐_ , snippet _d_ in Fig. 3) using the same compilation toolchain that generated the original IR ( _𝐼𝑅𝑜𝑟𝑖𝑔𝑖𝑛𝑎𝑙_ , snippet _b_ in Fig. 3). This step ensures that both representations operate at the same abstraction level, eliminating discrepancies caused by differing intermediate formats. The recompilation process is performed at the function granularity, where each function is treated as an independent code module. This modular approach minimizes inter-procedural dependencies and facilitates parallel analysis, as individual functions can be processed concurrently without requiring extensive access to the entire program structure. 

Subsequently, symbolic models (snippets _a_ and _b_ in Fig. 7) are constructed for both _𝐼𝑅𝑜𝑟𝑖𝑔𝑖𝑛𝑎𝑙_ and _𝐼𝑅𝑑𝑒𝑐_ to formally capture their behavioral semantics. These models abstract function logic into mathematical expressions that systematically map input arguments to return values while accounting for all feasible execution paths. Symbolic execution engines systematically traverse control flow graphs by treating function inputs as symbolic variables and incrementally accumulating path constraints during exploration. To enhance the efficiency of symbolic execution, we limit the number of times each loop is iterated by terminating path exploration once a predefined threshold is reached (set to 2 in our experiments). This allows us to explore more execution paths within a limited timeframe while maintaining the overall accuracy of the analysis [64]. Memory operations are handled through a hybrid modeling approach where symbolic pointers are allocated fixed-size buffers, and memory read/write operations are constrained to prevent unbounded address space exploration. For external function calls, we adopt the same technique as D-helix [62], which synthesizes return values based on the least significant bytes of the corresponding arguments. 

The generated symbolic models are subsequently compared using an SMT solver. For each function pair, the input arguments are unified symbolically, and an assertion (snippet _c_ in Fig. 7) is constructed to verify whether their return values diverge under any valid input assignment. This assertion is encoded as an SMT query, where a satisfiable result indicates semantic inequivalence, whereas an unsatisfiable outcome demonstrates equivalence. To enhance solver performance, redundant constraints are simplified, and shared subexpressions between models are identified to reduce formula complexity. Timeout mechanisms are implemented for complex queries, with unsolved cases conservatively flagged for manual inspection. 

#### **5. Experimental setup** 

In this section, we present several aspects of the experimental setup, including the list of our five research questions (Section 5.1), datasets (Section 5.2), baselines (Section 5.3), evaluation metrics (Section 5.4), and implementation details (Section 5.5). 

#### _5.1. Research questions_ 

Our study revolves around the following five research questions (RQs): 

RQ1: How does DecIR perform in comparison with existing rule-based decompilers? 

RQ2: How does each individual component contribute to the overall performance of DecIR? 

RQ3: How stable are LLM outputs when performing multiple iterations of compilation error repair processes? 

RQ4: How reliable are different semantic equivalence checking methods? 

- RQ5: How consistent is the reliability of DecIR compared to human experts in assessing the functional correctness of LLM-decompiled code? 

#### _5.2. Datasets_ 

We employs two benchmark datasets: ExeBench [20] and Decompile-Eval [21]. ExeBench utilizes an automated toolchain to extract 4.5 million compilable C functions, including 700,000 executable ones, from open-source GitHub repositories. The methodological innovation of this dataset addresses two critical challenges: resolving external type and function dependencies, and generating test cases. Specifically, the approach creates dummy symbols for missing external types and function references in the collected code snippets to ensure compilability. Furthermore, it generates 10 distinct sets of test cases for each C function, which we utilize in our 

10 

_Science of Computer Programming 254 (2026) 103512_ 

_Y. Li, X. Zhang, T. Xu et al._ 



**Fig. 7.** An example of symbolic models. 

experiments to assess the semantic reliability of decompiled code. Decompile-Eval, a recently developed decompilation evaluation benchmark, establishes re-compilability and re-executability as its core evaluation metrics. This dataset builds upon C-language adaptations of the HumanEval programming problem set, which contains 164 programming challenges accompanied by corresponding test assertions. It is important to note that Decompile-Eval differs from ExeBench in its test case implementation, where test cases are embedded within the main function. This implementation restricts test execution outcomes to binary pass/fail results. Consequently, this methodological distinction manifests in our comparative analysis of the two datasets, which we will discuss in greater detail in subsequent sections. 

During the data preprocessing phase, given the specialized requirement of our proposed symbolic execution model for semantic analysis based on function return values, we first filter the original datasets to retain only function samples containing explicit return statements. After this filtering step, 13,092 and 524 valid function samples are extracted from the ExeBench and Decompile-Eval datasets, respectively. We compile each sample using Clang [22] at four optimization levels (O0-O3) to generate corresponding IR variants. The IR snippet extraction follows the methodology outlined in Section 4.2. 

#### _5.3. Baselines_ 

To comprehensively evaluate the effectiveness of our proposed approach, we conduct a systematic comparison with two distinct categories of baseline methods: conventional rule-based decompilers and alternative LLM-based decompilation techniques. 

For traditional rule-based decompilers, we select two representative tools: RetDec [12] and LLVM-CBE [65], both of which support decompiling LLVM IR into C code. Specifically, RetDec is an open-source decompilation framework developed by Avast that supports binary reverse engineering for a wide range of architectures. Its modular design enables decompilation of LLVM IR into humanreadable C code by utilizing a subset of its functionality. LLVM-CBE, which is a component of the LLVM toolchain, specializes in translating LLVM IR into C code. This tool maintains a key advantage in preserving both the control flow structure and type information from the original program. However, it does not prioritize the readability of the decompiled code. 

Current research on LLM-based decompilation lacks studies that directly process IR inputs. Therefore, we adopt two additional prompt strategies inspired by existing work in source code generation. First, we eliminate the iterative process of LLM-based compilation error correction and directly use the initial decompilation result generated by the LLM as the final output. This baseline enables us to evaluate the LLM’s inherent capability when producing a single uncompromised output. Additionally, in an alternative baseline configuration, we replace symbolic model-based semantic equivalence checking with LLM queries while maintaining all other procedures identical to DecIR. For these LLM-driven semantic equivalence assessments, we employ the following prompt: 

11 

_Science of Computer Programming 254 (2026) 103512_ 

_Y. Li, X. Zhang, T. Xu et al._ 

Perform semantic equivalence analysis on these two LLVM IR snippets. 

- First LLVM IR: {IR1} 

- Second LLVM IR: {IR2} 

Requirements: - Compare only the functional behavior 

- Ignore comments, metadata, and formatting differences 

- Output must be exactly one word: “true” if fully equivalent, “false” otherwise 

- No explanations, justifications, or additional output 

#### _5.4. Evaluation metrics_ 

The primary objective of decompilation is to transform low-level code into a semantically equivalent high-level code, thereby facilitating both code analysis and reuse. For analysis purposes, the generated code must exhibit sufficient readability to be comprehensible to human reviewers, whereas for reuse scenarios, the decompiled code must preserve correct semantics to ensure that it can be successfully executed by a machine and produce the intended behavior. Given these two distinct yet equally critical requirements, we establish a multi-dimensional evaluation framework that enables a comprehensive assessment of decompilation quality across different aspects. 

Readability is a subjective criterion primarily concerning human comprehension, which makes it challenging to quantify with fair and comprehensive metrics. Following prior studies [21,23], we employ textual similarity as a proxy measure. This approach assumes that the original source code is highly readable; thus, the readability of decompiled code is approximated by its similarity to the original code, measured by the extent to which the two code snippets share analogous syntactic structures and statements. Specifically, we employ two evaluation metrics: Bilingual Evaluation Understudy (BLEU) [37] and Edit Similarity (ES) [23]. BLEU is a widely adopted metric in natural language processing for assessing the quality of machine-generated text. It calculates a score between 0 and 1 by measuring the n-gram overlap between a candidate text and one or more reference texts, with higher scores indicating better quality. BLEU can be formulated as follows: 



where _𝑠_ 1 represents the reference text, _𝑠_ 2 represents the generated text, _𝑤𝑛_ denotes the weight of n-gram which is set to 1∕ _𝑁_ , and _𝑝𝑛_ represents the precision of n-gram. We set _𝑁_ to 4, meaning that BLEU-4 is adopted. In comparison, ES quantifies the difference between two strings based on the minimum number of edit operations (e.g., insertions, deletions, and substitutions) required to transform one string into the other. This approach is grounded in the concept of edit distance (such as Levenshtein distance), which is then normalized into a similarity score ranging from 0 to 1. A higher ES value likewise reflects a greater degree of similarity and thus better quality. ES can be formulated as follows: 





To mitigate potential bias from variations in code style and comments, all source code is formatted and normalized before similarity metrics are computed. As detailed in Section 4.3, this preprocessing removes superficial discrepancies like irregular indentation, inconsistent whitespace, and non-functional comments. 

In the context of functional semantics evaluation for decompiled code, we conduct assessments across three critical dimensions. First, we examine the compilability (Re-Comp, RC) of decompiled code by attempting to compile it into executable binaries. While the DecIR framework incorporates an iterative error-correction mechanism to resolve compilation issues, our empirical findings demonstrate that some cases still fail to compile even after reaching the maximum allowed iteration count. This observation underscores the importance of evaluating compilation success rates as a fundamental quality metric. Second, for code that successfully compiles, we assess its executability (Re-Exec, RE), which refers to the ability to execute without runtime errors when provided with valid inputs. This evaluation serves as a key indicator of functional integrity at the binary execution level. Finally, for decompiled code that exhibits both compilability and executability, we perform more detailed functional correctness verification through unit testing. Specifically, we utilize the accompanying test cases from the datasets to quantitatively measure input-output accuracy (I/O Acc.), thereby determining whether the decompiled implementations maintain precise behavioral semantics equivalent to the original programs. Note that the I/O Acc. is contingent upon the validity of the test cases used in the evaluation. To assess this, we manually inspect a randomly selected subset of these test cases. A more detailed discussion is provided in Section 7.2. The evaluation metrics mentioned above can be formulated as follows: 





12 

_Science of Computer Programming 254 (2026) 103512_ 

_Y. Li, X. Zhang, T. Xu et al._ 

**Table 1** 

Rule set for code quality assessment. 

|Level|Basic Rule|Extended Rule<sup>1</sup>|
|---|---|---|
|1|RC **and** RE **and** I/O Acc. = 1.0|ES _≻_ BLEU|
|2|RC **and** RE **and** I/O Acc. ≠ 1.0|I/O Acc. _≻_ ES _≻_ BLEU|
|3|RC **and** **not** RE|RE_ERROR<sup>2</sup> _≻_ ES _≻_ BLEU|
|4|**not** RC|RC_ERROR<sup>3</sup> _≻_ RC_ERROR_COUNT<sup>4</sup> _≻_ ES _≻_ BLEU|



> ∗The samples are classified according to the basic rules; for those at the same level, they are then sorted based on the extended rules. 

> 1X _≻_ Y indicates that X takes precedence in sorting; when X values are identical, Y is used as the secondary sorting criterion. 

> 2RE_ERROR ∈{logic_error _,_ timeout _,_ core_dump} is the type of runtime error whose severity follows the order logic_error < timeout < core_dump. 

> 3RC_ERROR ∈{func _,_ whole} is the type of compilation error whose severity follows the order whole < func. 

> 4RC_ERROR_COUNT is the number of compilation errors. 

Beyond the individual evaluation metrics discussed above, we propose a comprehensive comparative criterion named Code Quality (CQ) to enable a holistic ranking of the code generated by different methods for the same task. The CQ criterion is based on a hierarchical, practice-oriented decision model that prioritizes functional correctness. It operates by first comparing code samples based on a multi-level functional hierarchy: 1) passes all test cases (I/O Acc. = 1.0), 2) is executable but does not pass all tests, 3) is compilable but not executable, and 4) is not compilable. This order reflects the principle that functionality is a prerequisite for code quality. For samples within the same hierarchy level, a finer-grained comparison is performed by analyzing the specific reasons preventing advancement to a higher level (e.g., type and count of compilation or runtime errors). Readability metrics (ES and BLEU) are used as a tiebreaker only when all preceding functional comparisons are equal. For a given task, all compared methods are sorted according to this complete rule set, resulting in a relative rank (e.g., best=5, worst=1 if five methods are compared). The final CQ score for a method is the average of its relative ranks across all tasks, where a higher score indicates better average relative performance. The detailed rules of this evaluation scheme are provided in Table 1. 

#### _5.5. Implementation details_ 

Our implementation is primarily developed in Python. For function-level IR extraction, we design a custom Module Pass component using the LLVM (3.8) API framework. This component performs function-level IR extraction and normalization by overriding the `runOnModule()` method, enabling seamless integration with standard LLVM compilation pipelines. For LLM queries, we utilize API services provided by public cloud platform that adhere to OpenAI interface specifications [66]. The models employed in our evaluation include DeepSeek-V3 [67], Qwen2.5-7b-instruct [68], and Qwen-Plus [69]. To check semantic equivalence, we extend and adapt the open-source implementation of D-helix [62]. Specifically, we employ PROMPT [70] to symbolically execute both the original IR and the IR generated from recompiling decompiled code. We then solve the resulting constraints using the Z3 (4.9.1) solver. The source code for DecIR is available at: https://github.com/yuzhanglee/llm_for_dec. 

All our experiments are conducted on the server running Ubuntu 22.04 with 64 processors (Intel(R) Xeon(R) Gold 5218 CPU @ 2.30GHz) and 192GB memory. 

#### **6. Result analysis** 

In this section, we present a comprehensive experimental analysis to address the research questions under investigation, which is organized into four subsections. 

#### _6.1. RQ1: comparison with traditional decompilers_ 

The comparative evaluation results between DecIR and baseline methods are presented in Table 2, where the parameter _𝑇_ denotes the maximum number of retries, and the suffix `(-sym)` indicates configurations utilizing the LLM rather than symbolic models for semantic equivalence checking. 

From the perspective of code readability, the experimental results demonstrate that LLM-based decompilation approaches show significant advantages over traditional methods. All evaluated DecIR variants consistently outperform conventional decompilers by a substantial margin in both BLEU and ES metrics, achieving at least two-fold improvements across both benchmark datasets. The results demonstrate that LLM-based decompilation effectively bridges the semantic gap between low-level and high-level code by recovering sophisticated program semantics that conventional decompilers typically fail to restore. Leveraging their advanced pattern recognition capabilities, LLMs reconstruct high-level abstractions from compiled code, including complex control structures and data types that traditional approaches often overlook. This process goes beyond mere syntactic translation by capturing both the programmer’s intent and the computational patterns present in the original source code before compilation. 

13 

_Science of Computer Programming 254 (2026) 103512_ 

_Y. Li, X. Zhang, T. Xu et al._ 

**Table 2** 

Comparison of DecIR and baseline methods. 

|Method|ExeBenc|h||||Decompi|le-Eval|||
|---|---|---|---|---|---|---|---|---|---|
||BLEU|ES|RC<sup>1</sup>|RE<sup>1</sup>|I/O Acc.<sup>1</sup>|BLEU|ES|RC|RE<sup>2</sup>|
|RetDec|7.30|12.01|89.65|83.08|64.48|2.43|20.57|84.54|84.54|
|LLVM-CBE|2.85|18.36|**100.0**|**100.0**|**100.0**|0.04|7.33|**100.0**|**100.0**|
|(DeepSeek-V3)||||||||||
|DecIR_𝑇_=1<br>3|**21.10**|30.81|75.33|74.69|73.42|57.76|57.27|97.63|97.63|
|DecIR_𝑇_=5|21.09|31.27|83.14|82.52|74.83|**57.79**|**57.34**|**100.0**|**100.0**|
|DecIR_𝑇_=10|**21.10**|**31.28**|83.22|82.60|81.35|**57.79**|**57.34**|**100.0**|100.0|
|DecIR_𝑇_=10 (-sym)<sup>4</sup>|**21.10**|**31.28**|83.22|69.69|66.60|**57.79**|**57.34**|**100.0**|92.24|
|(Qwen-Plus)||||||||||
|DecIR_𝑇_=1|18.67|28.57|55.46|55.46|46.71|46.87|49.16|86.79|86.79|
|DecIR_𝑇_=5|18.76|28.41|70.11|69.69|60.82|46.95|49.42|96.45|90.42|
|DecIR_𝑇_=10|18.76|28.40|70.27|69.85|61.02|46.95|49.42|97.04|90.98|
|DecIR_𝑇_=10 (-sym)|18.76|28.40|70.27|50.25|42.76|46.95|49.42|97.04|69.19|
|(Qwen2.5-7b)||||||||||
|DecIR_𝑇_=1|14.47|25.48|41.53|39.95|21.42|29.19|36.09|60.47|51.82|
|DecIR_𝑇_=5|14.84|26.19|67.18|64.53|35.44|30.56|36.95|86.79|63.11|
|DecIR_𝑇_=10|14.83|26.97|68.57|65.95|36.77|30.56|36.91|88.95|64.68|
|DecIR_𝑇_=10 (-sym)|14.83|26.97|68.57|51.77|30.79|30.56|36.91|88.95|43.67|



> ∗The units of the above data are all in percentage (%). 

> 1RC = Re-Compilability, RE = Re-Executability, I/O Acc. = Input-Output Accuracy (as described in Section 5.4). 

> 2The RE results on the Decompile-Eval dataset also represent I/O Acc. because the unit tests are integrated into the main program (as described in Section 5.2), this design leads to execution failure when test cases fail. 

> 3 _𝑇_ = _𝑛_ denotes the maximum number of retries. 

> 4 `(-sym)` represents using the LLM to check semantic equivalence instead of the proposed symbolic modelbased method. 

**Table 3** Results of code quality (CQ) across DecIR and baseline methods. 

|Model|ExeBench<sup>1</sup>|Decompile-Eval<sup>2</sup>|
|---|---|---|
|RetDec|2.44|2.25|
|LLVM-CBE|**3.47**|1.25|
|DecIR_𝑇_=10 (DeepSeek-V3)|3.41|**4.58**|
|DecIR_𝑇_=10 (Qwen-Plus)|3.24|3.67|
|DecIR_𝑇_=10 (Qwen2.5-7b)|2.44|3.25|



> 1Friedman test: _𝜒_ 2 = 204 _._ 684, _𝑝<_ 0 _._ 05. 

> 2Friedman test: _𝜒_ 2 = 31 _._ 867, _𝑝<_ 0 _._ 05. 

From the perspective of functional semantics, the DecIR variant that employs DeepSeek-V3 as its underlying LLM exhibits superior performance across all code evaluation metrics when compared to RetDec. Specifically, it achieves perfect accuracy (100%) on the Decompile-Eval dataset. In contrast, RetDec attains a maximum re-executable rate of only 84.54% on both datasets, which suggests that the predefined heuristic rules utilized by traditional decompilers are inherently imperfect. Nevertheless, this performance remains marginally lower than that of LLVM-CBE, which maintains perfect accuracy across both evaluated datasets. The observed performance disparity can be theoretically explained by the fact that LLVM-CBE is specifically optimized to generate C code that preserves strict semantic equivalence with the input IR code. This design prioritizes semantic preservation at the expense of code readability, a trade-off that is further supported by its comparatively weaker performance on readability metrics. 

To evaluate the performance differences between DecIR and the baseline methods, we conduct a Friedman test on the CQ scores (as detailed in Section 5.4). In this non-parametric test, each function from the benchmark datasets is treated as an independent block. The data are arranged into a matrix where rows represent the blocks (i.e., functions), columns correspond to the different methods (DecIR and the baselines), and each cell contains the CQ score achieved by a given method on the corresponding function. This design satisfies the requirement of statistical independence between blocks. We thus test the null hypothesis that there is no significant performance difference among all compared methods over the entire set of functions. The result of the Friedman test is statistically significant (Table 3), indicating that the performance distributions differ significantly across the methods. Subsequently, the Nemenyi post-hoc test reveals that, on the ExeBench dataset, DecIR _𝑇_ =10 (DeepSeek-V3) significantly outperforms RetDec (p < 0.05). On the Decompile-Eval dataset, DecIR _𝑇_ =10 (DeepSeek-V3) achieves significantly better results than both RetDec and LLVM-CBE (p < 0.05 for both comparisons). The detailed statistical significance outcomes are further illustrated in Fig. 8. 

14 

_Science of Computer Programming 254 (2026) 103512_ 

_Y. Li, X. Zhang, T. Xu et al._ 



**Fig. 8.** Heatmap of the Nemenyi post-hoc test _𝑝_ -values for Code Quality (CQ) across DecIR and baseline methods. 

**Summary for RQ1** : Our proposed DecIR framework effectively balances code readability and semantic consistency, significantly enhancing human comprehension and reuse of decompiled code. The experimental results confirm that DecIR surpasses conventional decompilers like RetDec in terms of both output quality and practical usability. This performance advantage demonstrates the potential of DecIR for practical application and provides a solid foundation for future exploration of its efficacy in real-world, complex reverse engineering scenarios. 

#### _6.2. RQ2: ablation study_ 

To assess the contribution of each component in our proposed DecIR workflow, we conduct a comprehensive ablation study. The experimental design examines two key aspects: (1) the performance variation when adjusting the number of retry attempts _𝑇_ ∈{1 _,_ 5 _,_ 10}, and (2) the comparison between scenarios where _𝑇_ = 10 with symbolic model-based equivalence checking versus scenarios that rely solely on LLM queries for equivalence checking. We evaluate these configurations across three different LLMs, with the detailed results presented in Table 2. 

The primary observation reveals that the choice of underlying LLM significantly impacts the quality of decompilation results. For instance, in the ExeBench dataset, DecIR _𝑇_ =10 (DeepSeek-V3) achieves an average code quality score that is approximately 1 _._ 4× higher than that of DecIR _𝑇_ =10 (Qwen2.5-7b). This performance gap is statistically significant, as supported by the results summarized in Table 3 and illustrated in Fig. 8. This substantial discrepancy can be attributed to fundamental differences in model architectures, training objectives, and parameter scales among various LLMs. This finding underscores the critical importance of carefully selecting appropriate LLM for achieving high-quality LLM-based decompilation. 

Through extensive analysis of different _𝑇_ values, we observe a consistent improvement in functional semantic metrics as the number of allowed retry attempts increased. In the DeepSeek-V3 experimental group, for example, setting _𝑇_ = 10 yields approximately 9% higher IO accuracy on the Exebench dataset compared to _𝑇_ = 5, while maintaining stable readability metrics throughout the process. This suggests that our iterative refinement mechanism effectively enhances functional correctness without compromising code readability. However, it is important to note that increasing the permitted number of retries leads to a linear growth in the computational load required by the process. To quantify this relationship, we define the token cost as the total number of tokens consumed during a single LLM query for a given function, which includes both the prompt and the model completion. Fig. 9 presents the relationship between the average token cost across all tested functions and the number of iterations. Here, _𝑇_ = 0 denotes the token cost incurred by a single LLM-based decompilation query without iterative refinement. As shown in Fig. 9, the required token cost rises in sync with an increasing number of retries. This trend suggests that, in practical applications, the maximum number of retries must be carefully balanced against other considerations, including available computing resources, time constraints, and accuracy requirements, to ensure feasible and efficient deployment. 

However, replacing symbolic model-based equivalence checking with LLM query-based verification results in significant performance degradation. The Qwen-Plus experimental group exhibits substantial drops in IO accuracy (approximately 30% and 24% across two benchmark datasets). This deterioration indicates that current LLMs struggle to reliably assess semantic equivalence through their internal multi-agent collaboration mechanisms, particularly in the context of decompilation tasks. Notably, in both DeepSeek-V3 and Qwen-Plus experimental groups, DecIR _𝑇_ =10 (using LLM-based equivalence checking) underperforms DecIR _𝑇_ =1, suggesting that LLMderived semantic judgments can misguide the iterative optimization process and negatively impact the overall decompilation quality. 

**Summary for RQ2** : Our proposed enhancement strategy, which combines iterative retry mechanisms with symbolic model-based equivalence checking, significantly improves the quality of LLM-based decompilation results when implemented on high-performance foundation models. 

15 

_Science of Computer Programming 254 (2026) 103512_ 

_Y. Li, X. Zhang, T. Xu et al._ 



**Fig. 9.** Average token cost vs. number of iterations for different LLMs. 

#### _6.3. RQ3: LLM iteration stability_ 

To examine whether LLMs can effectively concentrate on localized modifications at compiler-reported error positions during iterative repair processes, we conduct a comprehensive analysis of intermediate repair outcomes. This investigation is motivated by the observation that global code restructuring may lead to divergent iterations, which could compromise both efficiency and result reliability. Since these intermediate results are not directly compilable, we employs source code-level textual similarity metrics for quantitative assessment. Specifically, we quantify the stability of the iterative code repair process by measuring the similarity between the code outputs generated by the LLM in consecutive iterations. For a given decompiled code snippet targeted for repair, the entire iterative process produces a sequence of code versions. The stability of this process, denoted as _𝑆_<sup>∗</sup> ( _𝑠_ ) for a code sequence _𝑠_ =<sup>{</sup> _𝑠𝑡_ ∣ _𝑡_ ∈{1 _,_ … _, 𝑇_ }<sup>}</sup> , is formally defined as follows: 







where the coefficient _𝑤_ serves as a normalization factor, while _𝑒_ ∈(0 _,_ 1] functions as a penalty term applied to the similarity metric. This penalty is introduced because a similarity value of 1 in the iterative repair process indicates that no modification has been made. By incorporating this penalty, we adjust the evaluation to more accurately reflect the actual effectiveness of the repair. During our experimental assessment, the relevant parameters are configured as follows: _𝑤𝐵𝐿𝐸𝑈_ = 0 _._ 5, _𝑤𝐸𝑆_ = 0 _._ 5, _𝑒𝐵𝐿𝐸𝑈_ = 0 _._ 9 and _𝑒𝐸𝑆_ = 0 _._ 9. This configuration indicates that both BLEU and ES are assigned equal importance in the overall assessment. Furthermore, a modification rate of 90% is considered optimal for both metrics. 

The experimental results, presented as violin plots in Fig. 10, illustrate the varying stability of different LLMs in iterative repair tasks. DeepSeek-V3 demonstrates the most favorable performance, with its stability values predominantly concentrated near 1. It achieves the highest mean stability score of 0.98, indicating highly consistent and localized code modifications. Qwen-Plus exhibits the second-best performance; although its stability distribution remains unimodal, the values are slightly more dispersed compared to DeepSeek-V3, yielding a mean stability of 0.92. In contrast, Qwen2.5-7b displays a distinct bimodal distribution in its stability score, with a considerably lower mean value of 0.70. This pattern suggests that for a substantial subset of code samples, Qwen2.5-7b tends to apply non-localized code transformations rather than minimal edits aimed at resolving compilation errors. Such behavior deviates from the expected repair strategy, which prioritizes localized modifications to ensure minimal deviation from the original program structure. 

Furthermore, to investigate the indicative significance of stability, we conduct a correlation analysis to examine the relationship between iterative stability and the overall effectiveness of the method. Specifically, we measure the stability ( _𝑆_<sup>∗</sup> ) of the code generated 

16 

_Science of Computer Programming 254 (2026) 103512_ 

_Y. Li, X. Zhang, T. Xu et al._ 



**Fig. 10.** Results of LLM iteration stability. 

by the LLM across iterations and correlate it with the final compilation outcome (1 = pass, 0 = fail). A point-biserial correlation analysis reveals a statistically significant and strong positive correlation between compilation success and iterative stability (on dataset ExeBench: _𝑟_ = 0 _._ 617, _𝑝<_ 0 _._ 001; on dataset Decompile-Eval: _𝑟_ = 0 _._ 623, _𝑝<_ 0 _._ 001). This result suggests that LLMs with higher iterative stability are more likely to produce compilable code, implying that maintaining structural consistency during iterative refinement plays a critical role in achieving high-quality outputs. This observation is qualitatively supported by the results presented in Table 2, which shows that the LLM with the highest iterative stability (DeepSeek-V3) also achieves the highest overall performance, followed by Qwen-Plus and Qwen2.5-7b. 

**Summary for RQ3** : Our experiments demonstrate that the iterative stability of an LLM is closely tied to its inherent capabilities. Consequently, our findings establish iterative stability as a valuable metric for evaluating and selecting LLMs in code repair scenarios. Given the significant disparities in stability observed across different models, prioritizing this criterion is crucial for achieving optimal performance. 

#### _6.4. RQ4: reliability of semantic equivalence checking_ 

A core contribution of DecIR lies in its adoption of semantic equivalence checking, which relies on symbolic models rather than equivalence judgments derived from LLM queries. To evaluate the reliability of various semantic equivalence checking methods, we construct a specialized dataset based on semantic equivalence principles. Specifically, we select a subset of 2000 samples from the datasets described in Section 5.2 according to the following criteria: (1) For semantically equivalent samples, we randomly collect multiple variants of identical functions compiled at different optimization levels. This selection strategy is theoretically sound because compiler optimizations, while modifying low-level implementation details, are designed to preserve program semantics. These samples consequently serve as reliable equivalent cases for validation. (2) For semantically inequivalent samples, we deliberately pair functionally distinct implementations compiled at randomly selected optimization levels. These pairs are inherently semantically different since they implement divergent computational logic and exhibit contrasting behavioral characteristics. 

As shown in Table 4, we present a comprehensive comparative analysis of various semantic equivalence checking approaches. The experimental results indicate that the symbolic model-based approach (SymDiff) achieves superior recall rates across both datasets, including perfect 100% recall on the Decompile-Eval dataset. In contrast, while LLM-based approaches (DeepSeek-V3/Qwen2.57b/Qwen-Plus) demonstrate perfect precision (100% in all cases), their suboptimal recall performance suggests these models may exhibit a bias toward classifying code pairs as semantically equivalent. From a reliability perspective, recall is more critical than precision in semantic equivalence checking. A low precision rate, indicating a higher number of false positives, means that semantically equivalent code snippets are incorrectly deemed inequivalent. Since such results are either discarded for regeneration or reported as timeouts, false positives primarily increase workflow overhead without directly corrupting the final output. In contrast, a low recall rate implies a higher incidence of false negatives, where semantically different code is incorrectly judged as equivalent. These erroneous results, however, are accepted and returned to the user. Consequently, false negatives are considerably more detrimental, 

17 

_Science of Computer Programming 254 (2026) 103512_ 

_Y. Li, X. Zhang, T. Xu et al._ 

**Table 4** 

Comparison of different semantic equivalence checking methods. 

|Method|ExeBench||||Decompile-|Eval|||
|---|---|---|---|---|---|---|---|---|
||Accuracy|Precision|Recall|F1|Accuracy|Precision|Recall|F1|
|SymDif|92.11|92.79|**98.26**|95.46|**100.0**|**100.0**|**100.0**|**100.0**|
|DeepSeek-V3|**98.00**|**100.0**|96.00|**97.96**|94.66|**100.0**|89.31|94.35|
|Qwen2.5-7b|92.40|**100.0**|84.80|91.77|77.48|**100.0**|54.96|70.93|
|Qwen-Plus|95.60|**100.0**|91.20|95.40|85.11|**100.0**|70.23|82.51|



> ∗The units of the above data are all in percentage (%). 

**Table 5** 

Agreement matrix between DecIR and human expert evaluation. 

|Role|Expert (correct)|Expert (incorrect)|Total|
|---|---|---|---|
|**DecIR** **(pass)**|43|7|50|
|**DecIR** **(fail)**|4|46|50|
|**Total**|47|53|100|



Cohen’s Kappa: _𝜅_ = 0 _._ 78. 

as they directly compromise the output’s correctness and thus the trustworthiness of the entire workflow. The experimental results thus provide compelling evidence that symbolic model-based semantic equivalence checking offers substantial advantages over LLMbased alternatives in terms of both effectiveness and reliability. The superior performance of symbolic methods can be attributed to their rigorous formal analysis capabilities, which systematically explore the semantic space of program behaviors. LLM-based approaches, despite their promising precision, appear limited by their tendency to produce conservative judgments, potentially due to their training on predominantly correct code examples. 

**Summary for RQ4** : Our proposed symbolic model-based approach for semantic equivalence checking achieves the objective of minimizing false negatives, thereby significantly enhancing the reliability of LLM-assisted decompilation processes. This methodology establishes a rigorous framework for validating the semantic consistency between original and decompiled code, addressing a critical challenge in reverse engineering applications. 

#### _6.5. RQ5: agreement with human evaluation_ 

To assess the reliability of DecIR from an external perspective, we conduct a manual validation experiment that compares its judgments with independent evaluations from human experts. This experiment begins with randomly sampling 100 code snippets checked by DecIR from the dataset, balancing cases judged as “pass” and “fail” to cover diverse scenarios. Subsequently, three independent software engineering experts, uninvolved in this study, are invited to perform independent reviews. The anonymized samples include both the original and the LLM-generated decompiled code. Without knowledge of DecIR’s determinations, the experts perform a binary assessment of functional correctness, classifying each sample as correct or incorrect based on semantic equivalence. This assessment criterion aligns strictly with DecIR’s “pass/fail” logic. Throughout the review process, communication among experts remains prohibited to ensure independence. 

The agreement between DecIR’s judgments and the expert evaluation results (using majority voting) is shown in Table 5. We use Cohen’s Kappa coefficient ( _𝜅_ ) to measure their agreement, a metric that accounts for chance agreement. Based on the table data, _𝜅_ is calculated to be 0.78. According to Landis and Koch’s benchmarks for strength of agreement, this value falls within the 0.61-0.80 range, indicating a substantial agreement. Among the 100 samples, there were 11 cases of disagreement. We perform a root-cause analysis on these inconsistent cases: 

**DecIR Pass but Expert Incorrect (7 cases)** : For 5 of these, the disagreement can be attributed to the more comprehensive path coverage achieved by DecIR’s symbolic execution, whereas the experts fail to exhaust all boundary conditions during their review. This highlights the advantage of formal verification in terms of coverage and objectivity. The remaining 2 cases stem from DecIR’s failure to model certain function side effects (this limitation will be discussed in Section 7.1). 

**DecIR Fail but Expert Correct (4 cases)** : These cases are primarily caused by the overly conservative constraints applied by the symbolic execution on function inputs, leading to the false rejection of otherwise acceptable code [71]. This points to a direction for future improvements in verification precision. 

**Summary for RQ5** : The substantial agreement ( _𝜅_ = 0 _._ 78) between DecIR and human experts confirms its reliability for verifying LLM-decompiled code, supporting its use in assisting or partially replacing manual inspection. Disagreements stem from human cognitive biases under time constraints versus the tool’s inherent limitations in path/model completeness, highlighting their complementary roles in practice. 

#### **7. Discussion** 

In this section, we discuss the limitations of our work (Section 7.1) followed by threats to validity (Section 7.2). 

18 

_Science of Computer Programming 254 (2026) 103512_ 

_Y. Li, X. Zhang, T. Xu et al._ 

#### _7.1. Limitations_ 

While LLMs show significant promise in processing human-readable source code, their application to decompilation tasks presents distinct challenges. Unlike conventional rule-based decompilers [11,12] that allow engineers to verify outputs through examination of underlying heuristic rules, the inherent opacity of LLMs makes their decompilation results difficult to interpret. This limitation becomes particularly evident when LLMs generate hallucinated content that appears plausible but contains factually incorrect code snippets. Our experimental results demonstrate that developing reliable deterministic verification mechanisms remains crucial for LLM-based decompilation systems. 

The primary limitation arises from our symbolic modeling technique’s dependence on function return statements. This methodology inherently struggles to analyze void functions, as they lack explicit return values required for symbolic model construction. Furthermore, even for non-void functions, the modeling accuracy may be compromised if a function’s behavior is primarily realized through side effects, such as modifications to global variables or system state. A notable example is the `main` function: although it conventionally returns an integer indicating the program termination status, this return value often carries limited semantic weight, since the core functionality is largely achieved via side effects. Consequently, analyzing the return value alone is insufficient for comprehensive semantic verification, as the meaningful program behavior is more frequently embodied in side effects and execution traces. 

The second limitation concerns the computational complexity of symbolic analysis when applied to functions with intricate control flow structures. This approach becomes particularly resource-intensive when handling conditional branches and loop constructs, where path explosion leads to an exponential increase in potential execution paths. For highly complex functions, symbolic analysis may demand prohibitive computational resources, potentially exceeding practical operational constraints in real-world scenarios. 

In summary, although our symbolic model-based semantic equivalence checking approach substantially improves the trustworthiness of decompilation results, several limitations persist which present significant research opportunities. Future work should prioritize the development of more robust symbolic modeling techniques capable of handling diverse function types while simultaneously optimizing symbolic analysis performance for complex decompilation scenarios. 

#### _7.2. Threats to validity_ 

Threats to validity represent potential factors that could affect the reliability of our experimental conclusions. These primarily concern construct validity (Section 7.2.1), which examines whether our measurements accurately reflect the theoretical constructs, and external validity (Section 7.2.2), which determines the generalizability of our findings. 

#### _7.2.1. Construct validity_ 

For code-based evaluation, we employ I/O accuracy as the key metric, which measures semantic equivalence by verifying behavioral consistency between decompiled and original code through a comprehensive test suite. Although this unit testing approach is widely adopted in the field, its effectiveness inherently relies on test case coverage adequacy. Inadequate test coverage may lead to undetected semantic discrepancies in the decompiled code. To mitigate this concern, we conduct a manual assessment by randomly selecting 100 test cases from the datasets described in Section 5.2. The results confirm that all inspected cases satisfy the expected functional and semantic criteria. Based on this analysis, we conclude that the test cases in the datasets are generally reliable. Consequently, the I/O accuracy metric derived from these test cases can be considered a trustworthy indicator for evaluating the semantic equivalence between original and decompiled code. 

#### _7.2.2. External validity_ 

When assessing the external validity of our approach, four key factors require careful consideration. First, version compatibility issues in LLVM IR, which serves as the input to our approach, may affect semantic recognition. Since LLVM IR exhibits semantic variations across different versions, we conduct all experiments using LLVM 3.8 to ensure reliability and reproducibility, as described in Section 5.5. Second, the selection of LLMs impacts the experimental results. Although various open-source and proprietary LLMs exist, each demonstrating strengths in specific tasks, we choose DeepSeek [67] and Qwen [68,69] as representative models. It is important to note that our technique remains independent of the underlying LLM, as its primary contribution involves utilizing program analysis to enhance and verify LLM outputs. Third, we select C as the target high-level language for decompilation, a choice made to align with conventional decompilers and thereby facilitate a consistent and fair evaluation. It is important to note, however, that the proposed method itself is not inherently restricted to C; it can be generalized to other high-level languages as well. The process of adapting our decompilation framework to a different language depends primarily on whether the corresponding compiler infrastructure is capable of generating an IR that is amenable to symbolic execution, such as LLVM IR. This requirement highlights the reliance on mature compiler tooling for effective generalization. Currently, our approach is applicable to several widely-used highlevel languages, including C/C++, Go, Rust, and Java, whereas support for additional languages may be constrained by limitations in the underlying software infrastructure. Fourth, we conduct experimental evaluations on two benchmark datasets, ExeBench and Decompile-Eval. Our choice is motivated by their established use in prior decompilation research [21,23] and their built-in support for unit tests, which facilitates systematic validation. However, it should be noted that these benchmarks, though derived from realworld code, comprise intentionally curated snippets with limited scale and complexity. To address scenarios involving larger and more realistic codebases, we employ a function-grained divide-and-conquer strategy, ensuring effective and scalable processing. 

19 

_Science of Computer Programming 254 (2026) 103512_ 

_Y. Li, X. Zhang, T. Xu et al._ 

#### **8. Conclusion** 

In this paper, we present DecIR, a novel decompilation framework that leverages LLMs. Our approach combines the advanced code generation capabilities of LLMs with conventional program analysis techniques to produce highly reliable decompilation results. DecIR employs an iterative process wherein the LLM performs decompilation tasks through multiple invocations while compiler-guided automated error detection occurs during each iteration. The framework implements rigorous semantic equivalence checking based on symbolic models to validate the correctness of decompilation outputs. A distinctive feature of DecIR is its specialized focus on LLVM IR, which capitalizes on the universal nature of LLVM IR as the intermediate representation within LLVM toolchains. This design facilitates seamless integration between the LLM and existing LLVM toolchains, thereby significantly enhancing the framework’s compatibility and extensibility. Our experimental results demonstrate that DecIR effectively improves the quality of decompiled code generated by LLMs, particularly in terms of compilability and executability, thus advancing the applicability of LLMs in decompilation tasks. However, we also identify trade-offs between performance bottlenecks and completeness in the employed program analysis method. For future work, we plan to optimize the construction of symbolic models for equivalence checking, which will further enhance the practicality of LLM-based decompilation methods in real-world scenarios. 

#### **Declaration of generative AI and AI-assisted technologies in the writing process** 

During the preparation of this work the authors used DeepSeek in order to improve language and readability. After using this tool, the authors reviewed and edited the content as needed and take full responsibility for the content of the published article. 

#### **CRediT authorship contribution statement** 

**Yuzhang Li:** Writing – review & editing, Writing – original draft, Software, Methodology, Investigation, Conceptualization; **Xi Zhang:** Writing – review & editing, Supervision, Conceptualization; **Tao Xu:** Writing – review & editing, Conceptualization; **Chunlu Wang:** Writing – review & editing, Supervision, Conceptualization. 

#### **Declaration of competing interest** 

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper. 

#### **Acknowledgements** 

This research is supported by Key Laboratory of Trustworthy Distributed Computing and Service, MoE (Beijing University of Posts and Telecommunications). We wish to thank the editor for their assistance and oversight during the review process. We are also profoundly grateful to the anonymous reviewers for their time and expertise. Their insightful comments and constructive criticisms were invaluable in significantly improving the manuscript’s clarity, depth, and overall quality. 

#### **References** 

- [1] S. Dinesh, N. Burow, D. Xu, M. Payer, RetroWrite: statically instrumenting COTS binaries for fuzzing and sanitization, in: 2020 IEEE Symposium on Security and Privacy (SP), 2020, pp. 1497–1511. https://doi.org/10.1109/SP40000.2020.00009 

- [2] S. Nagy, A. Nguyen-Tuong, J.D. Hiser, J.W. Davidson, M. Hicks, Breaking through binaries: compiler-quality instrumentation for better binary-only fuzzing, in: 30th USENIX Security Symposium (USENIX Security 21), USENIX Association, 2021, pp. 1683–1700. https://www.usenix.org/conference/usenixsecurity21/ presentation/nagy. 

- [3] Stantinko’s new cryptominer features unique obfuscation techniques, 2020, https://www.welivesecurity.com/2020/03/19/stantinko-new-cryptominer-uniqueobfuscation-techniques. Accessed April 10, 2025. 

- [4] A deep-dive into the SolarWinds Serv-U SSH vulnerability, 2021, (https://www.microsoft.com/en-us/security/blog/2021/09/02/a-deep-dive-into-thesolarwinds-serv-u-ssh-vulnerability). Accessed April 10, 2025. 

- [5] J. Lee, T. Avgerinos, D. Brumley, TIE: principled reverse engineering of types in binary programs, in: Proceedings of the Network and Distributed System Security Symposium, NDSS 2011, San Diego, California, USA, 6th February-9th February 2011, The Internet Society, 2011. https://www.ndsssymposium.org/ndss2011/tie-principled-reverse-engineering-of-types-in-binary-programs. 

- [6] J. Lacomis, P. Yin, E.J. Schwartz, M. Allamanis, C. Le Goues, G. Neubig, B. Vasilescu, DIRE: a neural approach to decompiled identifier naming, in: Proceedings of the 34th IEEE/ACM International Conference on Automated Software Engineering, ASE ’19, IEEE Press, 2020, p. 628–639. https://doi.org/10.1109/ASE. 2019.00064 

- [7] Z. Zhang, Y. Ye, W. You, G. Tao, W.-c. Lee, Y. Kwon, Y. Aafer, X. Zhang, OSPREY: recovery of variable and data structure via probabilistic analysis for stripped binary, in: 2021 IEEE Symposium on Security and Privacy (SP), 2021, pp. 813–832. https://doi.org/10.1109/SP40001.2021.00051 

- [8] K. Pei, J. Guan, M. Broughton, Z. Chen, S. Yao, D. Williams-King, V. Ummadisetty, J. Yang, B. Ray, S. Jana, StateFormer: fine-grained type recovery from binaries using generative state modeling, in: Proceedings of the 29th ACM Joint Meeting on European Software Engineering Conference and Symposium on the Foundations of Software Engineering, ESEC/FSE 2021, Association for Computing Machinery, New York, NY, USA, 2021, p. 690–702. https://doi.org/10.1145/ 3468264.3468607 

- [9] Q. Chen, J. Lacomis, E.J. Schwartz, C.L. Goues, G. Neubig, B. Vasilescu, Augmenting decompiler output with learned variable names and types, in: 31st USENIX Security Symposium (USENIX Security 22), USENIX Association, Boston, MA, 2022, pp. 4327–4343. https://www.usenix.org/conference/usenixsecurity22/ presentation/chen-qibin. 

- [10] IDA pro: a powerful disassembler and a versatile debugger, 2025, (https://hex-rays.com/ida-pro). Accessed April 10, 2025. 

- [11] Ghidra software reverse engineering framework, 2019, (https://github.com/NationalSecurityAgency/ghidra). Accessed April 10, 2025. 

- [12] RetDec: retargetable machine-code decompiler based on LLVM, 2017, (https://github.com/avast/retdec). Accessed April 10, 2025. 

20 

_Science of Computer Programming 254 (2026) 103512_ 

_Y. Li, X. Zhang, T. Xu et al._ 

- [13] O. Katz, Y. Olshaker, Y. Goldberg, E. Yahav, et al., Towards neural decompilation, 2019, http://arxiv.org/abs/1905.08325. 

- [14] C. Fu, H. Chen, H. Liu, X. Chen, Y. Tian, F. Koushanfar, J. Zhao, Coda: An End-to-End Neural Program Decompiler, Curran Associates Inc., Red Hook, NY, USA, 2019. 

- [15] P. Hu, R. Liang, K. Chen, et al., DeGPT: optimizing decompiler output with LLM, in: Proceedings 2024 Network and Distributed System Security Symposium, Internet Society, San Diego, CA, USA, 2024. https://www.ndss-symposium.org/wp-content/uploads/2024-401-paper.pdf. 

- [16] W.K. Wong, H. Wang, Z. Li, Z. Liu, S. Wang, Q. Tang, S. Nie, S. Wu, et al., Refining decompiled C code with large language models, 2023, http://arxiv.org/abs/ 2310.06530. 

- [17] X. Xu, Z. Zhang, S. Feng, Y. Ye, Z. Su, N. Jiang, S. Cheng, L. Tan, X. Zhang, et al., LmPa: improving decompilation by synergy of large language model and program analysis, 2023, http://arxiv.org/abs/2306.02546. 

- [18] The LLVM compiler infrastructure, 2003, (https://llvm.org). Accessed April 10, 2025. 

- [19] L. De Moura, N. Bjørner, Satisfiability modulo theories: introduction and applications, Commun. ACM 54 (9) (2011) 69–77. https://doi.org/10.1145/1995376. 1995394 

- [20] J. Armengol-Estapé, J. Woodruff, A. Brauckmann, M.a. J.W. de Souza, M.F.P. O’Boyle, ExeBench: an ML-scale dataset of executable C functions, in: Proceedings of the 6th ACM SIGPLAN International Symposium on Machine Programming, MAPS 2022, Association for Computing Machinery, New York, NY, USA, 2022, p. 50–59. https://doi.org/10.1145/3520312.3534867 

- [21] H. Tan, Q. Luo, J. Li, Y. Zhang, LLM4Decompile: decompiling binary code with large language models, 2024, 2403.05286 

- [22] Clang: a C language family frontend for LLVM, 2007, (https://clang.llvm.org). Accessed April 10, 2025. 

- [23] J. Armengol-Estapé, J. Woodruff, C. Cummins, M.F.P. O’Boyle, et al., SLaDe: a portable small language model decompiler for optimized assembly, in: 2024 IEEE/ACM International Symposium on Code Generation and Optimization (CGO), IEEE, Edinburgh, United Kingdom, 2024, pp. 67–80. https://ieeexplore.ieee. org/document/10444788/. 

- [24] E.J. Schwartz, J. Lee, M. Woo, D. Brumley, Native ×86 decompilation using semantics-preserving structural analysis and iterative control-flow structuring, in: Proceedings of the 22nd USENIX Conference on Security, SEC’13, USENIX Association, USA, 2013, p. 353–368. 

- [25] K. Cho, B. van Merriënboer, D. Bahdanau, Y. Bengio, On the properties of neural machine translation: encoder–decoder approaches, in: D. Wu, M. Carpuat, X. Carreras, E.M. Vecchi (Eds.), Proceedings of SSST-8, Eighth Workshop on Syntax, Semantics and Structure in Statistical Translation, Association for Computational Linguistics, Doha, Qatar, 2014, pp. 103–111. https://aclanthology.org/W14-4012/. 

- [26] N. Kalchbrenner, P. Blunsom, Recurrent continuous translation models, in: D. Yarowsky, T. Baldwin, A. Korhonen, K. Livescu, S. Bethard (Eds.), Proceedings of the 2013 Conference on Empirical Methods in Natural Language Processing, Association for Computational Linguistics, Seattle, Washington, USA, 2013, pp. 1700–1709. https://aclanthology.org/D13-1176/. 

- [27] I. Hosseini, B. Dolan-Gavitt, Beyond the C: retargetable decompilation using neural machine translation, in: Proceedings 2022 Workshop on Binary Analysis Research, BAR 2022, Internet Society, 2022. https://doi.org/10.14722/bar.2022.23009 

- [28] A. Al-Kaswan, T. Ahmed, M. Izadi, A.A. Sawant, P. Devanbu, A. Van Deursen, et al., Extending source code pre-trained language models to summarise decompiled binaries, in: 2023 IEEE International Conference on Software Analysis, Evolution and Reengineering (SANER), IEEE, Taipa, Macao, 2023, pp. 260–271. https: //ieeexplore.ieee.org/document/10123452/. 

- [29] J. Devlin, M.-W. Chang, K. Lee, K. Toutanova, BERT: pre-training of deep bidirectional transformers for language understanding, 2019, 1810.04805 

- [30] Y. Wang, W. Wang, S. Joty, S.C.H. Hoi, CodeT5: identifier-aware unified pre-trained encoder-decoder models for code understanding and generation, in: Proceedings of the 2021 Conference on Empirical Methods in Natural Language Processing, 2021, pp. 8696–8708. 

- [31] N. Jiang, C. Wang, K. Liu, X. Xu, L. Tan, X. Zhang, Nova<sup>+</sup> : generative language models for binaries, 2023, 2311.13721 

- [32] M.H. Halstead, Elements of Software Science (Operating and Programming Systems Series), Elsevier Science Inc., USA, 1977. 

- [33] H. Tan, Q. Luo, J. Li, Y. Zhang, LLM4Decompile: decompiling binary code with large language models, in: Y. Al-Onaizan, M. Bansal, Y. Chen (Eds.), Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing, EMNLP 2024, Miami, FL, USA, November 12-16, 2024, Association for Computational Linguistics, 2024, pp. 3473–3487. https://aclanthology.org/2024.emnlp-main.203. 

- [34] R. Liang, Y. Cao, P. Hu, K. Chen, et al., Neutron: an attention-based neural decompiler, Cybersecurity 4 (1) (2021) 5. https://cybersecurity.springeropen.com/ articles/10.1186/s42400-021-00070-0. 

- [35] Y. Cao, R. Liang, K. Chen, P. Hu, Boosting neural networks to decompile optimized binaries, in: Proceedings of the 38th Annual Computer Security Applications Conference, ACSAC ’22, Association for Computing Machinery, New York, NY, USA, 2022, p. 508–518. https://doi.org/10.1145/3564625.3567998 

- [36] X. Jin, J. Larson, W. Yang, Z. Lin, et al., Binary code summarization: benchmarking ChatGPT/GPT-4 and other large language models, 2023, http://arxiv.org/ abs/2312.09601. 

- [37] K. Papineni, S. Roukos, T. Ward, W.-J. Zhu, BLEU: a method for automatic evaluation of machine translation, in: Proceedings of the 40th Annual Meeting on Association for Computational Linguistics, ACL ’02, Association for Computational Linguistics, USA, 2002, p. 311–318. https://doi.org/10.3115/1073083. 1073135 

- [38] T. Chang, S. Chen, G. Fan, Z. Feng, A self-iteration code generation method based on large language models, in: 2023 IEEE 29th International Conference on Parallel and Distributed Systems (ICPADS), 2023, pp. 275–281. https://doi.org/10.1109/ICPADS60453.2023.00049 

- [39] Y. Dong, X. Jiang, Z. Jin, G. Li, Self-collaboration code generation via ChatGPT, ACM Trans. Softw. Eng. Methodol. 33 (7) (2024). https://doi.org/10.1145/ 3672459 

- [40] T. Huang, Z. Sun, Z. Jin, G. Li, C. Lyu, Knowledge-aware code generation with large language models, in: Proceedings of the 32nd IEEE/ACM International Conference on Program Comprehension, ICPC ’24, Association for Computing Machinery, New York, NY, USA, 2024, p. 52–63. https://doi.org/10.1145/3643916. 3644418 

- [41] X. Jiang, Y. Dong, L. Wang, Z. Fang, Q. Shang, G. Li, Z. Jin, W. Jiao, Self-planning code generation with large language models, ACM Trans. Softw. Eng. Methodol. 33 (7) (2024). https://doi.org/10.1145/3672456 

- [42] Z. Fan, X. Gao, M. Mirchev, A. Roychoudhury, S.H. Tan, et al., Automated repair of programs from large language models, in: 2023 IEEE/ACM 45th International Conference on Software Engineering (ICSE), IEEE, Melbourne, Australia, 2023, pp. 1469–1481. https://ieeexplore.ieee.org/document/10172854/. 

- [43] M. Jin, S. Shahriar, M. Tufano, X. Shi, S. Lu, N. Sundaresan, A. Svyatkovskiy, InferFix: end-to-end program repair with LLMs, in: Proceedings of the 31st ACM Joint European Software Engineering Conference and Symposium on the Foundations of Software Engineering, ESEC/FSE 2023, Association for Computing Machinery, New York, NY, USA, 2023, p. 1646–1656. https://doi.org/10.1145/3611643.3613892 

- [44] C.S. Xia, Y. Wei, L. Zhang, et al., Automated program repair in the era of large pre-trained language models, in: 2023 IEEE/ACM 45th International Conference on Software Engineering (ICSE), IEEE, Melbourne, Australia, 2023, pp. 1482–1494. https://ieeexplore.ieee.org/document/10172803/. 

- [45] C. Lemieux, J.P. Inala, S.K. Lahiri, S. Siddhartha, et al., CodaMosa: escaping coverage plateaus in test generation with pre-trained large language models, in: 2023 IEEE/ACM 45th International Conference on Software Engineering (ICSE), IEEE, Melbourne, Australia, 2023, pp. 919–931. https://ieeexplore.ieee.org/ document/10172800/. 

- [46] J. Wang, Y. Huang, C. Chen, Z. Liu, S. Wang, Q. Wang, Software testing with large language models: survey, landscape, and vision, IEEE Trans. Softw. Eng. 50 (4) (2024) 911–936. https://doi.org/10.1109/TSE.2024.3368208 

- [47] Z. Yuan, M. Liu, S. Ding, K. Wang, Y. Chen, X. Peng, Y. Lou, Evaluating and improving ChatGPT for unit test generation, Proc. ACM Softw. Eng. 1 (FSE) (2024). https://doi.org/10.1145/3660783 

- [48] OpenAI, J. Achiam, S. Adler, et al., GPT-4 technical report, 2024, 2303.08774 

- [49] M. Chen, J. Tworek, H. Jun, Q. Yuan, H.P. de Oliveira Pinto, J. Kaplan, et al., Evaluating large language models trained on code, 2021, https://arxiv.org/abs/ 2107.03374. 

- [50] Z. Rasheed, M. Waseem, M.A. Sami, K.-K. Kemell, A. Ahmad, A.N. Duc, K. Systä, P. Abrahamsson, Autonomous agents in software development: a vision paper, in: L. Marchesi, A. Goldman, M.I. Lunesu, A. Przybyłek, A. Aguiar, L. Morgan, X. Wang, A. Pinna (Eds.), Agile Processes in Software Engineering and Extreme Programming – Workshops, Springer Nature Switzerland, Cham, 2025, pp. 15–23. 

21 

_Science of Computer Programming 254 (2026) 103512_ 

_Y. Li, X. Zhang, T. Xu et al._ 

- [51] N. Alshahwan, M. Harman, I. Harper, A. Marginean, S. Sengupta, E. Wang, et al., Assured LLM-based software engineering, 2024, http://arxiv.org/abs/2402. 04380. 

- [52] A. Blasi, A. Gorla, M.D. Ernst, M. Pezzè, Call me maybe: using NLP to automatically generate unit test cases respecting temporal constraints, in: Proceedings of the 37th IEEE/ACM International Conference on Automated Software Engineering, ASE ’22, Association for Computing Machinery, New York, NY, USA, 2023. https://doi.org/10.1145/3551349.3556961 

- [53] S. Ugare, T. Suresh, H. Kang, S. Misailovic, G. Singh, SynCode: LLM generation with grammar augmentation, 2024, https://arxiv.org/abs/2403.01632. 

- [54] J. Li, G. Li, Y. Li, Z. Jin, Structured chain-of-thought prompting for code generation, ACM Trans. Softw. Eng. Methodol. 34 (2) (2025). https://doi.org/10.1145/ 3690635 

- [55] H. Ye, M. Martinez, X. Luo, T. Zhang, M. Monperrus, SelfAPR: self-supervised program repair with test execution diagnostics, in: Proceedings of the 37th IEEE/ACM International Conference on Automated Software Engineering, ASE ’22, Association for Computing Machinery, New York, NY, USA, 2023. https: //doi.org/10.1145/3551349.3556926 

- [56] J. Lee, K. Han, H. Yu, A light bug triage framework for applying large pre-trained language model, in: Proceedings of the 37th IEEE/ACM International Conference on Automated Software Engineering, ASE ’22, Association for Computing Machinery, New York, NY, USA, 2023. https://doi.org/10.1145/3551349.3556898 

- [57] N. Wadhwa, J. Pradhan, A. Sonwane, S.P. Sahu, N. Natarajan, A. Kanade, S. Parthasarathy, S. Rajamani, et al., Frustrated with code quality issues? LLMs can help!, 2023, http://arxiv.org/abs/2309.12938. 

- [58] C. Cadar, S. Koushik, Symbolic execution for software testing: three decades later, Commun. ACM 56 (2) (2013) 82–90. https://doi.org/10.1145/2408776. 2408795 

- [59] L. Gao, Y. Qu, S. Yu, Y. Duan, H. Yin, SigmaDiff: semantics-aware deep graph matching for pseudocode diffing, in: 31st Annual Network and Distributed System Security Symposium, NDSS 2024, San Diego, California, USA, February 26-March 1, 2024, The Internet Society, 2024. 

- [60] J. Glock, J. Pichler, M. Pinzger, PASDA: a partition-based semantic differencing approach with best effort classification of undecided cases, J. Syst. Softw. 213 (2024) 112037. https://www.sciencedirect.com/science/article/pii/S0164121224000803. 

- [61] J. Ming, D. Xu, Y. Jiang, D. Wu, BinSim: trace-based semantic binary diffing via system call sliced segment equivalence checking, in: Proceedings of the 26th USENIX Conference on Security Symposium, SEC’17, USENIX Association, USA, 2017, p. 253–270. 

- [62] M. Zou, A. Khan, R. Wu, H. Gao, A. Bianchi, D.J. Tian, D-Helix: a generic decompiler testing framework using symbolic differentiation, in: 33rd USENIX Security Symposium (USENIX Security 24), USENIX Association, Philadelphia, PA, 2024, pp. 397–414. https://www.usenix.org/conference/usenixsecurity24/ presentation/zou. 

- [63] J. Wei, X. Wang, D. Schuurmans, M. Bosma, B. Ichter, F. Xia, E.H. Chi, Q.V. Le, D. Zhou, Chain-of-thought prompting elicits reasoning in large language models, in: Proceedings of the 36th International Conference on Neural Information Processing Systems, NIPS ’22, Curran Associates Inc., Red Hook, NY, USA, 2022. 

- [64] M. Eckert, A. Bianchi, R. Wang, Y. Shoshitaishvili, C. Kruegel, G. Vigna, Heaphopper: bringing bounded model checking to heap implementation security, in: Proceedings of the 27th USENIX Conference on Security Symposium, SEC’18, USENIX Association, USA, 2018, p. 99–116. 

- [65] Resurrected LLVM “C Backend” with improvements, 2019, (https://github.com/JuliaHubOSS/llvm-cbe). Accessed April 10, 2025. 

- [66] Examples and guides for using the OpenAI API, 2022, (https://github.com/openai/openai-cookbook). Accessed April 10, 2025. 

- [67] DeepSeek-V3, a strong mixture-of-experts (MoE) language model with 671B total parameters with 37B activated for each token, 2024, (https://huggingface.co/ deepseek-ai/DeepSeek-V3). Accessed April 10, 2025. 

- [68] Qwen2.5 is the latest series of Qwen large language models, 2024, (https://huggingface.co/Qwen/Qwen2.5-7B-Instruct). Accessed April 10, 2025. 

- [69] Qwen-plus provides a balanced combination of performance, speed, and cost, ideal for moderately complex tasks, 2024, (https://www.alibabacloud.com/help/ en/model-studio/what-is-qwen-llm#6ad3cd90f0c5r). Accessed April 10, 2025. 

- [70] T. Yavuz, K.Y. Bai, Analyzing system software components using API model guided symbolic execution, J. Autom. Softw. Eng. 27 (2020) 329–367. https: //doi.org/10.1007/s10515-020-00276-5 

- [71] D.A. Ramos, D. Engler, Under-constrained symbolic execution: correctness checking for real code, in: Proceedings of the 24th USENIX Conference on Security Symposium, SEC’15, USENIX Association, USA, 2015, p. 49–64. 

22