Preprint, March 2026 

# Think Anywhere in Code Generation 

**Xue Jiang**<sup>1</sup><sup>_,_2</sup><sup>_,_�</sup> **, Tianyu Zhang**<sup>1</sup> **, Ge Li**<sup>1</sup><sup>_,_�</sup> **, Mengyang Liu**<sup>1</sup> **, Taozhi Chen**<sup>1</sup> **, Zhenhua Xu**<sup>1</sup> **, Binhua Li**<sup>2</sup> **, Wenpin Jiao**<sup>1</sup> **, Zhi Jin**<sup>1</sup> **, Yongbin Li**<sup>2</sup> **, Yihong Dong**<sup>1</sup><sup>_,_2</sup><sup>_,_�</sup> 

1 School of Computer Science, Peking University 

2 Tongyi Lab, Alibaba Group 

{jiangxue, dongyh}@stu.pku.edu.cn lige@pku.edu.cn 

## Abstract 

Recent advances in reasoning Large Language Models (LLMs) have primarily relied on upfront thinking, where reasoning occurs before final answer. However, this approach suffers from critical limitations in code generation, where upfront thinking is often insufficient as problems’ full complexity only reveals itself during code implementation. Moreover, it cannot adaptively allocate reasoning effort throughout the code generation process where difficulty varies significantly. In this paper, we propose THINK-ANYWHERE, a novel reasoning mechanism that enables LLMs to invoke thinking on-demand at any token position during code generation. We achieve THINK-ANYWHERE by first teaching LLMs to imitate the reasoning patterns through cold-start training, then leveraging outcome-based RL rewards to drive the model’s autonomous exploration of when and where to invoke reasoning. Extensive experiments on four mainstream code generation benchmarks (i.e., LeetCode, LiveCodeBench, HumanEval, and MBPP) show that THINK-ANYWHERE achieves state-of-the-art performance over both existing reasoning methods and recent post-training approaches, while demonstrating consistent generalization across diverse LLMs. Our analysis further reveals that THINK-ANYWHERE enables the model to adaptively invoke reasoning at high-entropy positions, providing enhanced interpretability. 

## 1 Introduction 

Recent advances in Large Language Models (LLMs) have demonstrated remarkable capabilities in code generation tasks (Rozière et al., 2023; Lozhkov et al., 2024; Guo et al., 2024; Dong et al., 2024a; 2025a). A pivotal breakthrough in this domain has been the integration of reasoning mechanisms, particularly exemplified by Chain-of-Thought (CoT) prompting (Wei et al., 2022; Jiang et al., 2024). Recent reasoning-optimized LLMs, such as industry-leading OpenAI’s o1 (Jaech et al., 2024), DeepSeek-R1 (Guo et al., 2025a), and Kimi K2 (Bai et al., 2025), have achieved unprecedented performance by scaling up reasoning through reinforcement learning (RL). These models are trained to first complete global planning and logical deliberation within an internal thinking block, and then proceed to generate the final output. This upfront thinking approach has become the dominant technical pathway for enhancing complex reasoning capabilities in code generation (Jaech et al., 2024; Jiang et al., 2026; Guo et al., 2025a). 

While the upfront thinking approach has proven effective, it exhibits two limitations in code generation. First, upfront thinking is often insufficient, as the full complexity of problems typically only reveals itself during implementation. For instance, LLMs usually perform only plan-level thinking in the upfront reasoning phase, while new problems emerge during the code implementation stage, leading to bugs due to the lack of adequate reasoning, as shown in Figure 1. Second, upfront thinking cannot precisely allocate reasoning effort to the positions where it is needed. Different positions in code generation vary in difficulty, with simple boilerplate code requiring minimal computation while complex algorithmic decisions or edge case handling demanding deep reasoning. By contrast, human 

> *Work done during Xue Jiang and Yihong Dong’s internship at Tongyi Lab. 

> † Our source code and data are available at https://github.com/jiangxxxue/Think-Anywhere. 

1 

Preprint, March 2026 



