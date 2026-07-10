[![van der Schaar Lab](https://www.vanderschaar-lab.com/wp-content/uploads/2020/04/transpLogo_icon_plus.png)](https://www.vanderschaar-lab.com/)

- Search
- [LinkedIn](https://www.linkedin.com/in/mihaela-van-der-schaar/)
- [Twitter](https://twitter.com/MihaelaVDS)
- [YouTube](https://www.youtube.com/vanderSchaarLab)
- [GitHub](https://github.com/vanderschaarlab)

[Facebook](https://www.vanderschaar-lab.com/l2mac/#) [X](https://www.vanderschaar-lab.com/l2mac/#) [Reddit](https://www.vanderschaar-lab.com/l2mac/#) [Pinterest](https://www.vanderschaar-lab.com/l2mac/#)Email

[New publication](https://www.vanderschaar-lab.com/category/new-publication/) [News](https://www.vanderschaar-lab.com/category/news/)

# L2MAC: Large Language Model Automatic Computer for Extensive Code Generation

[![](https://www.vanderschaar-lab.com/wp-content/uploads/2024/03/1681086378458-150x150.jpeg)Joseph Ginsberg](https://www.vanderschaar-lab.com/author/joseph/)[![](https://www.vanderschaar-lab.com/wp-content/uploads/2021/10/Sam_photo_sq-150x150.jpg)Sam Holt](https://www.vanderschaar-lab.com/author/sam/)

April 15, 2024

6 min read

With the recent meteoric rise of procedural text-generating applications such as ChatGPT, the inherent limitations of such large language model (LLM) frameworks have become increasingly evident. Many have noticed that, despite their remarkable ability to generate short bursts of highly coherent text, these applications struggle with long-term memory limitations – for both reading and writing – that result in a sort of digital amnesia. This is because LLM frameworks have a goldfish-like memory: after processing a certain number of tokens (a group of characters that the model uses as building blocks), surpassing what is known as the context window constraint, they have no memory of the tokens outside their context window; akin to a _limited attention span_.

This _limited attention span_ is problematic for tasks that involve the generation of large cohesive outputs, as the total generated output expected is significantly greater than the context window constraint. Such tasks, for example, include generating a large code base complete with many files, where each line of code could crucially depend on any other line of code, i.e., be cohesive and coherent to all the other lines for proper functioning.

Hailed as one of the most promising potential benefits of LLMs, automatic code-base generation allows large programs to be procedurally generated within minutes, potentially revolutionizing the landscape of software development by significantly accelerating the traditionally time-consuming process of coding. Yet while LLMs are currently adept at generating short snippets of code, longer code generation, which requires maintaining proper context over extended sequences of instructions, consistently causes them to break down. Frustratingly, this memory limitation of LLMs is inherent, as the context window is baked into the underlying architecture of each model – it’s not simply a parameter that can later be tweaked at will. Once the LLM has been created, the size of its context window, part and parcel of the model itself, is permanently fixed.

One seemingly simple solution would be to augment the LLM with extra external memory to read from, containing relevant information for the model to draw upon when generating larger bodies of text. Yet this approach is only viable for particular tasks, typically those for which the body of knowledge the LLM will draw upon is distinctly known and can be formatted in an easily accessible data structure, such as a dictionary or database. For generative tasks involving creative, unique, and original output, no such fixed body of information is available. Such proposed solutions also adopt poor memory _writing_ strategies: simply appending newly generated data sequentially to an external memory source will render any errors in the text essentially permanent. In order for an LLM to effectively generate large sections of error-free text or code, a more dynamic form of external memory is required, one that can be updated continuously as the model is running and which allows it to maintain long-term semantic and syntactic consistency.

**More technically, a viable LLM architecture for extensive output generation requires:**

1. **At each step of the procedural generation, the LLM has access to contextually relevant information that allows it to carry out the current instruction. This context must be dynamically managed to ensure that it does not exceed the built-in context window constraint.**
2. **The LLM is itself endowed with the ability to read and write memory, allowing it to both obtain and update relevant parts of previously generated outputs on the fly.**
3. **The LLM is capable of self-checking its output for mistakes, and discovered errors – whether they be syntactic or semantic – can be remedied by iteration.**

Accordingly, we at the van der Schaar Lab have recently introduced [L2MAC](https://openreview.net/pdf?id=EhrzQwsV4K) (LLM Automatic Computer), the first practical LLM-based stored-program automatic computer (von Neumann architecture) framework for long and consistent output generation tasks. The design of L2MAC is a practical implementation of the von Neumann architecture, which is a stored-program computer model. Here, the program is a set of sequential instructions to execute at each step. These instructions are stored in an external memory alongside all of the inputs and previous outputs from the program’s operation (including the final output, which is read directly from this external memory).

**This is accepted, and we will present L2MAC at the International Conference on Learning Representations (ICLR) in Vienna in May 2024.**

Such a framework successfully implements the above three conditions through the introduction of a Control Unit, which orchestrates the execution of the LLM and its interaction with the external memory. As outlined in the figure below, the LLM first generates a task-orientated set of sequential instructions from the user input prompt that contains specific requirements for the generated output to have. The Control Unit dynamically controls the LLM’s context, so it always includes the next unresolved instruction to execute, appropriate parts of the external memory, and information about the execution of past instructions. It also declutters the context when it approaches its limit. Crucially, the Control Unit provides the LLM tools to read and update any existing region of the external memory or extend it with new outputs. Furthermore, to ensure coherent outputs, the Control Unit checks the generated output of the LLM for any syntactic or semantic errors, and if any are found, they are corrected through iteration with the LLM.

![](https://www.vanderschaar-lab.com/wp-content/uploads/2024/04/l2mac-block-diagram-1024x431.png)

In our experiments, a practical instantiation of L2MAC for generating large, extensive code-bases was created, dubbed Code-L2MAC. This excels in generating fully functional, error-minimal code that contains pre-specified user features, outperforming other previously proposed methods. Additionally, we were able to empirically observe that Code-L2MAC successfully implemented all three conditions outlined above: task-oriented context management, precise read/write operations of memory, and error detection and correction. We further evaluated Code-L2MAC on the standard HumanEval benchmark and observed that it achieves a competitive score of 90.2% Pass@1, ranking 4th globally on the [leaderboard](https://paperswithcode.com/sota/code-generation-on-humaneval). Also, we showed that L2MAC works for general-purpose, extensive text-based tasks, such as writing an entire book, as seen in the [paper](https://openreview.net/pdf?id=EhrzQwsV4K).

While L2MAC is an initial work, it is an important step forward in advancing the capabilities of language models and their application in tasks such as extensive code-base generation. As we continue to progress, exciting avenues for future work include addressing complex instruction flows (such as having instructions with if / else conditions and loops) and enhancing the interpretability of prompt programs. These challenges mark the beginning of a promising journey toward advancing LLM-based systems for even greater capabilities and applications for solving large real-world tasks. We note that you can get started running L2MAC for your own task or building your own complete application with the corresponding [code](https://github.com/samholt/l2mac).

To illustrate the capabilities of L2MAC, we used it to create a full book from just a single input prompt. You can find the book [here](https://drive.google.com/file/d/13Z7WJdH9eBOcj7emaWRxkWUl1IETDfFT/view). Want to try it yourself? Here is the code we used to generate this book on [GitHub](https://samholt.github.io/L2MAC/guide/use_cases/book_generator.html).

_Many thanks to Samuel Holt, Max Luyten, and Mihaela van der Schaar for their helpful comments and edits. You can find their recently published paper on L2MAC_ [_here_](https://openreview.net/pdf?id=EhrzQwsV4K) _._

[Code](https://www.vanderschaar-lab.com/tag/code/) [LLM](https://www.vanderschaar-lab.com/tag/llm/)

![](https://www.vanderschaar-lab.com/wp-content/uploads/2024/03/1681086378458-150x150.jpeg)

#### Joseph Ginsberg

Joseph is a computer engineering and mathematics student enrolled in a joint program between Yeshiva and Columbia universities in New York City. He has collaborated with NASA on several computer science-related initiatives, focusing on areas like coding efficiency, and is now hoping to leverage that experience in the domain of machine learning.

Joseph advocates for a multidisciplinary approach to scientific research and has made significant contributions to a wide array of fields, including digital humanities, robotics, and computational astrophysics. At the van der Schaar lab, he is focused on understanding the potential partnerships between AI models and clinicians and how such alliances can improve risk diagnostics and treatment effect estimation. Additionally, he is exploring the guts of effective science communication and how best to accurately convey the risks and promises of advanced AI (especially with regard to medicine).

If you catch him outside of research, he is likely reading (often medieval manuscripts), running, or out with friends.

[View all posts](https://www.vanderschaar-lab.com/author/joseph/)

![](https://www.vanderschaar-lab.com/wp-content/uploads/2021/10/Sam_photo_sq-150x150.jpg)

#### Sam Holt

Sam holds a M.Eng. in Engineering Science from the University of Oxford, where he graduated with a first-class degree and numerous awards for academic excellence (placing 2nd in the year for his master’s thesis).

In the course of his studies, Sam undertook two machine learning research internships at the University of Oxford: one researching detecting and tracking cars in noisy radar data (for a self-driving car), and the other in economic time-series forecasting. He also initiated his own original research into noise reduction on propellers, developing a propeller design that emits 44% less noise.

Upon graduating, Sam worked for an Oxford spin out, Mind Foundry, investigating dialogue systems for an industrial client. He has also authored and taught an online machine learning course covering recent work, and shared his passion for machine learning through teaching students in a classroom at a London-based tech-MBA program. Previously, he has collaborated and led three quantitative financial research projects, alongside working in data science and software engineering for a quantitative finance startup, Fifth Row Technologies. He has also created proof-of-concept automation ML tools to help doctors in GP practices.

Sam’s research is supported by funding from AstraZeneca.

[View all posts](https://www.vanderschaar-lab.com/author/sam/)

#### You may also like

[News](https://www.vanderschaar-lab.com/category/news/)

## [Mihaela van der Schaar appointed the Chief AI Scientist at the Francis Crick Institute](https://www.vanderschaar-lab.com/crick-chief-ai-scientist/)

Mihaela van der Schaar appointed the Chief AI Scientist at the Francis Crick Institute

[![](https://www.vanderschaar-lab.com/wp-content/uploads/2025/08/Screen-Shot-2025-08-20-at-10.45.34-pm-150x150.png)Marika Niihori](https://www.vanderschaar-lab.com/author/marika/)

June 24, 2026

[Big ideas](https://www.vanderschaar-lab.com/category/big-ideas/) [News](https://www.vanderschaar-lab.com/category/news/)

## [From Phenomena to Problems: Open-Beginningness and the Next Frontier of AI](https://www.vanderschaar-lab.com/open-beginningness/)

A new white paper introduces open-beginningness: the capacity of AI to recognise when an observation outside its current task may warrant sustained attention and lead to a new or revised problem.

[![](https://www.vanderschaar-lab.com/wp-content/uploads/2020/04/IMG-20191212-WA0002-1-e1587984332248-150x150.jpg)Mihaela van der Schaar](https://www.vanderschaar-lab.com/author/mihaela/)

June 22, 2026

[Big ideas](https://www.vanderschaar-lab.com/category/big-ideas/) [News](https://www.vanderschaar-lab.com/category/news/)

## [From AI Methods to Clinical-Trial Transformation: Ten Years of Research at the van der Schaar Lab Research](https://www.vanderschaar-lab.com/ai-enabled-clinical-trials/)

Explore a decade of research on AI-enabled clinical trials, spanning causal AI, digital twins, synthetic data, adaptive trials and agentic AI.

[![](https://www.vanderschaar-lab.com/wp-content/uploads/2020/04/IMG-20191212-WA0002-1-e1587984332248-150x150.jpg)Mihaela van der Schaar](https://www.vanderschaar-lab.com/author/mihaela/)[![](https://www.vanderschaar-lab.com/wp-content/uploads/2025/08/Screen-Shot-2025-08-20-at-10.45.34-pm-150x150.png)Marika Niihori](https://www.vanderschaar-lab.com/author/marika/)

June 2, 2026