<!-- Start of picture text -->
<think> I need to find the minimum edit distance between two strings.Steps: Standard Thinking of LLMs Givenword1 totwoword2.stringsYouword1can performand word2,threereturn Problem: Edit Distance operations:the minimuminsert,numberdelete,of operationsor replacerequireda character.to convert<br>1. Use dynamic programming with a 2D array dp[i][j]<br>2...3...4...5. Return dp[m][n] <think> ... </think> Think-Anywhere<br>Time complexity: O(m*n), Space complexity: O(m*n)<br></think> def minDistancemdpforfor, n=idpjdp=[[in[in[len0i0]][][rangerange(*0j(word1]]word1(n==((+minj),,1++)word2len11for):):(word2):_ in)range(m + 1)] def minDistancemdpforforfor, n=idpjdpifor=[[in[in[inlen0i0]][][jrangerangerange(*0jin(word1]]word1(n==range(((+minj1),,,1++)m(word2len111for):):+, (1nword2):):_+ in1):)range(m + 1)]<br>for iforinj if elserangein word1 dp:dprange([[1ii, [ ][][ i m( ] jj1]]+, == ==1n): word2 dpmin+[1i():dp [ - j [ ]: 1i][-j1-][1j]], dp BUG: index out of bounds [i][j - 1], dp[i - 1][j - 1]) + 1 </thinkanywhere> [j - 1], dp[iifelse- dpdp1word1][:i[[iij -][][-[1jj<]]]1 thinkanywhere> dp is 1-based but string is 0-based, use i-1  ])=== = dpmin+word2[1<(< thinkanywhere> ... </thinkanywhere>thinkanywhere> ... </thinkanywhere> [ < thinkanywhere> ... </thinkanywhere> idp-[1ij ][--j 11-][]:1j]], dp[i]<br>return dp[m][n] return dp[m][n]<br><!-- End of picture text -->

Figure 1: Illustration of THINK-ANYWHERE. Reasoning can be invoked at any token position during code generation. The ellipsis (“...”) within <think> or <thinkanywhere> represents truncated thinking content for brevity. 

coding cognition shows that developers not only think before coding but also pause to think at any point during implementation, which proves a more reasonable thinking approach. Motivated by these observations, we desire a mechanism that enables models to invoke reasoning at any token position during code generation based on immediate context and local complexity, which we term THINK-ANYWHERE. The THINK-ANYWHERE mechanism is demonstrated in Figure 1. 

Realizing the THINK-ANYWHERE mechanism presents significant challenges. Since LLMs do not spontaneously invoke reasoning during code generation, they must be explicitly taught this capability. We achieve this through cold-start training by constructing supervised learning samples that demonstrate reasoning invocation patterns of THINK-ANYWHERE. While cold-start training can teach models to invoke reasoning blocks within code, it cannot effectively teach models where reasoning is necessary. The decision of which token positions to invoke thinking requires the model to identify its own moments of high complexity or logical risk, which demands adaptive judgment that goes beyond pattern matching in supervised data. To address this challenge, we employ Reinforcement Learning with Verifiable Rewards (RLVR) to enable LLMs to autonomously learn where to trigger reasoning during code generation, allowing the model to discover optimal thinking positions through reward-driven exploration. 

In this work, we propose THINK-ANYWHERE, a novel reasoning mechanism of LLMs for code generation that enables models to invoke thinking at any token position based on LLM’s demands. THINK-ANYWHERE is realized through a two-stage training pipeline. First, through cold-start training with carefully constructed code generation samples that demonstrate THINK-ANYWHERE, we teach models the fundamental capability of pausing to think at arbitrary token positions during code generation. Second, we employ RLVR to further reinforce this capability, allowing models to autonomously explore and discover the optimal positions and strategies for invoking reasoning that suit the specific challenges they encounter. THINK-ANYWHERE enables models to think on-demand at critical moments during code generation, precisely allocating computational resources to tokens that necessitate deep thinking. Moreover, by observing where and how models think during code generation, THINK-ANYWHERE provides greater transparency into the decision-making process, enhancing the interpretability. 

Extensive experiments demonstrate that THINK-ANYWHERE achieves state-of-the-art performance over existing LLM reasoning-enhanced methods and recently proposed post-training methods on four mainstream code generation benchmarks, including LeetCode, LiveCodeBench, HumanEval, and MBPP. THINK-ANYWHERE also exhibits strong generalization across different LLM families and model sizes. Ablation studies reveal that combining cold-start initialization with RLVR yields optimal results, and token-level thinking outperforms alternative variants such as line-level thinking. Further analysis highlights that LLMs tend to invoke thinking at positions with higher entropy, demonstrating that THINK-ANYWHERE can reason at appropriate positions on demand. 

## 2 Related Work 

**Reasoning and Planning Mechanisms in LLMs.** Enhancing the reasoning and planning capabilities of LLMs has emerged as a central research focus in recent years. A seminal advancement 

2 

Preprint, March 2026 

in this direction is Chain-of-Thought (CoT) prompting (Wei et al., 2022), which elicits complex reasoning by guiding LLMs to generate intermediate reasoning steps before arriving at a final answer. Subsequent studies build on CoT with richer prompting strategies and search mechanisms (Kojima et al., 2022; Wang et al., 2023; Zhou et al., 2023; Yao et al., 2023). In the domain of code generation, Self-Planning (Jiang et al., 2024) conducts problem decomposition and planning prior to code generation to reduce task complexity. While these methods treat reasoning as an upfront thinking phase, recent work explores interleaved strategies that tightly couple thinking with task execution. For instance, Interleaved Thinking (Xie et al., 2025; Liang et al., 2025) guides LLMs to alternate between thinking and answering, enabling incremental refinement based on intermediate results. TwiG (Guo et al., 2025b) interleaves textual reasoning throughout visual generation trajectories, allowing reasoning to guide upcoming synthesis and reflect on previously generated content. 

Recent advances in reasoning LLMs, such as DeepSeek-R1 (Guo et al., 2025a) and Kimi-K2 (Bai et al., 2025), have achieved remarkable success by employing upfront thinking. While recent work on Interleaved Thinking allows reasoning to occur during implementation, it requires thinking at each sub-step and lacks the flexibility for on-demand invocation. This limitation introduces unnecessary computational overhead, while failing to allocate deeper reasoning effort to the most challenging portions of a task. 

**Post-Training of LLMs for Code Generation.** Post-training has become important for improving the code generation capabilities of LLMs beyond pretraining, as it can better exploit task-specific data and verifiable execution signals. One major approach is distillation from stronger reasoning LLMs. For example, OlympicCoder (Hugging Face, 2025) fine-tunes models on competitive programming tasks using reasoning trajectories distilled from DeepSeek-R1. Similarly, OCR-Qwen-7B (Ahmad et al., 2025) is distilled from DeepSeek-R1, leveraging a large-scale dataset of over 730K reasoningannotated samples for open-source reproduction. Another major approach is RL from executable feedback, which has been widely adopted to strengthen code generation and reasoning capabilities. Skywork-OR1 (He et al., 2025) employs large-scale RLVR training following DeepSeek-R1’s pipeline for code generation. CodePRM (Li et al., 2025b) introduces a process reward model that provides step-level rewards for intermediate steps during generation. CodeBoost (Wang et al., 2025) enhances code generation through RL training on code reasoning tasks. CodeRL+ (Jiang et al., 2025) further enriches the learning signal by aligning code generation with execution semantics beyond binary pass/fail feedback. 

Existing post-training methods, regardless of whether they are based on distillation or RL, predominantly adopt the upfront thinking practice. This introduces the limitations discussed in Section 1, necessitating a shift in the thinking approach for code generation. 

## 3 Methodology 

3.1 Defining THINK-ANYWHERE 

We begin by formally defining the THINK-ANYWHERE mechanism and contrasting it with the conventional upfront thinking method. Let _x_ denote the requirement and _c_ denote the generated code. We define two special token pairs: _⟨_ think _⟩_ and _⟨_ /think _⟩_ for the upfront thinking block, and _⟨_ thinkanywhere _⟩_ and _⟨_ /thinkanywhere _⟩_ for the THINK-ANYWHERE thinking block. 

**Upfront Thinking.** In the upfront thinking method adopted by existing reasoning-enhanced LLMs (Jaech et al., 2024; Guo et al., 2025a), the generation process can be decomposed into two sequential phases. Given input _x_ , the model first generates a complete reasoning trace _s_ enclosed within _⟨_ think _⟩_ and _⟨_ /think _⟩_ tokens, and then generates the code _c_ conditioned on both _x_ and _s_ : 



This formulation enforces a strict separation between reasoning and code generation, making LLM difficult to invoke additional reasoning in code generation process. 

**THINK-ANYWHERE.** THINK-ANYWHERE enables LLM to precisely reason at any position where deliberation is needed during code generation. Considering the non-uniform distribution of logical 

3 

Preprint, March 2026 

You are a coding assistant that generates both code and inline self-guidance signals. First output <think>... </think> with brief reasoning, then output the final code. 

MUST FOLLOW Rules for <thinkanywhere>...</thinkanywhere> tags: 

1. You MUST use <thinkanywhere>...</thinkanywhere> tags for self-guidance or intermediate reasoning. 

2. <thinkanywhere>...</thinkanywhere> MUST be embedded within an existing program statement token sequence. 

3. The code must remain valid and executable after removing all <thinkanywhere>...</thinkanywhere> segments. 

User: Prompt. Assistant: 

Table 1: Template for THINK-ANYWHERE. Prompt will be replaced with the specific coding requirement. 

complexity in code generation, THINK-ANYWHERE allows the model to dynamically scale its reasoning length at challenging bottlenecks, achieving a truly on-demand allocation of computational resources. Formally, the model generates a mixed sequence **y** . This sequence naturally decomposes into code segments and thinking blocks: 



where _s_ denotes the initial thinking block enclosed within _⟨_ think _⟩_ and _⟨_ /think _⟩_ , each _c_<sup>(</sup><sup>_i_)</sup> represents a code segment, and each _h_<sup>(</sup><sup>_i_)</sup> represents a thinking block enclosed within _⟨_ thinkanywhere _⟩_ and _⟨_ /thinkanywhere _⟩_ tokens that is placed between code segments. The number of thinking blocks _M ≥_ 0 and their positions are dynamically determined by the model during generation. 

The generation process of THINK-ANYWHERE can be formulated as: 



where **y** _<c_ ( _i_ ) and **y** _<h_ ( _i_ ) denote all preceding tokens before code segment _c_<sup>(</sup><sup>_i_)</sup> and thinking block _h_<sup>(</sup><sup>_i_)</sup> , respectively. Notably, upfront thinking can be viewed as a special case of THINK-ANYWHERE where thinking occurs exclusively at the beginning. 

The final executable code _c_ is obtained by removing all thinking blocks from **y** , including the initial _⟨_ think _⟩_ block and all _⟨_ thinkanywhere _⟩_ blocks: 



where _⊕_ denotes sequence concatenation. 

**Training Template.** To train THINK-ANYWHERE, we design a template that guides LLMs to follow the THINK-ANYWHERE generation format, as shown in Table 1. The template instructs the model to first produce initial reasoning within _⟨_ think _⟩_ tags, then generate code with _⟨_ thinkanywhere _⟩_ blocks invoked at positions requiring deliberation. We constrain only the structural format while avoiding content-specific biases, allowing the model to discover optimal thinking patterns through subsequent reinforcement learning. 

### 3.2 Cold Start for THINK-ANYWHERE 

LLMs do not invoke thinking blocks during code generation, and even explicit instructions in prompts often fail to enforce this behavior reliably. Therefore, they must be explicitly taught this capability through training. The goal of cold start is to equip the model with the fundamental ability to reason at arbitrary positions within code. 

4 

Preprint, March 2026 

**Automatic Data Construction.** We leverage strong reasoning LLMs with our training template to automatically construct training data that demonstrates the THINK-ANYWHERE pattern. Specifically, we prompt the reasoning LLMs to solve coding problems while explicitly invoking thinking blocks enclosed within _⟨_ thinkanywhere _⟩_ and _⟨_ /thinkanywhere _⟩_ tokens at positions where deliberation is needed during code generation. 

To ensure data quality, we filter out samples with incorrect formatting, such as malformed thinking block boundaries or improper nesting of special tokens. Following prior work (Li et al., 2025a) that demonstrates both correct and incorrect solutions contribute to model learning, we retain samples regardless of code correctness. This process of data construction yields approximately 5,000 training samples. 

We perform supervised fine-tuning using LoRA (Hu et al., 2022) on the constructed training samples as cold start. Following (Schulman & Lab, 2025), we adopt LoRA over full-parameter SFT as it achieves comparable performance with greater robustness and lower computational overhead. This training enables the model to learn the pattern of invoking _⟨_ thinkanywhere _⟩_ blocks within code, acquiring the basic capability that serves as the foundation for subsequent reinforcement learning. 

**Dedicated Reasoning Trigger Token.** In default implementation, _⟨_ thinkanywhere _⟩_ is tokenized into multiple ordinary tokens, each carrying its own lexical meaning. Requiring the model to use these tokens simultaneously as lexical units and as a trigger signal for invoking reasoning introduces semantic ambiguity. Moreover, generating a multi-token delimiter increases the prediction path length for a single control decision, making the trigger less reliable. We therefore introduce a special token variant (THINK-ANYWHERE*) that represents the thinking delimiter as a single dedicated vocabulary entry, providing an unambiguous and efficient signal for invoking inline reasoning. 

However, directly adding randomly initialized special tokens is ineffective, as the limited posttraining data is insufficient for the model to learn meaningful representations from scratch. To address this, we propose a semantic-aware initialization strategy that composes the embedding from two complementary sources: the semantic content of the trigger and the structural role of a delimiter. Specifically, we initialize the embeddings of the new special tokens as: 



where **e** _⟨_ ta _⟩_ and **e** _⟨_ /ta _⟩_ denote the embeddings of the opening and closing special tokens, respectively. The first term encodes the semantic intent of “think anywhere,” while the second term inherits the structural behavior of existing delimiter tokens ( _⟨_ im_start _⟩_ and _⟨_ im_end _⟩_ ), which the model has already learned to treat as mode-switching boundaries during pretraining. 

To effectively train the dedicated trigger tokens, we adopt a two-stage cold-start procedure: 

1. **Stage 1: Embedding alignment.** We freeze the model parameters and train only the input embeddings and LM head weights. This stage allows the tokens to develop appropriate representations without disrupting the model’s existing capabilities. 

2. **Stage 2: Joint fine-tuning.** We continue training the special token embeddings and LM head jointly with LoRA adapters applied to the model, enabling the model to learn how to generate and respond to the dedicated trigger tokens in context. 

The subsequent RLVR stage proceeds identically to the default version. 

### 3.3 RLVR for THINK-ANYWHERE 

We then employ RLVR to enable the LLMs to autonomously discover optimal thinking positions and strategies through reward-driven exploration. 

**Reinforcement Learning Algorithm.** We adopt Group Relative Policy Optimization (GRPO) (Shao et al., 2024) as our reinforcement learning algorithm. Unlike Proximal Policy Optimization (PPO) (Schulman et al., 2017) which requires a separate value model to estimate baselines, GRPO computes baselines from group-level statistics, eliminating the need for an additional value model and significantly reducing computational overhead. 

5 

Preprint, March 2026 

Specifically, for each input _x_ , GRPO samples a group of _G_ candidate outputs _{y_ 1 _, y_ 2 _, . . . , yG}_ from the current policy _πθ_ . The reward for each output _yi_ is computed as _R_ ( _yi_ ), and the group-normalized advantage is calculated as: 



The policy is then optimized by maximizing the clipped surrogate objective with a KL divergence penalty: 



where _ρi_ = _ππ_ old _<u>θ</u>_ <u>((</u> _<u>yyii||xx</u>_ <u>))</u><sup>denotes the probability ratio,</sup><sup>_ϵ_is the clipping threshold,and</sup><sup>_β_controls the</sup> strength of the KL penalty against the reference policy _π_ ref. 

**Reward Modeling.** We design a hierarchical reward function for THINK-ANYWHERE. The reward consists of two components: a reasoning structure reward _R_ struct and a code correctness reward _R_ correct, combined in a gated manner: 



where _α_ = 0 _._ 1 controls the weight between the two components. 

The reasoning structure reward _R_ struct _∈{_ 0 _,_ 1 _}_ verifies that the model adheres to the THINKANYWHERE reasoning definition. Specifically, it checks whether the output contains an initial thinking block within _⟨_ think _⟩_ and _⟨_ /think _⟩_ tags, followed by code that incorporates _⟨_ thinkanywhere _⟩_ blocks: 



where HasInitialThinking( _·_ ) verifies the presence of the initial _⟨_ think _⟩_ block, and HasThinkAnywhere( _·_ ) ensures that at least one _⟨_ thinkanywhere _⟩_ block is embedded within the generated code. This reward encourages the model to actively engage in on-demand reasoning throughout the generation process. 

The code correctness reward _R_ correct _∈{_ 0 _,_ 1 _}_ evaluates the functional correctness of the generated code by executing it against the provided test cases: 



## 4 Experiments 

4.1 Experiment Setup 

**Training Details.** Follow previous work (He et al., 2025), our training corpus comprises 14K programming problem from the Skywork dataset. By default, we employ Qwen2.5-Coder-7BInstruct (Hui et al., 2024) as the base model for our experiments. The RL algorithm is implemented using the VeRL framework (Sheng et al., 2024). Training parameters are set as follows: batch size of 128, mini-batch size of 64, learning rate of 1 _×_ 10<sup>_−_6</sup> , and 2 training epochs. Each problem generates 8 rollout samples up to 4096 tokens. The experiments run on 8 NVIDIA A100 GPUs (40G). We employ Google’s Gemini 2.5 Flash (Comanici et al., 2025) to synthesize cold-start training data. 

**Evaluation Details.** Following established practices in prior work (Li et al., 2025b; Tang et al., 2025; Wang et al., 2025; Dong et al., 2025b; 2024b), our evaluation encompasses four widelyused code generation benchmarks: HumanEval (Chen et al., 2021), MBPP (Austin et al., 2021), LeetCode (Xia et al., 2025), and LiveCodeBench (Jain et al., 2024). We adopt pass@1 as our primary evaluation metric. To ensure reproducibility and consistency across all experiments, we employ greedy sampling with the temperature fixed at 0. 

6 

Preprint, March 2026 

Table 2: Performance of THINK-ANYWHERE compared to post-training methods and reasoningenhanced methods. Best results are in **bold** . THINK-ANYWHERE* denotes the special token variant with semantic-aware initialization (see Section 3.2). 

|**Method**|**LeetCode**|**LiveCodeBench**|**HumanEval**|**MBPP**|**Average**|
|---|---|---|---|---|---|
|Base Model|50.6|34.3|88.4|70.7|61.0|
|**Post-Training Methods**||||||
|OlympicCoder|45.3|30.9|75.6|67.2|54.8|
|OCR-Qwen-7B|53.3|33.0|86.8|58.9|58.0|
|CodePRM|52.8|34.8|88.4|73.9|62.5|
|CodeBoost|53.3|34.6|87.2|65.7|60.2|
|CodeRL+|63.3|36.9|90.9|76.2|66.8|
|**Reasoning-Enhanced Methods**||||||
|CoT|53.9|30.9|86.6|77.7|62.3|
|Self-planning|49.2|31.1|86.9|77.9|61.3|
|Interleaved Thinking|50.6|30.7|86.4|79.2|61.7|
|GRPO|67.3|36.0|88.6|81.7|68.4|
|THINK-ANYWHERE(Prompting)|41.1|34.4|84.8|67.4|56.9|
|THINK-ANYWHERE* (SFT)|46.7|32.5|79.9|78.2|59.3|
|THINK-ANYWHERE* (Ours)|68.9|36.7|90.2|84.5|70.0|
|THINK-ANYWHERE(SFT)|47.9|32.3|82.9|79.4|60.6|
|THINK-ANYWHERE**(Ours)**|**69.4**|**37.2**|**91.5**|**82.9**|**70.3**|



**Baselines.** Beyond the base model and standard GRPO method (Shao et al., 2024), we compare THINK-ANYWHERE with two categories of methods, all using the same base model. The first category includes the reasoning-enhanced approaches that incorporate thinking mechanisms, including **CoT** (Wei et al., 2022), **Self-Planning** (Jiang et al., 2024), and **Interleaved Thinking** (Xie et al., 2025)<sup>1</sup> . The second category includes the recently proposed post-training models and methods developed for code generation, including **OlympicCoder** (Hugging Face, 2025), **OCR-Qwen-7B** (Ahmad et al., 2025), **CodePRM** (Li et al., 2025b), **CodeBoost** (Wang et al., 2025), and **CodeRL+** (Jiang et al., 2025). 

### 4.2 Experiment Results 

**Performance of THINK-ANYWHERE.** Table 2 presents the main results of THINK-ANYWHERE compared to baselines on four benchmarks. Overall, THINK-ANYWHERE achieves the best performance across all benchmarks, with an average score of 70.3%, representing a 9.3% absolute improvement over the base model. Compared to Post-Training Methods, THINK-ANYWHERE surpasses the best-performing baseline CodeRL+, demonstrating the effectiveness of our approach over other RL-based approaches. Compared to Reasoning-Enhanced Methods, THINK-ANYWHERE substantially outperforms CoT, Self-planning, Interleaved Thinking, and GRPO across all metrics. Notably, some methods exhibit inconsistent improvements across different benchmarks. In contrast, THINK-ANYWHERE achieves consistent improvements on both simple and challenging tasks, suggesting that our dynamic thinking strategy is more effective than fixed reasoning patterns. Furthermore, the comparison among THINK-ANYWHERE variants reveals the importance of RL-based training. THINK-ANYWHERE (Prompting) and THINK-ANYWHERE (SFT) underperform the base model on several benchmarks, whereas THINK-ANYWHERE with RL training achieves substantial gains, highlighting that reinforcement learning is crucial for learning effective thinking patterns. 

We also report the results of the special token variant (THINK-ANYWHERE*). With semantic-aware initialization and the two-stage cold-start procedure, THINK-ANYWHERE* achieves an average score of 70.0%, which is comparable to the default text-based version (70.3%). We observe that the textbased version tends to invoke thinking blocks at stereotyped positions ( _e.g_ ., after “=” tokens), while the special token variant exhibits more diverse and contextually appropriate placement. However, 

> 1As Interleaved Thinking does not provide source code, we adapt it to the code generation setting by prompting the model to alternate between reasoning and code implementation, following the method described in the original work. 

7 

Preprint, March 2026 

Table 3: Cross-domain generalization of THINK-ANYWHERE to mathematical reasoning benchmarks. The model is trained solely on code generation tasks. 

|**Method**||**AIME 202**|**4**||**AIME 202**|**5**||**HMMT 20**|**25**|
|---|---|---|---|---|---|---|---|---|---|
||pass@1|pass@5|pass@10|pass@1|pass@5|pass@10|pass@1|pass@5|pass@10|
|Base Model|5.3|14.6|20.0|4.0|13.4|16.7|0.0|0.0|0.0|
|GRPO|6.0|16.8|23.3|4.7|17.2|26.7|0.3|1.7|3.3|
|THINK-ANYWHERE|**17.3**|**32.9**|**40.2**|**17.7**|**28.0**|**33.2**|**14.4**|**18.5**|**19.6**|



the limited post-training data constrains the special token variant from fully learning the semantics of the new tokens. We believe that natively integrating THINK-ANYWHERE special tokens during large-scale pretraining would further unlock their potential. Since the text-based version slightly outperforms the special token variant under our post-training setting, we adopt the text-based version for all subsequent experiments. 

**Cross-Domain Generalization.** To investigate whether THINK-ANYWHERE generalizes beyond code generation, we directly evaluate our code-domain-trained model on mathematical reasoning benchmarks, including AIME 2024 (Mathematical Association of America, 2024), AIME 2025 (Mathematical Association of America, 2025), and HMMT 2025 (Balunovi´c et al., 2025). Table 3 reports the results under pass@1, pass@5, and pass@10 settings. Notably, although THINK-ANYWHERE is trained exclusively on code generation tasks, it achieves consistent and substantial improvements over both the base model and GRPO across three mathematical reasoning benchmarks. For instance, on AIME 2024, THINK-ANYWHERE improves pass@1 from 5.3% (Base Model) and 6.0% (GRPO) to 17.3%, representing a remarkable gain. Similar trends are observed on AIME 2025 and HMMT 2025, where THINK-ANYWHERE achieves 17.7% and 14.4% pass@1 respectively. These results suggest that the think-on-demand reasoning capability acquired through THINK-ANYWHERE is not domain-specific but transfers across tasks, demonstrating strong cross-domain generalization. 

**Application on Various LLMs.** To validate the generalizability of THINK-ANYWHERE, we evaluated its performance on three diverse LLMs spanning different model families and parameter scales: LLaMA-3.1-8B-Instruct (Meta AI, 2024), Qwen2.5-Coder-7B-Instruct (Hui et al., 2024), and Qwen2.5-Coder-1.5B-Instruct (Hui et al., 2024). Table 4 reports the average performance across four benchmarks. The results demonstrate that THINK-ANYWHERE consistently outperforms both the base model and GRPO across all LLMs, with substantial margins over GRPO. Notably, THINK-ANYWHERE achieves up to +13.9% improvement over the base model. Furthermore, THINK-ANYWHERE exhibits strong scalability across different model sizes. On the smaller Qwen2.5-Coder-1.5B-Instruct, THINK- 

Table 4: Generalizability of THINK-ANYWHERE across different model families and scales. 

|**Model**|**Average**|∆**vs. Base**|
|---|---|---|
|**Qwen2.5-Coder-7B-Instr**|**uct**||
|Base Model|61.0|–|
|+ GRPO|68.4|+7.4|
|+ THINK-ANYWHERE|**70.3**|**+9.3**|
|**Qwen2.5-Coder-1.5B-Ins**|**truct**||
|Base Model|40.6|–|
|+ GRPO|51.9|+11.3|
|+ THINK-ANYWHERE|**54.5**|**+13.9**|
|**LLaMA-3.1-8B-Instruct**|||
|Base Model|38.4|–|
|+ GRPO|42.0|+3.6|
|+ THINK-ANYWHERE|**43.8**|**+5.4**|



ANYWHERE achieves a substantial improvement over the base model, indicating that our method is particularly effective for smaller models with limited capacity. 

### 4.3 Ablation Study 

To understand the contribution of each component in THINK-ANYWHERE, we conduct comprehensive ablation studies comparing multiple variants on the LeetCode benchmark. We first ablate different training strategies: 1) THINK-ANYWHERE: Our complete method incorporates both cold-start training and RLVR in a two-stage pipeline. 2) **Only Cold Start** : Model trained solely with supervised learning on annotated samples of THINK-ANYWHERE, without RL phase. 3) **Only RLVR** : Model trained directly with RLVR of THINK-ANYWHERE from scratch, bypassing the cold-start phase. 4) **Line-level Thinking** : A variant where RLVR encourages line-level thinking (similar to comment-style reasoning) rather than arbitrary token positions. 5) **No Upfront Thinking** : A variant of our approach 

8 

Preprint, March 2026 



<!-- Start of picture text -->
400 80<br>300 60<br>200 40<br>100 20<br>0 0<br>-0.15 -0.10 -0.05 0.00 0.05 0.10 0.15 Assign Return Expr If AugAssign For<br>Value of Entropy  Syntax Type<br>(a) Token entropy analysis. (b) Syntactic context analysis.<br>Frequency<br>Proportion (%)<br><!-- End of picture text -->

Figure 2: Results of Thinking Position Analysis. 

that removes the initial thinking block and relies solely on THINK-ANYWHERE within the code. To isolate the impact of the THINK-ANYWHERE mechanism itself, we evaluate an inference variant: 6) **Padding Thinking** : During THINK-ANYWHERE generation, the content within <thinkanywhere> blocks is replaced with padding tokens before continuing generation. 

The results are presented in Table 5. We have the following observations. First, both cold-start and RLVR are essential. Removing either training stage leads to substantial performance degradation. Only Cold Start performs poorly, indicating that supervised learning alone is insufficient for the model to learn effective thinking. Only RLVR performs better but still lags behind the full method, suggesting that cold-start initialization helps stabilize RL training. Second, Line-level Thinking underperforms our token-level approach, suggesting that restricting thinking to line boundaries limits the model’s 

Table 5: The results of ablation study. 

|**Method**|**Pass@1**|∆|
|---|---|---|
|THINK-ANYWHERE|**69.4**|**–**|
|Only Cold Start|47.9|-21.5|
|<br>OnlyRLVR|63.4|-6.0|
|Line-level Thinking|67.2|-2.2|
|No Upfront Thinking|66.6|-2.8|
|Padding Thinking|67.6|-1.8|



ability to invoke reasoning at optimal positions, validating our design choice of allowing thinking at arbitrary token positions. Third, No Upfront Thinking incurs only a moderate drop (-2.8%), indicating that the primary performance gains of THINK-ANYWHERE stem from the THINK-ANYWHERE mechanism within the code rather than the upfront thinking phase. Finally, Padding Thinking also shows moderate performance degradation, demonstrating that the reasoning content within <thinkanywhere> blocks is indeed valuable. However, the performance does not fully deteriorate to the base model level, suggesting that identifying appropriate thinking positions is also important. Through the subsequent padding tokens, the model still performs some implicit reasoning during the forward pass (Goyal et al., 2024; Pfau et al., 2024). 

### 4.4 Further Analysis 

**Thinking Position Analysis.** Understanding where THINK-ANYWHERE chooses to invoke reasoning during code generation provides crucial insights into the model’s perception of code complexity and validates whether it truly allocates computational resources efficiently. We analyze generated solutions on the LeetCode benchmark through two perspectives: 1) Token entropy analysis: We compute the average token entropy over the n tokens following each <thinkanywhere> block and compare it against a baseline where no thinking blocks are generated, thereby quantifying the impact of <thinkanywhere> on entropy. We empirically set n=10 for entropy analysis, as this window size typically captures a statement unit, thereby mitigating individual token noise. 2) Syntactic context analysis: We employ an AST parser to identify the syntactic category of the statement enclosing each thinking position (e.g., If, While, FunctionDef, BinOp), characterizing where the model chooses to think within the code structure. 

Figure 2a shows the distribution of entropy differences between thinking-disabled/enabled runs at positions where the model originally invoked <thinkanywhere>. We observe that the differences are predominantly positive, indicating higher entropy when thinking is disabled. This suggests that the model tends to invoke <thinkanywhere> at positions where it anticipates high uncertainty, effectively identifying challenging points in code generation. Figure 2b presents the top five syntactic categories where <thinkanywhere> is invoked. The model most frequently invokes thinking at assignment statements, likely because assignments often involve complex computations or variable updates that benefit from intermediate reasoning. Return statements rank second, which we attribute to the model’s tendency to deliberate on final outputs to ensure correctness before concluding a function. 

9 

Preprint, March 2026 

**Computational Efficiency Comparison.** We 600 GRPO evaluate the inference efficiency of THINKCoT ANYWHERE by measuring the average num500 Think-Anywhere ber of tokens generated per solution. We com400 pare THINK-ANYWHERE against two reasoning baselines: GRPO (upfront thinking) and 300 CoT prompting. As shown in Figure 3, THINK200 ANYWHERE consistently generates fewer tokens than both baselines across benchmarks. 100 The reduction in total token cost is attributed 0 to the fact that THINK-ANYWHERE shortens HumanEval MBPP LeetCode the upfront thinking phase while introducing additional <thinkanywhere> tokens on demand. Figure 3: Token cost of different methods. Since GRPO and CoT can only reason before code generation, they are forced to deliberate exhaustively at the upfront thinking stage, anticipating all potential implementation challenges upfront, which results in lengthy reasoning traces. THINK-ANYWHERE, by contrast, invokes deliberation where it is needed. The upfront thinking phase therefore only needs to handle high-level planning, and its length is substantially reduced. The token savings from the shortened upfront thinking far outweigh the cost of the additional <thinkanywhere> blocks, resulting in a net reduction in total token usage. A detailed breakdown of the upfront thinking length and <thinkanywhere> block length is provided in Appendix A. 



<!-- Start of picture text -->
LeetCode LiveCodeBench HumanEval MBPP<br>85.0 96 92<br>82.5 41 95<br>90<br>80.0 40 94<br>77.5 93 88<br>39<br>75.0 92 86<br>72.5 38 91<br>70.0 GRPO 37 90 84<br>67.5 Think-Anywhere 36 89 82<br>1 2 4 8 16 1 5 10 1 2 4 8 16 1 2 4 8 16<br>k k k k<br>Pass@k (%) Pass@k (%) Pass@k (%) Pass@k (%)<br><!-- End of picture text -->

Figure 4: Pass@k comparison between GRPO and THINK-ANYWHERE across four benchmarks. 

**Pass@k Analysis.** Pass@k reflects the upper bound of a model’s capability by evaluating whether at least one correct solution exists among _k_ sampled candidates. We report pass@k results for both GRPO and THINK-ANYWHERE across all benchmarks to investigate whether THINK-ANYWHERE expands the model’s capability boundary. As shown in Figure 4, THINK-ANYWHERE consistently outperforms GRPO across all values of _k_ on benchmarks. More importantly, the performance gap between THINK-ANYWHERE and GRPO widens significantly as _k_ increases, particularly on LeetCode and MBPP. This widening gap demonstrates that THINK-ANYWHERE substantially raises the model’s capability ceiling. 

## 5 Conclusion 

In this work, we introduce THINK-ANYWHERE, a novel reasoning mechanism that enables LLMs to invoke thinking at any token position during code generation. Unlike conventional upfront thinking approaches that enforce a strict separation between reasoning and code implementation, THINKANYWHERE allows models to deliberate precisely where complexity arises. Extensive experiments across multiple mainstream benchmarks demonstrate that THINK-ANYWHERE achieves SOTA performance, with strong generalization across different LLMs. Beyond performance gains, our analysis reveals that LLMs naturally learn to invoke thinking at high-entropy positions, suggesting that THINK-ANYWHERE enables adaptive computation where reasoning effort is dynamically allocated based on local complexity. We believe THINK-ANYWHERE opens promising directions for future research, including extending THINK-ANYWHERE to other domains beyond code generation, and investigating how models can learn what _not_ to think, further optimizing the trade-off between reasoning depth and computational efficiency. 

10 

Preprint, March 2026 

## References 

- Wasi Uddin Ahmad, Sean Narenthiran, Somshubra Majumdar, Aleksander Ficek, Siddhartha Jain, Jocelyn Huang, Vahid Noroozi, and Boris Ginsburg. Opencodereasoning: Advancing data distillation for competitive coding. _arXiv preprint arXiv:2504.01943_ , 2025. 

- Jacob Austin, Augustus Odena, Maxwell I. Nye, Maarten Bosma, Henryk Michalewski, David Dohan, Ellen Jiang, Carrie J. Cai, Michael Terry, Quoc V. Le, and Charles Sutton. Program synthesis with large language models. _CoRR_ , abs/2108.07732, 2021. 

- Yifan Bai, Yiping Bao, Guanduo Chen, Jiahao Chen, Ningxin Chen, Ruijue Chen, Yanru Chen, Yuankun Chen, Yutian Chen, Zhuofu Chen, Jialei Cui, Hao Ding, Mengnan Dong, Angang Du, Chenzhuang Du, Dikang Du, Yulun Du, Yu Fan, Yichen Feng, Kelin Fu, Bofei Gao, Hongcheng Gao, Peizhong Gao, Tong Gao, Xinran Gu, Longyu Guan, Haiqing Guo, Jianhang Guo, Hao Hu, Xiaoru Hao, Tianhong He, Weiran He, Wenyang He, Chao Hong, Yangyang Hu, Zhenxing Hu, Weixiao Huang, Zhiqi Huang, Zihao Huang, Tao Jiang, Zhejun Jiang, Xinyi Jin, Yongsheng Kang, Guokun Lai, Cheng Li, Fang Li, Haoyang Li, Ming Li, Wentao Li, Yanhao Li, Yiwei Li, Zhaowei Li, Zheming Li, Hongzhan Lin, Xiaohan Lin, Zongyu Lin, Chengyin Liu, Chenyu Liu, Hongzhang Liu, Jingyuan Liu, Junqi Liu, Liang Liu, Shaowei Liu, T. Y. Liu, Tianwei Liu, Weizhou Liu, Yangyang Liu, Yibo Liu, Yiping Liu, Yue Liu, Zhengying Liu, Enzhe Lu, Lijun Lu, Shengling Ma, Xinyu Ma, Yingwei Ma, Shaoguang Mao, Jie Mei, Xin Men, Yibo Miao, Siyuan Pan, Yebo Peng, Ruoyu Qin, Bowen Qu, Zeyu Shang, Lidong Shi, Shengyuan Shi, Feifan Song, Jianlin Su, Zhengyuan Su, Xinjie Sun, Flood Sung, Heyi Tang, Jiawen Tao, Qifeng Teng, Chensi Wang, Dinglu Wang, Feng Wang, and Haiming Wang. Kimi K2: open agentic intelligence. _CoRR_ , abs/2507.20534, 2025. 

- Mislav Balunovi´c, Jasper Dekoninck, Ivo Petrov, Nikola Jovanovi´c, and Martin Vechev. Matharena: Evaluating llms on uncontaminated math competitions, February 2025. URL https://matharena. ai/. 

- Mark Chen, Jerry Tworek, Heewoo Jun, Qiming Yuan, Henrique Pondé de Oliveira Pinto, Jared Kaplan, Harri Edwards, Yuri Burda, Nicholas Joseph, Greg Brockman, Alex Ray, Raul Puri, Gretchen Krueger, Michael Petrov, Heidy Khlaaf, Girish Sastry, Pamela Mishkin, Brooke Chan, Scott Gray, Nick Ryder, Mikhail Pavlov, Alethea Power, Lukasz Kaiser, Mohammad Bavarian, Clemens Winter, Philippe Tillet, Felipe Petroski Such, Dave Cummings, Matthias Plappert, Fotios Chantzis, Elizabeth Barnes, Ariel Herbert-Voss, William Hebgen Guss, Alex Nichol, Alex Paino, Nikolas Tezak, Jie Tang, Igor Babuschkin, Suchir Balaji, Shantanu Jain, William Saunders, Christopher Hesse, Andrew N. Carr, Jan Leike, Joshua Achiam, Vedant Misra, Evan Morikawa, Alec Radford, Matthew Knight, Miles Brundage, Mira Murati, Katie Mayer, Peter Welinder, Bob McGrew, Dario Amodei, Sam McCandlish, Ilya Sutskever, and Wojciech Zaremba. Evaluating large language models trained on code. _arXiv preprint arXiv:2107.03374_ , 2021. 

- Gheorghe Comanici, Eric Bieber, Mike Schaekermann, Ice Pasupat, Noveen Sachdeva, Inderjit S. Dhillon, Marcel Blistein, Ori Ram, Dan Zhang, Evan Rosen, Luke Marris, Sam Petulla, Colin Gaffney, Asaf Aharoni, Nathan Lintz, Tiago Cardal Pais, Henrik Jacobsson, Idan Szpektor, NanJiang Jiang, Krishna Haridasan, Ahmed Omran, Nikunj Saunshi, Dara Bahri, Gaurav Mishra, Eric Chu, Toby Boyd, Brad Hekman, Aaron Parisi, Chaoyi Zhang, Kornraphop Kawintiranon, Tania Bedrax-Weiss, Oliver Wang, Ya Xu, Ollie Purkiss, Uri Mendlovic, Ilaï Deutel, Nam Nguyen, Adam Langley, Flip Korn, Lucia Rossazza, Alexandre Ramé, Sagar Waghmare, Helen Miller, Nathan Byrd, Ashrith Sheshan, Sangnie Bhardwaj, Pawel Janus, Tero Rissa, Dan Horgan, Sharon Silver, Ayzaan Wahid, Sergey Brin, Yves Raimond, Klemen Kloboves, Cindy Wang, Nitesh Bharadwaj Gundavarapu, Ilia Shumailov, Bo Wang, Mantas Pajarskas, Joe Heyward, Martin Nikoltchev, Maciej Kula, Hao Zhou, Zachary Garrett, Sushant Kafle, Sercan Arik, Ankita Goel, Mingyao Yang, Jiho Park, Koji Kojima, Parsa Mahmoudieh, Koray Kavukcuoglu, Grace Chen, Doug Fritz, Anton Bulyenov, Sudeshna Roy, Dimitris Paparas, Hadar Shemtov, Bo-Juen Chen, Robin Strudel, David Reitter, Aurko Roy, Andrey Vlasov, Changwan Ryu, Chas Leichner, Haichuan Yang, Zelda Mariet, Denis Vnukov, Tim Sohn, Amy Stuart, Wei Liang, Minmin Chen, Praynaa Rawlani, Christy Koh, JD Co-Reyes, Guangda Lai, Praseem Banzal, Dimitrios Vytiniotis, Jieru Mei, and Mu Cai. Gemini 2.5: Pushing the frontier with advanced reasoning, multimodality, long context, and next-generation agentic capabilities. _arXiv preprint arXiv:2507.06261_ , 2025. 

11 

Preprint, March 2026 

- Yihong Dong, Xue Jiang, Zhi Jin, and Ge Li. Self-collaboration code generation via chatgpt. _ACM Trans. Softw. Eng. Methodol._ , 33(7):189:1–189:38, 2024a. 

- Yihong Dong, Xue Jiang, Huanyu Liu, Zhi Jin, Bin Gu, Mengfei Yang, and Ge Li. Generalization or memorization: Data contamination and trustworthy evaluation for large language models. In _ACL (Findings)_ , Findings of ACL, pp. 12039–12050. Association for Computational Linguistics, 2024b. 

- Yihong Dong, Xue Jiang, Jiaru Qian, Tian Wang, Kechi Zhang, Zhi Jin, and Ge Li. A survey on code generation with llm-based agents. _CoRR_ , abs/2508.00083, 2025a. 

- Yihong Dong, Xue Jiang, Yongding Tao, Huanyu Liu, Kechi Zhang, Lili Mou, Rongyu Cao, Yingwei Ma, Jue Chen, Binhua Li, Zhi Jin, Fei Huang, Yongbin Li, and Ge Li. RL-PLUS: countering capability boundary collapse of llms in reinforcement learning with hybrid-policy optimization. _CoRR_ , abs/2508.00222, 2025b. 

- Sachin Goyal, Ziwei Ji, Ankit Singh Rawat, Aditya Krishna Menon, Sanjiv Kumar, and Vaishnavh Nagarajan. Think before you speak: Training language models with pause tokens. In _The Twelfth International Conference on Learning Representations_ , 2024. URL https://openreview.net/ forum?id=ph04CRkPdC. 

- Daya Guo, Qihao Zhu, Dejian Yang, Zhenda Xie, Kai Dong, Wentao Zhang, Guanting Chen, Xiao Bi, Y. Wu, Y. K. Li, Fuli Luo, Yingfei Xiong, and Wenfeng Liang. Deepseek-coder: When the large language model meets programming–the rise of code intelligence. _arXiv preprint arXiv:2401.14196_ , 2024. 

- Daya Guo, Dejian Yang, Haowei Zhang, Junxiao Song, Ruoyu Zhang, Runxin Xu, Qihao Zhu, Shirong Ma, Peiyi Wang, Xiao Bi, Xiaokang Zhang, Xingkai Yu, Yu Wu, Z. F. Wu, Zhibin Gou, Zhihong Shao, Zhuoshu Li, Ziyi Gao, Aixin Liu, Bing Xue, Bingxuan Wang, Bochao Wu, Bei Feng, Chengda Lu, Chenggang Zhao, Chengqi Deng, Chenyu Zhang, Chong Ruan, Damai Dai, Deli Chen, Dongjie Ji, Erhang Li, Fangyun Lin, Fucong Dai, Fuli Luo, Guangbo Hao, Guanting Chen, Guowei Li, H. Zhang, Han Bao, Hanwei Xu, Haocheng Wang, Honghui Ding, Huajian Xin, Huazuo Gao, Hui Qu, Hui Li, Jianzhong Guo, Jiashi Li, Jiawei Wang, Jingchang Chen, Jingyang Yuan, Junjie Qiu, Junlong Li, J. L. Cai, Jiaqi Ni, Jian Liang, Jin Chen, Kai Dong, Kai Hu, Kaige Gao, Kang Guan, Kexin Huang, Kuai Yu, Lean Wang, Lecong Zhang, Liang Zhao, Litong Wang, Liyue Zhang, Lei Xu, Leyi Xia, Mingchuan Zhang, Minghua Zhang, Minghui Tang, Meng Li, Miaojun Wang, Mingming Li, Ning Tian, Panpan Huang, Peng Zhang, Qiancheng Wang, Qinyu Chen, Qiushi Du, Ruiqi Ge, Ruisong Zhang, Ruizhe Pan, Runji Wang, R. J. Chen, R. L. Jin, Ruyi Chen, Shanghao Lu, Shangyan Zhou, Shanhuang Chen, Shengfeng Ye, Shiyu Wang, Shuiping Yu, Shunfeng Zhou, Shuting Pan, and S. S. Li. DeepSeek-R1 incentivizes reasoning in LLMs through reinforcement learning. _Nature_ , 645(8081):633, 2025a. 

- Ziyu Guo, Renrui Zhang, Hongyu Li, Manyuan Zhang, Xinyan Chen, Sifan Wang, Yan Feng, Peng Pei, and Pheng-Ann Heng. Thinking-while-generating: Interleaving textual reasoning throughout visual generation, 2025b. URL https://arxiv.org/abs/2511.16671. 

- Jujie He, Jiacai Liu, Chris Yuhao Liu, Rui Yan, Chaojie Wang, Peng Cheng, Xiaoyu Zhang, Fuxiang Zhang, Jiacheng Xu, Wei Shen, Siyuan Li, Liang Zeng, Tianwen Wei, Cheng Cheng, Bo An, Yang Liu, and Yahui Zhou. Skywork open reasoner 1 technical report. _arXiv preprint arXiv:2505.22312_ , 2025. 

- Edward J. Hu, Yelong Shen, Phillip Wallis, Zeyuan Allen-Zhu, Yuanzhi Li, Shean Wang, Lu Wang, and Weizhu Chen. Lora: Low-rank adaptation of large language models. In _ICLR_ . OpenReview.net, 2022. 

- Hugging Face. Open r1: A fully open reproduction of deepseek-r1, January 2025. URL https: //github.com/huggingface/open-r1. 

- Binyuan Hui, Jian Yang, Zeyu Cui, Jiaxi Yang, Dayiheng Liu, Lei Zhang, Tianyu Liu, Jiajun Zhang, Bowen Yu, Kai Dang, An Yang, Rui Men, Fei Huang, Xingzhang Ren, Xuancheng Ren, Jingren Zhou, and Junyang Lin. Qwen2. 5-coder technical report. _arXiv preprint arXiv:2409.12186_ , 2024. 

12 

Preprint, March 2026 

- Aaron Jaech, Adam Kalai, Adam Lerer, Adam Richardson, Ahmed El-Kishky, Aiden Low, Alec Helyar, Aleksander Madry, Alex Beutel, Alex Carney, Alex Iftimie, Alex Karpenko, Alex Tachard Passos, Alexander Neitz, Alexander Prokofiev, Alexander Wei, Allison Tam, Ally Bennett, Ananya Kumar, Andre Saraiva, Andrea Vallone, Andrew Duberstein, Andrew Kondrich, Andrey Mishchenko, Andy Applebaum, Angela Jiang, Ashvin Nair, Barret Zoph, Behrooz Ghorbani, Ben Rossen, Benjamin Sokolowsky, Boaz Barak, Bob McGrew, Borys Minaiev, Botao Hao, Bowen Baker, Brandon Houghton, Brandon McKinzie, Brydon Eastman, Camillo Lugaresi, Cary Bassin, Cary Hudson, Chak Ming Li, Charles de Bourcy, Chelsea Voss, Chen Shen, Chong Zhang, Chris Koch, Chris Orsinger, Christopher Hesse, Claudia Fischer, Clive Chan, Dan Roberts, Daniel Kappler, Daniel Levy, Daniel Selsam, David Dohan, David Farhi, David Mely, David Robinson, Dimitris Tsipras, Doug Li, Dragos Oprica, Eben Freeman, Eddie Zhang, Edmund Wong, Elizabeth Proehl, Enoch Cheung, Eric Mitchell, Eric Wallace, Erik Ritter, Evan Mays, Fan Wang, Felipe Petroski Such, Filippo Raso, Florencia Leoni, Foivos Tsimpourlas, Francis Song, Fred von Lohmann, Freddie Sulit, Geoff Salmon, Giambattista Parascandolo, Gildas Chabot, Grace Zhao, Greg Brockman, Guillaume Leclerc, Hadi Salman, Haiming Bao, Hao Sheng, Hart Andrin, Hessam Bagherinezhad, Hongyu Ren, Hunter Lightman, Hyung Won Chung, Ian Kivlichan, Ian O’Connell, Ian Osband, Ignasi Clavera Gilaberte, and Ilge Akkaya. Openai o1 system card. _CoRR_ , abs/2412.16720, 2024. 

- Naman Jain, King Han, Alex Gu, Wen-Ding Li, Fanjia Yan, Tianjun Zhang, Sida Wang, Armando Solar-Lezama, Koushik Sen, and Ion Stoica. Livecodebench: Holistic and contamination free evaluation of large language models for code. _arXiv preprint arXiv:2403.07974_ , 2024. 

- Xue Jiang, Yihong Dong, Lecheng Wang, Zheng Fang, Qiwei Shang, Ge Li, Zhi Jin, and Wenpin Jiao. Self-planning code generation with large language models. _ACM Trans. Softw. Eng. Methodol._ , 33 (7):182:1–182:30, 2024. 

- Xue Jiang, Yihong Dong, Mengyang Liu, Hongyi Deng, Tian Wang, Yongding Tao, Rongyu Cao, Binhua Li, Zhi Jin, Wenpin Jiao, Fei Huang, Yongbin Li, and Ge Li. Coderl+: Improving code generation via reinforcement with execution semantics alignment. _CoRR_ , abs/2510.18471, 2025. 

- Xue Jiang, Jiaru Qian, Xianjie Shi, Chenjie Li, Hao Zhu, Ziyu Wang, Jielun Zhang, Zheyu Zhao, Kechi Zhang, Jia Li, Wenpin Jiao, Zhi Jin, Ge Li, and Yihong Dong. KOCO-BENCH: can large language models leverage domain knowledge in software development? _CoRR_ , abs/2601.13240, 2026. 

- Takeshi Kojima, Shixiang Shane Gu, Machel Reid, Yutaka Matsuo, and Yusuke Iwasawa. Large language models are zero-shot reasoners. In _NeurIPS_ , 2022. 

- Junlong Li, Daya Guo, Dejian Yang, Runxin Xu, Yu Wu, and Junxian He. Codei/o: Condensing reasoning patterns via code input-output prediction. _CoRR_ , abs/2502.07316, 2025a. 

- Qingyao Li, Xinyi Dai, Xiangyang Li, Weinan Zhang, Yasheng Wang, Ruiming Tang, and Yong Yu. Codeprm: Execution feedback-enhanced process reward model for code generation. In _Findings of the Association for Computational Linguistics: ACL 2025_ , pp. 8169–8182, 2025b. 

- Anthony Liang, Jonathan Berant, Adam Fisch, Abhimanyu Goyal, Kalpesh Krishna, and Jacob Eisenstein. Plantain: Plan-answer interleaved reasoning, 2025. URL https://arxiv.org/abs/ 2512.03176. 

- Anton Lozhkov, Raymond Li, Loubna Ben Allal, Federico Cassano, Joel Lamy-Poirier, Nouamane Tazi, Ao Tang, Dmytro Pykhtar, Jiawei Liu, Yuxiang Wei, Tianyang Liu, Max Tian, Denis Kocetkov, Arthur Zucker, Younes Belkada, Zijian Wang, Qian Liu, Dmitry Abulkhanov, Indraneil Paul, Zhuang Li, Wen-Ding Li, Megan Risdal, Jia Li, Jian Zhu, Terry Yue Zhuo, Evgenii Zheltonozhskii, Nii Osae Osae Dade, Wenhao Yu, Lucas Krauß, Naman Jain, Yixuan Su, Xuanli He, Manan Dey, Edoardo Abati, Yekun Chai, Niklas Muennighoff, Xiangru Tang, Muhtasham Oblokulov, Christopher Akiki, Marc Marone, Chenghao Mou, Mayank Mishra, Alex Gu, Binyuan Hui, Tri Dao, Armel Zebaze, Olivier Dehaene, Nicolas Patry, Canwen Xu, Julian McAuley, Han Hu, Torsten Scholak, Sebastien Paquet, Jennifer Robinson, Carolyn Jane Anderson, Nicolas Chapados, Mostofa Patwary, Nima Tajbakhsh, Yacine Jernite, Carlos Muñoz Ferrandis, Lingming Zhang, Sean Hughes, Thomas Wolf, Arjun Guha, Leandro von Werra, and Harm de Vries. Starcoder 2 and the stack v2: The next generation, 2024. URL https://arxiv.org/abs/2402.19173. 

13 

Preprint, March 2026 

Mathematical Association of America. American invitational mathematics examination (aime) 2024. https://maa.org/maa-invitational-competitions/, 2024. 

Mathematical Association of America. American invitational mathematics examination (aime) 2025. https://maa.org/maa-invitational-competitions/, 2025. 

- Meta AI. Introducing llama 3.1: Our most capable models to date. https://ai.meta.com/blog/ meta-llama-3-1/, jul 2024. Accessed: 2025-10-06. 

- Jacob Pfau, William Merrill, and Samuel R. Bowman. Let’s think dot by dot: Hidden computation in transformer language models. In _First Conference on Language Modeling_ , 2024. URL https: //openreview.net/forum?id=NikbrdtYvG. 

- Baptiste Rozière, Jonas Gehring, Fabian Gloeckle, Sten Sootla, Itai Gat, Xiaoqing Ellen Tan, Yossi Adi, Jingyu Liu, Romain Sauvestre, Tal Remez, Jérémy Rapin, Artyom Kozhevnikov, Ivan Evtimov, Joanna Bitton, Manish Bhatt, Cristian Canton Ferrer, Aaron Grattafiori, Wenhan Xiong, Alexandre Défossez, Jade Copet, Faisal Azhar, Hugo Touvron, Louis Martin, Nicolas Usunier, Thomas Scialom, and Gabriel Synnaeve. Code llama: Open foundation models for code. _arXiv preprint arXiv:2308.12950_ , 2023. 

- John Schulman and Thinking Machines Lab. Lora without regret. _Thinking Machines Lab: Connectionism_ , 2025. doi: 10.64434/tml.20250929. https://thinkingmachines.ai/blog/lora/. 

- John Schulman, Filip Wolski, Prafulla Dhariwal, Alec Radford, and Oleg Klimov. Proximal policy optimization algorithms. _arXiv preprint arXiv:1707.06347_ , 2017. 

- Zhihong Shao, Peiyi Wang, Qihao Zhu, Runxin Xu, Junxiao Song, Mingchuan Zhang, Y. K. Li, Y. Wu, and Daya Guo. Deepseekmath: Pushing the limits of mathematical reasoning in open language models. _CoRR_ , abs/2402.03300, 2024. 

- Guangming Sheng, Chi Zhang, Zilingfeng Ye, Xibin Wu, Wang Zhang, Ru Zhang, Yanghua Peng, Haibin Lin, and Chuan Wu. Hybridflow: A flexible and efficient rlhf framework. _arXiv preprint arXiv: 2409.19256_ , 2024. 

Lingxiao Tang, He Ye, Zhongxin Liu, Xiaoxue Ren, and Lingfeng Bao. Codereasoner: Enhancing the code reasoning ability with reinforcement learning. _arXiv preprint arXiv:2507.17548_ , 2025. 

- Sijie Wang, Quanjiang Guo, Kai Zhao, Yawei Zhang, Xin Li, Xiang Li, Siqi Li, Rui She, Shangshu Yu, and Wee Peng Tay. CodeBoost: Boosting code LLMs by squeezing knowledge from code snippets with rl. _arXiv preprint arXiv:2508.05242_ , 2025. 

- Xuezhi Wang, Jason Wei, Dale Schuurmans, Quoc V. Le, Ed H. Chi, Sharan Narang, Aakanksha Chowdhery, and Denny Zhou. Self-consistency improves chain of thought reasoning in language models. In _ICLR_ . OpenReview.net, 2023. 

- Jason Wei, Xuezhi Wang, Dale Schuurmans, Maarten Bosma, Brian Ichter, Fei Xia, Ed H. Chi, Quoc V. Le, and Denny Zhou. Chain-of-thought prompting elicits reasoning in large language models. _Advances in neural information processing systems_ , 35:24824–24837, 2022. 

- Yunhui Xia, Wei Shen, Yan Wang, Jason Klein Liu, Huifeng Sun, Siyue Wu, Jian Hu, and Xiaolong Xu. Leetcodedataset: A temporal dataset for robust evaluation and efficient training of code llms. _arXiv preprint arXiv:2504.14655_ , 2025. 

- Roy Xie, David Qiu, Deepak Gopinath, Dong Lin, Yanchao Sun, Chong Wang, Saloni Potdar, and Bhuwan Dhingra. Interleaved reasoning for large language models via reinforcement learning. _CoRR_ , abs/2505.19640, 2025. 

- Shunyu Yao, Dian Yu, Jeffrey Zhao, Izhak Shafran, Tom Griffiths, Yuan Cao, and Karthik Narasimhan. Tree of thoughts: Deliberate problem solving with large language models. In _NeurIPS_ , 2023. 

- Denny Zhou, Nathanael Schärli, Le Hou, Jason Wei, Nathan Scales, Xuezhi Wang, Dale Schuurmans, Claire Cui, Olivier Bousquet, Quoc V. Le, and Ed H. Chi. Least-to-most prompting enables complex reasoning in large language models. In _ICLR_ . OpenReview.net, 2023. 

14 

Preprint, March 2026 

## A Token Cost Breakdown 

Table 6 provides a detailed breakdown of reasoning token costs. For GRPO and CoT, the token cost consists entirely of upfront thinking tokens. For THINK-ANYWHERE, we separately report the upfront thinking length and the <thinkanywhere> block length. The upfront thinking phase of THINK-ANYWHERE is substantially shorter than that of GRPO and CoT across benchmarks, and the additional <thinkanywhere> tokens are modest in comparison, resulting in a net reduction in total reasoning token usage. 

Table 6: Breakdown of reasoning token costs. For THINK-ANYWHERE, the two numbers denote upfront thinking length + <thinkanywhere> block length. 

|**Method**|**HumanEval**|**MBPP**|**LeetCode**|
|---|---|---|---|
|GRPO|309.4|325.2|440.7|
|CoT|348.8|372.0|577.0|
|THINK-ANYWHERE|215.6 + 22.5|183.2 + 23.2|283.0 + 22.9|



## B Thinking Block Statistics Across Training Stages 

To clarify the respective contributions of cold-start SFT and RLVR, we analyze the average frequency (Avg.Freq) and average length (Avg.Len) of <thinkanywhere> blocks across different training stages, as shown in Table 7. 

The base model never invokes thinking blocks during code generation. Even with explicit prompting (THINK-ANYWHERE Prompting), the model produces very few <thinkanywhere> blocks (frequency near zero) with abnormally long lengths, indicating that prompting alone cannot reliably elicit THINKANYWHERE behavior and that this capability is unlikely to originate from pre-training. After cold-start SFT, the model generates <thinkanywhere> blocks at a normal frequency and length, demonstrating that SFT successfully teaches the model to imitate the THINK-ANYWHERE reasoning pattern and establishes a solid foundation for subsequent RL training. After RL training, the frequency and length of <thinkanywhere> blocks decrease slightly compared to the SFT stage, while pass@1 improves substantially (as shown in Table 5). This indicates that RL does not simply increase the number of thinking tokens; rather, it refines the model’s ability to invoke reasoning on demand, enabling more concise and targeted deliberation at positions where it is truly needed. This is fully consistent with the design goal of THINK-ANYWHERE. 

Table 7: Average frequency and length of <thinkanywhere> blocks across training stages. 

|**Dataset**|**Model**|**Avg.Freq**|**Avg.Len**|
|---|---|---|---|
||Base Model|0|0|
|HumanEval|THINK-ANYWHERE(Prompting)|0.24|113.5|
||THINK-ANYWHERE(SFT)|6.69|31.9|
||THINK-ANYWHERE(Ours)|6.15|22.5|
||Base Model|0|0|
|MBPP|THINK-ANYWHERE(Prompting)|0.53|66.4|
||THINK-ANYWHERE(SFT)|5.76|33.4|
||THINK-ANYWHERE(Ours)|5.24|23.2|
||Base Model|0|0|
|LeetCode|THINK-ANYWHERE(Prompting)|0.31|219.7|
||THINK-ANYWHERE(SFT)|11.28|34.5|
||THINK-ANYWHERE(Ours)|11.26|22.9|



15