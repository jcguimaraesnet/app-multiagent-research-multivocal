The Journal of Systems and Software 241 (2026) 113009 



Contents lists available at ScienceDirect 

# The Journal of Systems & Software 

journal homepage: www.elsevier.com/locate/jss 



## Data augmentation of Python code refactoring datasets based on LLMs<sup>$,$$</sup> 

Vasilica-Andreea Moldovan ∗, Rareş Pătcaş ∗, Simona Motogna ∗ _Babeş-Bolyai University, Department of Computer Science, M. Kogalniceanu 1, Cluj-Napoca, 400084, Romania_ 

|A R T I C L E I N F O<br>A B S T R A C T|
|---|



|Dataset link:https://figshare.com/s/5df5df00f<br>39388dd35e6|Refactoring is a crucial software engineering practice aimed at improving code quality, yet automatically<br>detecting and predicting refactoring activities remains difficult due to the limited availability of labeled data.|
|---|---|
|_Keywords:_<br>Refactoring<br>Artificial Intelligence|This study examines how data augmentation can strengthen refactoring detection models. We experimented<br>with 4 augmentation methods, namely Back Translation from textual description, Back Translation from Java,<br>Generating Python code from existing comments, and Generating Python code from generated comments, and|
|AI in software refactoring|applied each of them using 4 large language models, specifically Gemini, GPT-4o, DeepSeek, and GPT-5-Nano.|
|Machine learning|Through these combinations, we generated new instances of paired pre-refactor and post-refactor functions|
|Data augmentation<br>|derived directly from the original ground truth pairs. We compute embedding-based cosine similarities between|
|LLMs in software engineering|original functions, refactored functions, and their generated counterparts to evaluate semantic fidelity and<br>proximity. We also validate and balance the resulting dataset to ensure it remains suitable for downstream<br>machine learning tasks. Our findings suggest that many augmented samples remain semantically aligned with<br>the original functions while adding diversity that improves robustness, reduces overfitting, and enhances<br>generalization in automated refactoring detection.|



### **1. Introduction** 

As software projects evolve, codebase often accumulates several inefficiencies that reduce performance, impact comprehension and complicate future maintenance. Refactoring has established itself as the main practice for maintaining software systems and for improving the overall quality of the code (Fowler, 1999). However, refactoring is a complex process and sometimes difficult to be included in project planning, which makes automation of refactoring gain constant interest from researchers and industry. In this context, availability of datasets for refactoring detection, recommendation and prioritization is an important aspect. 

One of the main issues present in refactoring datasets is represented by data imbalance, as identified in different studies (Alkharabsheh et al., 2022; Malhotra and Lata, 2021). The quality of an imbalanced dataset is also affected by its small size or by inappropriate representation of different refactoring types that might influence the results of refactoring detection or recommendation (Pecorelli et al., 2019). To mitigate data imbalance, additional samples must be introduced into the dataset, which requires the use of data augmentation techniques. One option is to augment the software quality metrics directly; however, this method can produce values that fail to accurately represent 

those originating from actual refactored code. A more reliable strategy is to augment the refactored code itself, thereby generating new refactoring instances and extracting the corresponding metrics from these newly produced code samples. 

In this study, we chose to use a Python refactoring instances dataset, due to the increased popularity of Python (StackOverflow, 2025) and its leading position in AI/ML applications. We focused on data augmentation techniques that involve code transformation instead of directly augmenting the features. We consider 4 main approaches based on: back-translation using a different programming language (more precisely, Java), back-translation from textual descriptions, code generation based on existing comments, and code generation from specifications obtained using CodeXGLUE on the refactored code. 

This paper extends our previous work (Moldovan et al., 2026) by conducting a more comprehensive experimental analysis. Specifically, we run all models across each method achieving a complete assessment, incorporating a larger set of experiments than before. The study also extends the considered models by adding DeepSeek and GPT-5-Nano, thus providing a more diverse comparative evaluation. Furthermore, the assessment process is improved by considering similarity-based metrics for code embeddings, providing a more rigorous and fine-grained evaluation of the generated refactorings. 

- $ This article is part of a Special issue entitled: ‘SEAA25’ published in The Journal of Systems & Software. 

> $$ Editor: Prof Raffaela Mirandola. 

> ∗ Corresponding authors. 

_E-mail addresses:_ vasilica.moldovan@ubbcluj.ro (V.-A. Moldovan), rares.patcas@ubbcluj.ro (R. Pătcaş), simona.motogna@ubbcluj.ro (S. Motogna). _URLs:_ http://www.cs.ubbcluj.ro/ (V.-A. Moldovan), http://www.cs.ubbcluj.ro/ (R. Pătcaş), http://www.cs.ubbcluj.ro/~motogna (S. Motogna). 

https://doi.org/10.1016/j.jss.2026.113009 

Received 28 November 2025; Received in revised form 3 June 2026; Accepted 15 June 2026 

Available online 18 June 2026 

0164-1212/© 2026 The Authors. Published by Elsevier Inc. This is an open access article under the CC BY-NC-ND license ( http://creativecommons.org/licenses/bync-nd/4.0/ ). 

_V.-A. Moldovan et al._ 

_The Journal of Systems & Software 241 (2026) 113009_ 

We express our contribution in three directions, namely a detailed analysis of source-code-level data-augmentation methods, a proposed pipeline for rectifying imbalanced datasets, and an augmented, validated, and balanced dataset suitable for refactoring detection, prioritization, recommendation, and related tasks. 

The distinctive aspects of our approach lie in: (i) synthesis of semantic-aware refactoring instances. While most of the prior work address feature augmentation or simple code level augmentation, our proposal generates new code intended to preserve structural and behavioral characteristics of the original refactoring instances and then derives specific metrics; and (ii) through our experiments, we show that LLM-based augmentation is a viable solution for imbalanced dataset augmentation, enhancing generalizability and reliability. 

The rest of the paper is organized as follows: the next section introduces the basic concepts and related work for refactoring and enhancement of datasets. Section 3 describes our approach, while the results from the performed experiments are presented in Section 4, followed by discussion and threats to validity. We end by stating conclusions and future research directions. 

### **2. Background** 

This section presents the theoretical concepts and reviews related work on refactoring. It then describes the data transformations we will perform, including data augmentation, computation and evaluation of code embeddings for similarity, and finally, dataset balancing. 

### _2.1. Refactoring_ 

Refactoring continues to attract significant attention because it is a crucial practice during maintenance and a well established technique for managing and improving the quality and efficiency of software systems. Various tools have been developed to support refactoring, and popular integrated development environments (IDEs) like Eclipse and IntelliJ include built-in refactoring features. In this study, we needed a tool able to detect method-level refactoring in Python, and we opted for PyRef. Atwi et al. (2021) due to its presence in research and practitioners communities. PyRef analyzes Python source code changes by parsing and examining only the modified parts to identify 9 specific refactoring types, producing a list of detected refactoring together with their associated locations. 

As mentioned in Motogna et al. (2024), numerous research efforts have explored the use of AI and machine learning methods for tasks such as refactoring detection, recommendation, and prioritization (Noei et al., 2025; Pecorelli et al., 2020b), among others. This continuous interest underlines the need for well-curated datasets to support this type of research. The study (Alkharabsheh et al., 2022) conducted experiments to assess the behavior of several ML models to detect God Class using balanced and unbalanced datasets. Their findings suggest that balancing does not impact the performance of classifiers. However, the study considers only one code smell and also uses strictly SMOTE to balance metric data and not the source code. This is an important differentiator for our study, as we stress that the augmentation should be applied to the source code, not the metrics or other features obtained from the code. 

In Malhotra and Lata (2021), the authors prove that balancing the dataset significantly improves the performance of maintainability prediction models. Since the maintainability prediction is close to our purposes as it involves code smells, hence refactoring opportunities, we address the problem of augmenting and balancing the dataset for refactoring investigation. 

### _2.2. Data augmentation techniques in software engineering_ 

With the rise of applying ML techniques and the continuous interest for empirical methods to Software Engineering (SE) problems, the issue of data augmentation became essential because it strengthens dataset diversity, addresses data scarcity, and enhances model robustness. In machine learning applications within SE, such as defect prediction, code summarization, refactoring detection, and bug localization, data augmentation techniques generate more comprehensive training datasets. These techniques vary from code transformations (e.g., renaming variables, modifying control flow), to synthetic data creation, and adversarial examples, all aimed at improving the model’s ability to generalize effectively. 

There are two main methods for augmenting data in Software Engineering research: 

**Feature level** : This approach applies augmentation directly to features extracted from source code, such as quality metrics or abstract syntax trees (ASTs). Techniques include adding noise, modifying feature values, or generating synthetic data. 

**Source code level** : This method involves modifying the actual source code to create diverse training samples. Common techniques include code transformations, injecting synthetic bugs, back-translation, or generating adversarial examples. 

One of the most known methods for feature level data augmentation is SMOTE (Fernandez et al., 2018). Even if the method’s primary functionality is to address data balancing, we consider it also as data augmentation technique because it generates new synthetic data for minority class instances, thereby effectively expanding the dataset. 

Based on the observation that traditional SMOTE introduces randomness, the study (Feng et al., 2021) introduces stable SMOTE-based techniques that methodically select minority class instances and interpolation points, thereby minimizing performance variability. The authors evaluate their approach on 26 datasets and 4 classification methods, demonstrating improvements in consistency and performance. The study recommends substituting conventional SMOTE with such stable approaches. 

Various techniques have been proposed for source code level data augmentation. The most notable include: code translation, consisting of transforming the code from one programming language to another and then converting back to the original language, or transforming the code to a textual description (independent of a programming language) and then generating the code again, using code snippets based of existing patterns of using ML models. In addition, to introduce diversity, some systematic transformations might be applied, such as variable renaming, statement reordering, or syntactic variations. 

In Chen and Lampouras (2023), three methods are assessed for data augmentation: back-translation, multilinguality and numeric-aware technique with the purpose of programming language translation and summarization using pre-trained language models (PLMs). The findings revealed improvement of accuracy for back-translation, but the results differ for different programming languages (C# and Java). The authors recommend future research on developing more robust evaluation techniques and improving back-translation methods to better manage diverse code pair translations. 

The empirical research study presented in Dong et al. (2023) considers source code as textual content and evaluates the effectiveness of NLP data augmentation techniques for 4 programming languages: Java, Python, Ruby and Go. The experiments included 4 DNN models, namely BagOfToken, SeqOfToken, CodeBERT and GraphCodeBERT. In addition, several refactoring operations have been applied, including adding dead code, extending if statements, and renaming methods. They conclude that except for specific methods with particular configuration, in general the NLP-based data augmentation techniques are not suitable for code learning, in which context specialized methods are needed. 

2 

_V.-A. Moldovan et al._ 

_The Journal of Systems & Software 241 (2026) 113009_ 

The study (Yu et al., 2022) introduced another data augmentation technique for source code that uses program transformations based on generalization of deep learning models. They use 18 transformation rules that preserve program semantics and were validated to maintain syntactic genuineness. They also proposed a Java-based tool, SPAT, to automatically apply these transformations and evaluated it across three major code-related tasks: method name prediction, code commenting, and code clone detection. They conclude that a transformation should preserve the syntactic and semantic form of the code fragment, and that deep learning models, such as Code2Vec, DeepCom, Hybrid-DeepCom, ASTNN, and TBCCD produce promising results, even if the performance might vary depending on model, dataset or task. 

Although several methods have shown good results, concerns remain about the validity of the augmented code, so its verification is recommended (Pan et al., 2024). 

### _2.3. Automatic code generation_ 

Classical techniques for automatic code generation include the use of predefined rules to create source code, and the topic has received an important boost by applying artificial intelligence and machine learning techniques for this task. The approach gained attraction in software development due to its ability to decrease human errors, boost efficiency, and automate repetitive programming tasks. The rise of large language models (LLMs) like GPT-4o, Gemini, and Claude, generated significant advancements, allowing developers to improve their productivity. One major concern is the quality of the generated code, since AI-based methods may introduce inconsistencies in naming conventions, coding standards, or optimizations. AI-based techniques for automatic code generation include: 

- **Large Language Models (LLMs)** — such as GPT, Codex, Copilot, in which source code is generated from prompts expressed in natural language; 

- **AI-Based Code Completion** — e.g. Copilot, Tabnine, IntelliCode, autocompleting the code while typing in a IDE; 

- **AI-Powered Code Refactoring** — for example, DeepCode that applies optimizations and refactoring on existing code. 

**Back-to-back translation (B2B translation)** represents the translation of code from one language to another and back, and can incorporate any of the listed methods for automatic code generation. Defined in general, for any type of language, natural or domain-specific, in this study our focus will be B2B translations between programming languages or from programming language to text description and back. There have been numerous contributions on the topic, this section describing the ones that are closer to our approach. 

The study (Ahmad et al., 2023) introduced a method using code summarization and generation to facilitate back-translation for converting code between Python and Java. Using PLBART, a sequenceto-sequence model pre-trained on coding tasks, they fine-tuned it to translate code into normal text and then regenerate equivalent code in another language. This technique was tested on a Java–Python dataset and evaluated using CodeBLEU and Computational Accuracy metrics, showing comparable results to state-of-the-art systems like TransCoder. 

In Liu et al. (2023), the authors propose the SDA-Trans model as a solution to error-prone and costly code translation. It incorporates syntax structure and domain knowledge to improve cross-lingual transfer. Experiments on translation tasks among Python, Java, and C++ demonstrate that SDA-Trans produces better results than largescale pre-trained models, especially when translating to languages not encountered before in training. The study concludes that using syntaxaware mechanisms and domain-specific knowledge, accuracy and effectiveness in program translation can be achieved even with limited data. 

### _2.4. Code embedding_ 

Code embeddings provide a vector-based representation of source code that captures patterns in structure and semantics, making them suitable for analyzing similarity between code fragments and for identifying recurring programming behaviors. In the context of this study, embeddings are used to evaluate how closely augmented refactorings preserve the behavior of the original functions while also supporting broader pattern analysis relevant to refactoring detection. 

Unlike traditional feature-based representations that rely on metrics or token counts, embeddings are learned automatically from large corpora of source code and encode latent properties such as API usage, control flow, design idioms, and naming conventions. This allows semantically related code fragments to appear close in the vector space even when they differ syntactically. 

A notable line of work treats code as structured data rather than plain text. In Alon et al. (2019), path-based embeddings are derived from Abstract Syntax Trees, aggregating structural paths into vectors capable of predicting semantic attributes such as method names. These representations are robust to superficial variations like formatting changes or variable renaming while remaining closely aligned with program logic. 

Another approach processes code as a token sequence using transformer-based masked language modeling. These sequence embeddings are effective for tasks such as completion, summarization, and translation, where contextual token patterns are significant, although they may capture less explicit structural information. 

More advanced techniques incorporate semantic signals from program analysis. For example, Guo et al. (2021) augments embeddings with data flow information that aligns variables to semantic dependencies and predicts structural edges, improving performance on code search, clone detection, and refinement tasks. 

Contrastive learning further refines embedding spaces by pulling equivalent code fragments closer and pushing unrelated samples apart. Dou et al. (2024) applies this strategy for clone detection, demonstrating robustness to stylistic variation. The study in Liu et al. (2025) evaluates multilingual embeddings for large-scale retrieval and shows that general-purpose embeddings can remain competitive even without explicitly modeling program structure. 

Similarity between embeddings is typically computed using distance measures such as cosine or Euclidean distance, allowing semantically related code fragments to be identified even when they differ syntactically. These metrics enable applications such as ranking refactoring candidates, detecting semantic clones, retrieving related functions, and verifying whether transformed code preserves its original behavior. 

### _2.5. Data balancing_ 

To ensure an efficient training process and achieve high model performance, regardless of the specific task, several key factors must be considered. One critical aspect is the distribution of the dataset, particularly the issue of class imbalance, which can significantly impact model generalization and prediction accuracy. Class imbalance occurs when certain classes are significantly underrepresented relative to others, which can lead to biased learning, reduced model generalization, and diminished predictive accuracy. Empirical evidence suggests that models trained on imbalanced datasets often exhibit a tendency to favor majority classes, resulting in poor performance on minority classes (Leevy et al., 2018). To mitigate these issues, a variety of data balancing techniques have been developed. 

Numerous studies have investigated the impact of class imbalance and evaluated a variety of data balancing techniques. For instance, Jadhav et al. (2022) conducted an extensive empirical study examining the effectiveness of preprocessing-level data balancing methods. The techniques considered included Under Sampling (US), Over Sampling (OS), Hybrid Sampling (HS), Random Over Sampling Examples (ROSE), 

3 

_V.-A. Moldovan et al._ 

_The Journal of Systems & Software 241 (2026) 113009_ 

Synthetic Minority Over Sampling Technique (SMOTE), and ClusteringBased Under Sampling (CBUS). The evaluation was performed across six different classifiers and 25 datasets exhibiting varying levels of imbalance ratio (IR). The study found that the ‘‘None’’ and ROSE strategies consistently underperformed, whereas other methods (US, OS, HS, SMOTE, and CBUS) generally led to improved classifier performance. Nevertheless, the degree of improvement was dependent on the specific classifier used. Statistical analyses employing Friedman and Nemenyi tests revealed significant differences among the data balancing techniques, while Kendall’s W coefficient indicated only partial agreement in the resulting rankings, suggesting that the effectiveness of these techniques varies with both the classifier and the dataset’s imbalance ratio. Overall, the study concluded that while data balancing techniques can enhance classification performance, further research is required to fully understand their applicability across diverse scenarios. 

Another notable large-scale empirical study examining the impact of data balancing techniques on machine learning-based code smell detection is presented by Pecorelli et al. (2020a). It presents the evaluation of several techniques, including no balancing, oversampling, undersampling, SMOTE, cost-sensitive classifiers, and one-class classifiers. The results indicated that SMOTE generally achieved the highest classification accuracy, although its training phase may not always be practical due to computational constraints. In contrast, avoiding data balancing did not substantially reduce model effectiveness, while methods focusing solely on the minority class (such as cost-sensitive and one-class classifiers) or other resampling strategies like class balancing and resampling, were largely ineffective. Additionally, the study confirmed that structural metrics alone are insufficient for accurate code smell detection, corroborating previous research emphasizing the importance of textual and historical metrics. Overall, the authors concluded that the evaluated data balancing approaches were inadequate for this domain and recommended further research to develop more effective techniques tailored for code smell detection. 

### **3. Our approach** 

Our main objective is to create a reliable data augmentation method for Python datasets focused on refactoring, ensuring the resulting dataset is balanced, contains valid code and is suitable for accurate detection, recommendation and prioritization of refactoring. Consequently, we seek to produce as result a consistent dataset that can be effectively used in future research on Python source code refactoring. We divide our objective in the following research questions: 

- _RQ1: To what extent does generated code preserve similarity with the original code?_ We intend to obtain an indicator for the quality of augmentation. We achieve this by computing embedding based similarity. 

- _RQ2: How do augmented instances impact refactoring detection models?_ Through this evaluation we aim to obtain an indicator regarding the quality of the augmented data. We conduct experiments with several classifiers (Random Forest, XGBoost, Naive Bayes and SVM) and compare the augmented dataset with the original one and with a SMOTE-enhanced dataset. 

toolkits, distributed systems, and various developer tools. The projects also span multiple size categories, from large systems (≥50 k _𝐿𝑂𝐶_ ) to medium (10k–50k LOC) and small codebases ( _<_ 10k LOC). This dataset is subject to augmentation using 4 methods, namely B2B translation using text, B2B translation using Java, code generation from comments and code generation from specifications obtained using CodeXGLUE. Each of the 4 data augmentation methods was applied using 4 different LLMs, resulting in a total of 16 newly generated datasets. The augmented code is then subject to validation, ensuring syntactical correctness, balancing, as the main objective of our efforts, and assessment using similarity metrics. Finally, we perform some experiments with the dataset with and without augmentation. 

### _3.2. Dataset_ 

We start with the Python Software Quality Dataset (Moldovan et al., 2024), which ensures a diverse range of software quality information, including SonarQube results for quality metrics and PySZZ bugfixing commit pairs, thus offering valuable insights into maintainability and defect resolution. Although this dataset was not primarily constructed for refactoring purposes, using the PyRef tool (Atwi et al., 2021), method-level refactoring instances were automatically identified by analyzing code changes across commits, and approximately 12k refactoring instances were detected, making it an excellent base for augmenting refactoring instances. This study applies data augmentation techniques to expand and balance the variety of refactoring types, thereby enhancing the performance of machine learning models in detecting and analyzing refactoring patterns. 

Refactoring instances were obtained through an automated detection process using PyRef, which enabled large-scale identification of method-level refactorings by analyzing fine-grained code changes across commits. This capability supports the systematic extraction of paired pre- and post-refactoring function versions, forming the basis for constructing transformation-aware datasets suitable for empirical software engineering studies. By operating directly on version history, the tool facilitates the capture of real-world refactoring activities across diverse project contexts. PyRef has also been employed in prior software engineering research investigating the effects of refactorings on software quality aspects such as security (Edward et al., 2024), supporting its relevance for building refactoring datasets in Python ecosystems. 

Our focal point is the REFACTORING_RECORD table, which contains detailed data about detected refactorings. Each entry specifies one or more refactoring types, the related commit hash, and the location (line) where the refactoring took place. To recognize the affected methods, we use GitHub API to access historical source code versions and employed a regex-based technique to extract the modified function signatures and method bodies. We captured all methods impacted by the refactoring, presenting them in both pre-commit and post-commit forms to clearly illustrate the code changes. This approach guarantees precise identification of refactored elements, facilitating more effective data augmentation and enhancing the accuracy of refactoring detection models (see Data Availability section for details about dataset). 

### _3.3. Data augmentation_ 

### _3.1. Methodology_ 

We structured our research study as a solution proposal (Petersen et al., 2008), using a descriptive and evaluative approach: we document different data augmentation strategies and we evaluate them against quality criteria and similarity measures. The pipeline taken in our study is depicted in Fig. 1: we formed a collection of projects based on the following inclusion criteria: the presence of Python source code and confirmed refactored code covering multiple refactoring types. The selected dataset is diverse in both application domain and project scale. It includes web frameworks, web applications, ML and deep learning 

As shown in Fig. 1, we evaluated 4 methods for augmenting the refactored code samples, which are detailed in this section. In particular, we applied back-translation by converting Python code to Java and then translating it back to Python; separately, we translated Python code into textual descriptions before reconstructing the Python code from those descriptions. In addition, we generated Python code from the comments in the original refactored examples. The last data augmentation method we applied was to create textual specifications from Python code using CodeXGLUE, which were then used to regenerate the corresponding Python code. 

4 

_V.-A. Moldovan et al._ 

_The Journal of Systems & Software 241 (2026) 113009_ 



**Fig. 1.** Pipeline of the proposed study. 

_Back-Translation from Java._ To implement back-translation through an intermediate programming language, we selected Java due to the availability of strong, well-trained models for Java code. Since the original code is written in Python, the use of Java as an intermediary offers a structurally different yet widely used programming language, enabling meaningful transformations while preserving the program’s logic. This choice also allows us to take advantage of reliable translation models trained on large Java–Python datasets, supporting highquality conversions in both directions. As a model, we used 4 different models: Google’s Gemini model (Siam et al., 2024), OpenAI’s GPT-4o model (Hou and Ji, 2025), DeepSeek-chat model (DeepSeek-AI et al., 2024), and OpenAI’s GPT-5-Nano model (OpenAI, 2025), as all 4 models represent generative AI systems capable of handling complex code translation tasks while maintaining syntactic correctness and semantic equivalence. The translation process was implemented, separately, using the Gemini-Pro model (gemini-2.5-pro-exp-03-25), the GPT-4o model (gpt-4o-2024-08-06), the DeepSeek-chat model (DeepSeek-V3.2Exp) and the GPT-5-Nano model (gpt-5-nano-2025-08-07). All these models were configured to process Python-to-Java and Java-to-Python transformations. Given that API-based model invocations are subject to rate limits, safety filters, and response time constraints, we incorporated mechanisms to handle API failures, retries, and response validation. To perform back-translation, refactored Python snippets were translated into Java using the above mentioned models, then retranslated into Python to preserve the original logic. 

_Back-Translation from textual description._ As for the back-translation using textual descriptions, the procedure closely followed the approach described above for Java-based back-translation. The main difference is that, instead of converting the code into Java, the original Python code was first translated into a natural-language description, from which we then reconstructed the corresponding Python implementation. We used the same 4 models as for the previous data augmentation method presented (Gemini, GPT-4o, DeepSeek, GPT-5-Nano), as they have demonstrated strong performance in similar code understanding and generation tasks (Siam et al., 2024; Hou and Ji, 2025; Fernandes et al., 2025). To accomplish this, each refactored Python block was initially processed using a prompt that instructed the model to produce a clear and detailed English description, capturing the code’s functionality and intent. This description was then provided as input to a second model invocation, in which the model was tasked with reconstructing the original Python function based on the description. 

_Generating Python code from existing comments._ For this augmentation approach, we used the same 4 models as in the previous two methods, but applied them to generate Python code directly from the available textual comments. These models were selected due to their strong natural language understanding and code generation capabilities, which allow them to accurately interpret textual descriptions 

and produce Python code that is both syntactically correct and semantically meaningful. Furthermore, each model has been trained on large-scale datasets containing both natural language and programming languages, making them particularly well-suited for tasks that require bridging the gap between human-readable documentation and executable code. This ensures that the generated code preserves the intended behavior described in the comments while adhering to proper coding conventions. 

_Generating Python code from generated comments._ The final data augmentation method consisted of generating textual specifications from the refactored code snippets using CodeXGLUE (Lu et al., 2021), followed by producing Python code from these specifications using the same 4 models employed in the other augmentation approaches. This method mirrors the approach previously applied for generating code from existing comments. CodeXGLUE was selected because it provides a comprehensive suite of standardized benchmarks for code-related tasks, including code summarization, code completion, and code-to-text translation, which are crucial for creating meaningful textual specifications (Lu et al., 2021). By leveraging CodeXGLUE’s pre-trained models, we benefit from its effective understanding of code semantics, enhancing the quality and precision of the generated specifications. The subsequent use of the employed LLMs to translate these text specifications back into Python code takes advantage of their strong natural language understanding and capacity to produce code that is both syntactically correct and semantically accurate to the original logic. 

The reason for which we used all 4 models: Gemini, GPT-4o, DeepSeek and GPT-5-Nano, is because each model offers distinct advantages suited to different aspects of the translation and augmentation process and we wanted to ensure a fair and comprehensive comparison. 

GPT-4o, developed by OpenAI, excels at generating syntactically correct code from natural language, making it ideal for tasks like creating Python code from comments and specifications. Its ability to transform plain English into complex code structures provides flexibility for natural language-to-code tasks, as seen in our work. 

On the other hand, Gemini-Pro, developed by Google, excels at translating code between languages like Python and Java, making it ideal for back-translation tasks or language-specific transformations, ensuring high-quality, semantically accurate translations. 

When considering the DeepSeek model, it is particularly well-suited for translating code between programming languages due to its extensive training on large, multi-language code datasets. This enables it to preserve program logic and semantics while accurately capturing syntactic structures, ensuring high-quality, precise cross-language code translations. 

5 

_V.-A. Moldovan et al._ 

_The Journal of Systems & Software 241 (2026) 113009_ 



#### **Table 3** 

Dataset distribution using the DeepSeek model. 

|Refactoring type|Text|CommGen|CodeXGLUE|Java|
|---|---|---|---|---|
|Add Parameter|3531|1536|3693|3533|
|Rename method|2536|928|2435|2533|
|Remove parameter|1177|529|1210|1170|
|Change/Rename Param|806|325|765|807|
|Change return type|328|131|333|325|



#### **Table 4** 

Dataset distribution using the GPT-5-Nano model. 

|Refactoring type|Text|CommGen|CodeXGLUE|Java|
|---|---|---|---|---|
|Add Parameter|1779|1746|3647|1801|
|Rename method|1948|938|2400|1947|
|Remove parameter|1788|585|1199|1789|
|Change/Rename Param|1770|320|751|1772|
|Change return type|870|137|271|870|



**Fig. 2.** Initial dataset. 

**Table 1** 

### _3.4. Validation_ 

Dataset distribution using the Gemini model. 

|Refactoring type|Text|CommGen|CodeXGLUE|Java|
|---|---|---|---|---|
|Add Parameter|3213|1697|3695|2141|
|Rename method|2111|934|2400|1156|
|Remove parameter|912|511|1150|681|
|Change/Rename Param|568|368|747|417|
|Change return type|329|134|300|199|



#### **Table 2** 

Dataset distribution using the GPT-4o model. 

|Refactoring type|Text|CommGen|CodeXGLUE|Java|
|---|---|---|---|---|
|Add Parameter|1779|1746|3734|1779|
|Rename method|1948|938|2400|1948|
|Remove parameter|1790|585|1199|1790|
|Change/Rename Param|1774|320|751|1774|
|Change return type|876|137|271|876|



We also decided to include the GPT-5-Nano model among the employed ones due to its compact architecture, strong natural language and code understanding capabilities. GPT-5-Nano is particularly effective for generating Python code from textual descriptions and comments, as well as reconstructing code from specifications, while requiring fewer computational resources compared to larger models. 

The decision to use all 4 models was driven by their complementary strengths across the data augmentation techniques. By employing all 4 models, we were able to leverage their individual advantages to comprehensively augment our dataset across all considered augmentation strategies, ensuring both syntactic correctness and semantic consistency of the generated code. 

A statistic showing the initial distribution of the employed dataset is presented in Fig. 2, while the distribution obtained after generating the new refactoring instances using the described data augmentation techniques is presented in Tables 1, 2, 3, 4. 

It is important to note that not all refactoring instances were successfully translated, leading to situations in which the balanced datasets contained fewer examples than the initial one, for certain refactoring types, such as ‘Add Parameter’. Certain functions were flagged as unsafe by the models during the text-to-code translation process, and some translations were affected by internal errors, such as timeouts. However, these failures did not impact the objectives of our study. Our focus was on evaluating the effectiveness and characteristics of the data augmentation techniques themselves, rather than examining the specific causes of individual translation errors or the robustness of each model in handling edge cases. 

To ensure syntactic correctness of the generated code, we first applied validation using the **AST (Abstract Syntax Tree) package** . AST parses Python source code into a structured tree representation, enabling static analysis without execution. An advantage of AST is that it validates individual functions in isolation, allowing correctness checks even when dependencies such as external modules or class definitions are not included. While AST ensures structural correctness, it does not verify logical equivalence or behavior preservation. Consequently, syntactic validation should not be interpreted as evidence of semantic equivalence between the original and generated code. Overall, 90% of the generated code across all augmentation methods passed AST validation, confirming that most transformations remained syntactically correct. 

To further validate the augmented refactorings, we applied a second stage of evaluation using **GPT-4o** . In this stage, each generated version of a function was compared with its original counterpart. The validation followed two steps: first, determining whether the transformed refactoring preserved the original behavior, and second, checking whether the applied transformation matched the intended refactoring type, for example, parameter addition, method renaming, or extraction. GPT-4o was selected for this stage due to its strong performance in code understanding and reasoning tasks, and it was consistently used as the sole validator across all generated outputs. We acknowledge that relying on a single LLM-based validator may introduce model-family bias and circularity effects, especially when evaluating outputs generated by related models. Therefore, the automated semantic validation should be interpreted as an approximate assessment of behavioral plausibility rather than formal proof of semantic equivalence. 

As mentioned previously, each augmentation method generated 4 datasets corresponding to the 4 employed models. All resulting datasets were included in the validation stage. 

_Manual Validation._ To assess the reliability of the automated validation pipeline, we performed a manual validation on a small subset of the generated refactorings, by reviewing the code and determining whether it could be integrated into the corresponding codebase. It is important to note that the generated code was not executed; the validation was based solely on code review. Execution-based validation was not feasible at scale because many extracted functions depended on incomplete project context, unavailable runtime environments, or external dependencies. We randomly selected 160 instances: two instances of each refactoring type for every method and for each model, ensuring coverage of all employed methods, models, and refactoring types. We manually verified the same three properties: syntax correctness, functionality preservation and refactoring preservation. The manual validation results were then compared with the results produced by the automated validation pipeline. 

6 

_V.-A. Moldovan et al._ 

_The Journal of Systems & Software 241 (2026) 113009_ 

#### **Table 5** 

|Class distribution using G|emini.||||
|---|---|---|---|---|
|Refactoring type|Text|CommGen|CodeXGLUE|Java|
|Add Parameter|3596|3400|3501|3412|
|Change/Rename Param|2357|2051|1950|1978|
|Remove parameter|2041|1969|1970|1859|
|Rename method|3704|3006|2600|3003|
|Change return type|1096|1685|1690|1683|



#### **Table 6** 

Class distribution using GPT-4o. 

|Refactoring type|Text|CommGen|CodeXGLUE|Java|
|---|---|---|---|---|
|Add Parameter|3308|3208|2956|3316|
|Change/Rename Param|2195|2113|1951|2062|
|Remove parameter|2037|2013|1972|2034|
|Rename method|2680|2508|2404|2802|
|Change return type|1462|1512|1496|1565|



#### **Table 7** 

Class distribution using DeepSeek. 

|Refactoring type|Text|CommGen|CodeXGLUE|Java|
|---|---|---|---|---|
|Add Parameter|3566|3456|3559|3308|
|Change/Rename Param|2249|2159|2050|2049|
|Remove parameter|1976|1976|1969|1977|
|Rename method|3012|2513|2600|2712|
|Change return type|1664|1673|1685|1664|



#### **Table 8** 

Class distribution using GPT-5-Nano. 

|Refactoring type|Text|CommGen|CodeXGLUE|Java|
|---|---|---|---|---|
|Add Parameter|3388|2952|2960|3290|
|Change/Rename Param|1963|2949|2950|2963|
|Remove parameter|2747|2756|2769|2732|
|Rename method|2807|2793|2701|2877|
|Change return type|1308|1794|1696|1678|



**Table 9** 

### _3.5. Balancing data_ 

To mitigate the initial class imbalance, we selected oversampling as the balancing strategy, following a careful assessment of the refactoring datasets and the available techniques. Given that refactoring instances are typically scarce, undersampling was considered unsuitable because discarding data at this stage could result in the loss of critical information. Hybrid sampling methods were also excluded, as they combine oversampling and undersampling and may still cause the omission of valuable minority class instances. Furthermore, hybrid approaches often introduce additional complexity in data preprocessing and can create inconsistencies in the distribution of refactoring types, which may adversely affect model performance and generalization. Under these considerations, oversampling was prioritized to ensure adequate representation of minority classes while preserving the integrity of the dataset. 

First, the distribution of refactoring types was analyzed and the imbalance ratio (IR), defined as the ratio between the largest and smallest class sizes, was computed. In the original dataset, the imbalance ratio was IR = 10.87, indicating a significant disparity between classes. After applying the augmentation and balancing procedure, the imbalance ratio decreased to values between IR = 1.64 and IR = 3.28, resulting in a more balanced dataset while preserving the diversity of the samples. 

The balancing procedure began by adding data generated through the proposed augmentation techniques, continuing until either the class distribution was equalized or all available augmented instances had been utilized. In cases where the augmented data alone proved insufficient, additional balancing was performed by randomly duplicating instances from the minority class. To avoid excessive replication, each minority-class instance was duplicated at most once. This balancing process was applied independently for each of the employed data augmentation techniques: back-translation from Java, back-translation from text descriptions, code generation from comments present in the original code, and code generation from specifications derived using CodeXGLUE, for each of the employed LLMs (Gemini, GPT-4o, DeepSeek, GPT-5-Nano). Because the balancing process relied primarily on the availability of augmented data, rather than unrestricted replication, some refactoring types could not be expanded to fully match the initial majority classes. Consequently, the final distributions of the 4 resulting datasets are presented in Tables 5, 6, 7, and 8. 

Unlike general-purpose techniques such as SMOTE, which create synthetic samples through feature-space interpolation, our approach relies on semantically valid code transformations. This ensures that the generated samples preserve the syntactic correctness and behavioral properties of real refactoring instances while reducing class imbalance. 

Validation Results of back-to-back code <u>generation</u> methods. 

|Model|Method|Syntax|Spec|Refactor|
|---|---|---|---|---|
|DeepSeek|CodeXGLUE|99.75|30.27|55.51|
|DeepSeek|Comments|99.74|28.41|13.63|
|DeepSeek|Java|99.18|95.06|42.74|
|DeepSeek|Text|99.68|95.74|21.14|
|Gemini|CodeXGLUE|99.76|29.99|60.57|
|Gemini|Comments|99.74|37.36|64.62|
|Gemini|Java|96.27|59.11|63.29|
|Gemini|Text|99.42|32.53|57.71|
|GPT-4o|CodeXGLUE|99.77|27.80|66.04|
|GPT-4o|Comments|99.73|63.80|71.36|
|GPT-4o|Java|99.56|73.10|59.02|
|GPT-4o|Text|99.69|77.92|63.35|
|GPT-5-Nano|CodeXGLUE|99.84|33.47|73.60|
|GPT-5-Nano|Comments|99.30|72.38|79.72|
|GPT-5-Nano|Java|99.81|75.32|62.64|
|GPT-5-Nano|Text|99.91|77.17|64.96|



### **4. Analysis and results** 

In the following, we present the results of validating the newly augmented data, assessing the similarity between the generated samples and the original ones, and using the augmented data in refactoring detection experiments. 

### _4.1. Validation results_ 

The validation results provided in Table 9 refer to the quality of the generated samples, presenting the percentages of correctly generated samples in terms of syntax, functionality preservation (the ‘‘Spec’’ column), and refactoring preservation (the ‘‘Refactor’’ column). Back Translation from Text using DeepSeek achieved the highest semantic preservation score with 95.74%, followed by Back Translation from Java using DeepSeek with 95.06%. For syntactic correctness, Back Translation from Text using GPT-5-Nano achieved 99.91%, followed by CodeXGLUE using GPT-5-Nano with 99.84%. In terms of correct refactoring classification, generating code from existing comments using GPT-5-Nano produced the best results with 79.72%, followed by CodeXGLUE with GPT-5-Nano at 73.60% and Comments using GPT-4o at 71.36%. These results suggest that text-based transformations tend to retain higher semantic similarity according to the employed validation criteria, while comment-driven generation methods are more effective at producing code that aligns with the intended refactoring type. 

The results obtained after performing manual validation are presented in Tables 10, 11 and 12. 

The results indicate that syntax validation is highly reliable, with almost perfect agreement between manual and automated validation, 

7 

_V.-A. Moldovan et al._ 

_The Journal of Systems & Software 241 (2026) 113009_ 

#### **Table 10** 

Manual validation results of back-to-back code <u>generation</u> methods. 

|Validation criteria|Accuracy<br>F1|Cohen’s k|
|---|---|---|
|Syntax|0.993<br>0.996|0.81|
|Functionality|0.593<br>0.575|0.28|
|Refactoring<br>**Table** **11**<br>F1-Score values of manual|0.750<br>0.833<br> validation by model.|0.41|
|Model|Syntax<br>Spec|Refactor|
|DeepSeek|98.70<br>65.00|80.70|
|Gemini|100<br>56.00|81.96|
|GPT-4o|100<br>48.64|81.96|
|GPT-5-Nano|100<br>58.82|88.52|



#### **Table 12** 

**Table 13** 

Original code similarity statistics: Mean and Standard deviation. 

|Model|Method|Mean|Std Dev|
|---|---|---|---|
|DeepSeek|CodeXGLUE|0.7280|0.1200|
|DeepSeek|Comments|0.5903|0.1874|
|DeepSeek|Java|0.7268|0.1514|
|DeepSeek|Text|0.7447|0.1486|
|Gemini|CodeXGLUE|0.6944|0.1325|
|Gemini|Comments|0.7152|0.1163|
|Gemini|Java|0.7548|0.1455|
|Gemini|Text|0.8180|0.1445|
|GPT-4o|CodeXGLUE|0.7161|0.1267|
|GPT-4o|Comments|0.7069|0.1219|
|GPT-4o|Java|0.7960|0.1393|
|GPT-4o|Text|0.8139|0.1430|
|GPT-5-Nano|CodeXGLUE|0.6868|0.1349|
|GPT-5-Nano|Comments|0.7084|0.1054|
|GPT-5-Nano|Java|0.7572|0.1481|
|GPT-5-Nano|Text|0.8083|0.1509|



F1-Score values of manual validation by method. 

|Model|Syntax|Spec|Refactor|
|---|---|---|---|
|CodeXGLUE|100|14.28|80.64|
|Comments|100|22.22|87.50|
|Java|100|80.76|75.47|
|Text|100|70.58|88.52|



suggesting that the automated pipeline is effective at detecting syntactic correctness. 

However, the agreement decreases substantially for functionality preservation. The automated validation achieves an accuracy of 59%, with a low Cohen’s k (0.28), indicating only fair agreement with manual validation. This result highlights the difficulty of reliably assessing semantic equivalence in automatically generated refactorings. The relatively low agreement between automated and manual validation suggests that functionality preservation remains challenging to establish conclusively using static inspection and LLM-based reasoning alone. 

For refactoring preservation, the agreement is higher than for functionality, with 75% accuracy and F1 of 83%, and the k value (0.41) indicating moderate agreement. This suggests that the automated validation appears reasonably effective at identifying the intended refactoring transformation, although some inconsistencies remain. 

### _4.2. Similarities assessment_ 

Through this analysis we intend to provide answer to RQ1. To ensure that the augmented code samples remain semantically aligned with the original refactored functions, we evaluated similarity at both the pre-refactoring and post-refactoring stages. The goal of this process is to determine whether the newly generated samples preserve the behavior and structural intent of the corresponding original functions, rather than simply being syntactically valid. 

Our approach relies on embedding-based similarity rather than surface-level text comparison, since refactored code often introduces structural or naming variations that would make syntactic similarity metrics unreliable. For each refactoring instance, both the original and augmented functions (before and after refactoring) were converted into dense vector representations using OpenAI’s text-embedding-3small model, an improved version of the ADA embedding family with enhanced performance on code-related inputs. Using this model enables capturing semantic patterns such as API usage, control flow, and logical structure beyond lexical similarity. 

We computed similarity scores in two phases. First, we compared each original pre-refactor function to its generated pre-refactor counterpart. Second, we applied the same methodology for the post-refactor functions. Similarity between embeddings was computed using cosine distance, which measures directional closeness in a high-dimensional 

vector space. A higher cosine similarity value indicates that the generated function closely follows the semantics of the original version, even if syntactic differences exist due to transformations such as renaming, restructuring, or comment insertion. 

The statistical results presented in Table 13 provide an overview of how closely the augmented pre-refactoring functions match their original counterparts across different models and augmentation strategies. Overall, the mean similarity values indicate that most methods preserve semantic intent reasonably well, with averages generally between 0.68 and 0.82. Text-based back-translation consistently achieves the highest scores, with values such as 0.8180 (Gemini) and 0.8139 (GPT-4o), suggesting that transforming code into natural language before regeneration captures functional behavior more reliably. Javabased back-translation also performs strongly, particularly for GPT-4o (0.7960), demonstrating that using a structurally rich intermediary language can effectively retain semantics. In contrast, comment-based generation exhibits lower similarity (e.g., 0.5903 for DeepSeek), which aligns with the expectation that comments alone may lack sufficient detail to accurately reconstruct full method behavior. 

To complement these aggregate metrics, Table 14 reports distribution-level statistics, including minimum, median, and maximum similarities. The median values reinforce prior observations, with text-based approaches again achieving the highest central tendency (e.g., 0.8438 for Gemini and 0.8361 for GPT-4o), indicating that not only are mean values high, but the majority of samples cluster near high-similarity regions. Comment-based methods maintain lower medians (e.g., 0.6301 for DeepSeek), confirming greater variability and weaker semantic retention. The minimum values also provide insight into failure cases: some methods yield low or slightly negative similarities (e.g., −0.0460 for DeepSeek and −0.0357 for GPT-4o under text-based generation), indicating that a small subset of generated samples diverges substantially from the original logic. Despite this, maximum scores approach or equal 1.0 across all configurations, showing that under favorable conditions, augmentation can produce semantically equivalent functions. 

The similarity results for the refactored versions of the functions are summarized in Table 15. Compared to the original (pre-refactor) analysis, the mean similarity values exhibit a slightly different pattern. Text-based augmentation continues to perform well, particularly for GPT-4o (0.8121) and GPT-5-Nano (0.8054), indicating that naturallanguage intermediates preserve the semantics of the refactored code similarly to the original version. However, unlike the pre-refactoring case, comment-based generation produces competitive results for several models, such as DeepSeek (0.7214) and GPT-4o (0.7272), suggesting that comments may capture refactoring intent more clearly after structural transformations are applied. Java-based back-translation achieves strong performance with the models GPT-4o (0.7984) and 

8 

_V.-A. Moldovan et al._ 

_The Journal of Systems & Software 241 (2026) 113009_ 

**Table 14** 

Original code similarity distribution: Min, Median (P50), and Max. 

|Model|Method|Min|P50|Max|
|---|---|---|---|---|
|DeepSeek|CodeXGLUE|0.2968|0.7351|1.0000|
|DeepSeek|Comments|−0.0460|0.6301|0.9455|
|DeepSeek|Java|0.1548|0.7414|0.9897|
|DeepSeek|Text|0.2145|0.7620|0.9886|
|Gemini|CodeXGLUE|0.1890|0.7004|0.9999|
|Gemini|Comments|0.2952|0.7234|0.9868|
|Gemini|Java|0.0305|0.7663|0.9990|
|Gemini|Text|0.0441|0.8438|1.0000|
|GPT-4o|CodeXGLUE|0.2305|0.7241|1.0000|
|GPT-4o|Comments|0.2257|0.7135|0.9868|
|GPT-4o|Java|0.2277|0.8244|1.0000|
|GPT-4o|Text|−0.0357|0.8361|1.0000|
|GPT-5-Nano|CodeXGLUE|0.1739|0.6921|1.0000|
|GPT-5-Nano|Comments|0.2698|0.7177|0.9672|
|GPT-5-Nano|Java|0.0765|0.7691|1.0000|
|GPT-5-Nano|Text|0.0324|0.8261|1.0000|



**Table 16** 

Refactored code similarity distribution: Min, Median (P50), and Max. 

|Model|Method|Min|P50|Max|
|---|---|---|---|---|
|DeepSeek|CodeXGLUE|0.2432|0.7181|1.0000|
|DeepSeek|Comments|0.2580|0.7414|0.9707|
|DeepSeek|Java|0.0485|0.5179|0.8968|
|DeepSeek|Text|0.0215|0.5992|0.9562|
|Gemini|CodeXGLUE|0.2433|0.7184|1.0000|
|Gemini|Comments|0.2433|0.6857|0.9774|
|Gemini|Java|0.0789|0.6441|1.0000|
|Gemini|Text|0.2047|0.7164|1.0000|
|GPT-4o|CodeXGLUE|0.2206|0.7218|1.0000|
|GPT-4o|Comments|0.2957|0.7380|0.9905|
|GPT-4o|Java|0.2636|0.8246|1.0000|
|GPT-4o|Text|0.3575|0.8297|1.0000|
|GPT-5-Nano|CodeXGLUE|0.1911|0.6854|0.9982|
|GPT-5-Nano|Comments|0.2497|0.7180|0.9627|
|GPT-5-Nano|Java|0.1277|0.7717|1.0000|
|GPT-5-Nano|Text|0.1974|0.8216|1.0000|



#### **Table 15** 

Refactored code similarity statistics: Mean and Standard deviation. 

|Model|Method|Mean|Std Dev|
|---|---|---|---|
|DeepSeek|CodeXGLUE|0.7102|0.1273|
|DeepSeek|Comments|0.7214|0.1281|
|DeepSeek|Java|0.5157|0.1331|
|DeepSeek|Text|0.5940|0.1263|
|Gemini|CodeXGLUE|0.7110|0.1258|
|Gemini|Comments|0.6829|0.1185|
|Gemini|Java|0.6347|0.1610|
|Gemini|Text|0.7077|0.1284|
|GPT-4o|CodeXGLUE|0.7135|0.1267|
|GPT-4o|Comments|0.7272|0.1187|
|GPT-4o|Java|0.7984|0.1374|
|GPT-4o|Text|0.8121|0.1385|
|GPT-5-Nano|CodeXGLUE|0.6828|0.1314|
|GPT-5-Nano|Comments|0.7074|0.1037|
|GPT-5-Nano|Java|0.7569|0.1461|
|GPT-5-Nano|Text|0.8054|0.1486|



GPT-5-Nano (0.7569), though results drop significantly with DeepSeek (0.5157), indicating that preservation quality for cross-language transformations depends heavily on the underlying model. 

The distribution metrics provided in Table 16 further support these observations. Text-based transformations maintain high median similarity values across all models (e.g., 0.8297 for GPT-4o and 0.8216 for GPT-5-Nano), while Java-based augmentation also achieves high medians for stronger models (e.g., 0.8246 with GPT-4o). Commentbased methods exhibit moderate variance, with medians ranging from 0.6857 (Gemini) to 0.7414 (DeepSeek), reinforcing that comments can capture behavioral intent effectively post-refactoring but are sensitive to linguistic ambiguity. As with the original code, minimum similarity values reveal occasional degradation (e.g., 0.0215 for DeepSeek under text-based generation), though maximum similarity remains near 1.0 for all configurations, demonstrating that some generated samples are near-identical in semantics to their refactored originals. 

Overall, post-refactoring results show higher stability across methods compared to the pre-refactoring stage. This suggests that once refactoring transformations introduce clearer structure, augmentation models more reliably reconstruct equivalent behavior, particularly when leveraging textual abstraction or well-trained cross-language mapping. 

**Conclusion to RQ1:** Overall, the results indicate that the augmented code preserves a substantial degree of semantic similarity with the original refactoring instances. Among the evaluated methods, textbased and Java-based back-translation achieved the strongest and most consistent similarity scores, showing that LLM-based augmentation can generate diverse yet semantically aligned refactoring samples suitable for further analysis and learning tasks. 

### _4.3. Use of augmented data in refactoring detection_ 

To evaluate the effectiveness of the proposed data augmentation techniques and, thus, to answer RQ2, we conducted experiments, targeting the detection of software refactoring instances. We compared model performance across datasets generated using our augmentation methods, the original baseline dataset, and the baseline dataset enhanced with SMOTE for class balancing. The dataset was partitioned into 80% for training and 20% for testing, ensuring that training and testing samples were disjoint to enable a proper assessment of model performance and to prevent overfitting. 

The detection process relied on a variety of software quality metrics, including complexity, LOC, LLOC, SLOC, comment counts, multi-line and blank lines, maintainability index, as well as Halstead metrics (H1, H2, N1, N2, vocabulary, length, calculated length, volume, difficulty, effort, time, and estimated number of bugs), all extracted using the Radon tool (Rubik, 2024). In addition, we computed Average Cyclomatic Complexity, Weighted Methods per Class, Response for a Class, and Depth of Inheritance Tree metrics using the Understand tool (Scientific Toolworks, 2024). 

For our experiments, we selected the following classifiers: Random Forests (Parmar et al., 2019), XGBoost (Chen and Guestrin, 2016), Naive Bayes (Maron, 1961), and Support Vector Machines (SVM) (Suthaharan, 2016). These models were chosen due to their suitability for structured data and their widespread use in software quality and classification tasks. Employing multiple classifiers allows for a more comprehensive evaluation of the effectiveness of the data augmentation techniques, as relying on a single model could introduce bias. This approach provides a more robust assessment of the extent to which the augmented data enhances the detection of software refactorings across different classification methods. 

To enable a clear comparison of the applied data augmentation techniques, we evaluated the models on both the baseline dataset and the baseline dataset enhanced with SMOTE for class balancing. The performance results for the baseline and SMOTE-augmented datasets are presented in Table 17. Meanwhile, the outcomes for the datasets augmented using the proposed data augmentation techniques are reported in Tables 18, 19, 20, and 21. 

After analyzing the obtained results, we can conclude that all proposed data augmentation techniques outperform both the baseline and the SMOTE scenarios across all evaluated LLM-generated datasets (Gemini, GPT-4o, DeepSeek, and GPT-5-Nano), with substantial improvements in accuracy and F1-Score. The highest overall gains are observed with Random Forest, where the F1-Score rises by up to approximately 22% (from 0.61 to 0.83), while XGBoost also demonstrates strong improvements (up to 20%). SVM shows moderate gains (up to 17%), while Naive Bayes exhibits the most variable performance across 

9 

_V.-A. Moldovan et al._ 

_The Journal of Systems & Software 241 (2026) 113009_ 

#### **Table 17** 

Model <u>performance</u> without our data augmentation. 

|Data source|Model|Accuracy|Precision|Recall|F1 Score|
|---|---|---|---|---|---|
|Original|Random Forest|0.61|0.61|0.61|0.61|
|Original|XGBoost|0.59|0.60|0.59|0.59|
|Original|Naive Bayes|0.58|0.62|0.60|0.60|
|Original|SVM|0.58|0.59|0.59|0.59|
|SMOTE|Random Forest|0.61|0.61|0.61|0.61|
|SMOTE|XGBoost|0.58|0.58|0.58|0.58|
|SMOTE|Naive Bayes|0.62|0.62|0.62|0.62|
|SMOTE|SVM|0.57|0.58|0.57|0.57|



#### **Table 18** 

Model <u>performance</u> with our data augmentation — Gemini. 

|Data source|Model|Accuracy|Precision|Recall|F1 Score|
|---|---|---|---|---|---|
|CodeXGLUE|Random Forest|0.78|0.73|0.75|0.73|
|CodeXGLUE|XGBoost|0.71|0.72|0.69|0.7|
|CodeXGLUE|Naive Bayes|0.72|0.71|0.75|0.72|
|CodeXGLUE|SVM|0.73|0.69|0.72|0.7|
|Comments|Random Forest|0.79|0.78|0.78|0.78|
|Comments|XGBoost|0.68|0.69|0.67|0.67|
|Comments|Naive Bayes|0.72|0.69|0.73|0.7|
|Comments|SVM|0.73|0.7|0.7|0.7|
|Java|Random Forest|0.8|0.79|0.8|0.79|
|Java|XGBoost|0.7|0.71|0.7|0.68|
|Java|Naive Bayes|0.71|0.77|0.71|0.73|
|Java|SVM|0.78|0.76|0.76|0.76|
|Text|Random Forest|0.81|0.81|0.81|0.81|
|Text|XGBoost|0.71|0.72|0.71|0.69|
|Text|Naive Bayes|0.64|0.74|0.67|0.68|
|Text|SVM|0.75|0.75|0.75|0.75|



**Table 21** 

Model <u>performance</u> with our data augmentation - GPT-5-Nano. 

|Data source|Model|Accuracy|Precision|Recall|F1 Score|
|---|---|---|---|---|---|
|CodeXGLUE|Random Forest|0.72|0.79|0.68|0.72|
|CodeXGLUE|XGBoost|0.75|0.78|0.72|0.74|
|CodeXGLUE|Naive Bayes|0.75|0.73|0.73|0.73|
|CodeXGLUE|SVM|0.74|0.7|0.74|0.71|
|Comments|Random Forest|0.72|0.71|0.77|0.72|
|Comments|XGBoost|0.74|0.73|0.76|0.73|
|Comments|Naive Bayes|0.71|0.69|0.74|0.7|
|Comments|SVM|0.73|0.71|0.76|0.72|
|Java|Random Forest|0.8|0.87|0.81|0.83|
|Java|XGBoost|0.79|0.85|0.74|0.77|
|Java|Naive Bayes|0.7|0.72|0.73|0.72|
|Java|SVM|0.76|0.8|0.75|0.76|
|Text|Random Forest|0.76|0.83|0.77|0.78|
|Text|XGBoost|0.8|0.85|0.77|0.79|
|Text|Naive Bayes|0.7|0.74|0.7|0.71|
|Text|SVM|0.78|0.81|0.75|0.76|



augmentation methods. These findings indicate that augmenting the data directly at the code level provides more meaningful variability than feature-level oversampling alone. 

**Conclusion to RQ2:** Overall, code-level data augmentation consistently outperformed both the baseline and SMOTE across all LLMgenerated datasets, with the largest gains observed for Random Forest and XGBoost, suggesting that code-level augmentation introduced more meaningful variability than feature-level oversampling. 

### **5. Discussion** 

#### **Table 19** 

Model <u>performance</u> with our data augmentation - GPT-4o. 

|Data source|Model|Accuracy|Precision|Recall|F1 Score|
|---|---|---|---|---|---|
|CodeXGLUE|Random Forest|0.82|0.82|0.82|0.82|
|CodeXGLUE|XGBoost|0.72|0.72|0.72|0.72|
|CodeXGLUE|Naive Bayes|0.71|0.82|0.71|0.75|
|CodeXGLUE|SVM|0.77|0.75|0.77|0.75|
|Comments|Random Forest|0.78|0.81|0.73|0.75|
|Comments|XGBoost|0.73|0.77|0.65|0.68|
|Comments|Naive Bayes|0.75|0.88|0.75|0.79|
|Comments|SVM|0.78|0.75|0.77|0.75|
|Java|Random Forest|0.82|0.82|0.83|0.82|
|Java|XGBoost|0.76|0.79|0.78|0.77|
|Java|Naive Bayes|0.71|0.72|0.72|0.72|
|Java|SVM|0.77|0.76|0.77|0.76|
|Text|Random Forest|0.8|0.81|0.81|0.8|
|Text|XGBoost|0.76|0.82|0.76|0.77|
|Text|Naive Bayes|0.72|0.77|0.73|0.74|
|Text|SVM|0.77|0.8|0.73|0.75|



#### **Table 20** 

Model <u>performance</u> with our data augmentation — DeepSeek. 

|Data source|Model|Accuracy|Precision|Recall|F1 Score|
|---|---|---|---|---|---|
|CodeXGLUE|Random Forest|0.77|0.78|0.73|0.74|
|CodeXGLUE|XGBoost|0.73|0.72|0.72|0.71|
|CodeXGLUE|Naive Bayes|0.74|0.72|0.76|0.73|
|CodeXGLUE|SVM|0.74|0.7|0.71|0.7|
|Comments|Random Forest|0.75|0.79|0.71|0.73|
|Comments|XGBoost|0.72|0.73|0.71|0.71|
|Comments|Naive Bayes|0.73|0.75|0.75|0.74|
|Comments|SVM|0.72|0.75|0.7|0.71|
|Java|Random Forest|0.7|0.74|0.73|0.72|
|Java|XGBoost|0.73|0.74|0.73|0.72|
|Java|Naive Bayes|0.67|0.71|0.69|0.69|
|Java|SVM|0.72|0.73|0.72|0.72|
|Text|Random Forest|0.72|0.75|0.74|0.74|
|Text|XGBoost|0.72|0.74|0.73|0.73|
|Text|Naive Bayes|0.68|0.71|0.69|0.69|
|Text|SVM|0.72|0.74|0.72|0.72|



After examining the results obtained from the comparison between automatically validated data and manually validated data, we have observed that the reliability of automated validation varied across augmentation methods. For example, functionality validation F1-Score ranged from 0.22 for the Comments augmentation to 0.80 for the Java augmentation, suggesting that some augmentation strategies produce refactorings that are harder to validate automatically. In contrast, syntax validation remained consistently high across all strategies, achieving near-perfect agreement. Refactoring preservation showed intermediate performance, with F1 scores between 0.75 and 0.88, indicating that the automated validation pipeline is reasonably effective at identifying the intended refactoring. 

Regarding the models used in the data augmentation process, all models exhibited near-perfect agreement for syntax validation. However, functionality preservation varied substantially across models: automated validation achieved 0.65 F1-Score for DeepSeek, 0.49 for GPT-4o, 0.59 for GPT-5-Nano, and 0.56 for Gemini. These results suggest that both the correctness of generated refactorings and the ability of automated validation to detect semantic issues differ across models. In contrast, refactoring preservation was more consistent, with F1 scores ranging from 0.80 to 0.89. 

While the generated refactorings generally exhibited high syntactic correctness and strong embedding similarity, the semantic preservation results should be interpreted cautiously. The lower agreement scores observed for functionality preservation highlight the difficulty of reliably assessing behavioral equivalence in LLM-generated code transformations, particularly when validation relies on static inspection and LLM-based reasoning. Consequently, the generated instances are better viewed as semantically plausible approximations rather than guaranteed functionally equivalent refactorings. 

From the results presented in the previous section, it can be seen that the method involving code translation through Java and textbased back-translation emerged as the most effective augmentation strategy, performing nearly identically overall (average F1 scores of 0.748 and 0.744, respectively), with both consistently achieving strong results across LLMs, particularly for datasets generated using GPT-4o 

10 

_V.-A. Moldovan et al._ 

_The Journal of Systems & Software 241 (2026) 113009_ 

and GPT-5-Nano. The technique based on CodeXGLUE specification generation also performs strongly and remains competitive across all models (average F1 of 0.730). The augmentation method relying on comment-based code generation yields the lowest performance among the proposed approaches (average F1 of 0.723). Nevertheless, even this method substantially outperforms both baseline and SMOTE conditions, suggesting that despite potential semantic variations, it still preserves meaningful refactoring-related structural patterns. 

The largest performance gap between the baseline (with or without SMOTE) and the augmented datasets is observed for Random Forest. In contrast, XGBoost also shows strong absolute gains but exhibits more consistent performance across different augmentation strategies. While both Random Forest and XGBoost are ensemble methods, they rely on different learning strategies. Random Forest uses bagging to train multiple independent trees, whereas XGBoost employs gradient boosting with sequential tree construction. The results suggest that the bagging-based structure of Random Forest benefits more from the additional training diversity introduced by the augmented data. 

Overall, while the magnitude of improvement varies across the LLMs used to generate the augmented samples, all 4 models, Gemini, GPT-4o, DeepSeek, and GPT-5-Nano, successfully enhance classifier performance. Among them, GPT-4o generally leads to the highestquality augmented datasets (average F1 of 0.76), followed by GPT5-Nano (0.74), while Gemini and DeepSeek provide consistent but slightly lower improvements (both at 0.72 average). 

In order to test the significance of the obtained results, we used the Friedman statistical test followed by the Nemenyi post-hoc test, using the F1-Score values. First, we applied the Friedman test to determine whether there were significant differences between the methods. After ranking the F1-Scores per row and computing the test statistic, we obtained a Friedman test statistic of 14.8529 and a _𝑝_ -value of 0.0110, indicating that at least one data augmentation technique had a statistically different effect, making the Nemenyi test appropriate. The Nemenyi post-hoc test for pairwise comparisons revealed important findings. 

Among the augmentation techniques themselves, differences were not statistically significant, as nearly all pairwise p-values exceeded 0.95, indicating highly similar performance across LLM-generated datasets. However, several augmentation methods demonstrated statistically significant improvements over both the Original baseline and SMOTE. Most notably, the Java-based augmentation using GPT-5-Nano achieved the strongest significance against SMOTE (p = 0.030) and Original (p = 0.037), while Java-based augmentation with GPT-4o also showed significant improvements (p = 0.042 vs. SMOTE, p = 0.052 vs. Original). Additional statistically significant results were observed for GPT-4o Text-based augmentation (p = 0.052 vs. SMOTE, p = 0.064 vs. Original) and GPT-4o CodeXGLUE (p = 0.071 vs. SMOTE, p = 0.086 vs. Original). These results confirm that LLM-based augmentation methods, particularly those involving Java translation, provide statistically significant performance gains over traditional approaches. Fig. 3 shows the complete pairwise p-values matrix. 

Challenges specific to refactoring can have an impact on the augmentation process. Python refactoring detection is sometimes more difficult than in other languages, such as Java, due to more relaxed constraints and no explicit type signatures. However, this manifest as an advantage during augmentation since relaxed conditions means more options to generate similar code. 

Another challenge refers to overlapping different refactoring types, such as Add Parameter and Change Parameter Name. Augmentation expands the code in various ways, thus allowing separation of overlapping refactoring. 

### **6. Implications for researchers and practitioners** 

The findings of this study suggest that source-code-level augmentation can significantly influence the construction and quality of datasets used in empirical investigations on refactoring. By generating semantically consistent program transformations rather than altering feature distributions, the proposed approach preserves structural and behavioral properties that are essential for learning-based software engineering analyses. This highlights the role of augmentation not only as a data expansion mechanism, but also as a methodological factor that may affect the validity and interpretability of experimental outcomes. 

For researchers, the results underline the importance of evaluating augmentation strategies through multiple complementary perspectives, including semantic preservation, validation accuracy, and their impact on refactoring detection performance. The observed variability across models and transformation methods indicates that augmentation quality cannot be taken for granted, but must be empirically assessed within the specific research context. This suggests that future studies employing generative techniques should explicitly report augmentation design choices and validation criteria as part of their experimental methodology. 

From a practical perspective, the study indicates that validated synthetic refactoring instances can support the development of tools that assist developers during everyday programming tasks. For example, they can be used to improve AI-based linters, refactoring recommendation plugins, or IDE extensions that detect refactoring opportunities and suggest cleaner code structures in projects where real historical examples are too limited or unevenly distributed. In this way, augmented data can help increase the robustness and coverage of such tools across multiple refactoring types. 

At the same time, applying such augmentation pipelines in practice involves LLM-related resource considerations. Since each strategy requires multiple model invocations, computational cost, API cost, latency, rate limits, and scalability may influence its feasibility in large-scale or interactive settings. More capable models may generate higher-quality samples, but they may also require more resources, while smaller models can provide a more cost-effective alternative with possible trade-offs in augmentation quality. The results also emphasize that the adoption of generative augmentation in practice requires careful validation and monitoring to ensure alignment with real development patterns and to mitigate the risk of introducing artificial or misleading signals. These trade-offs are particularly relevant for AIbased development tools, where response time, reliability, and resource consumption can directly affect practical usability. 

### **7. Threats to validity** 

Following the existing guidelines (ACM, 2021), we identified and addressed threats related to construct, internal and external validity of our study. 

_Construct_ validity refers to the extent to which the tools we used, in this case LLMs, accurately reflect the theoretical construct, namely the generated code. One concern comes from the fact that LLMs tend to write code with longer variable and function names and additional comments to improve clarity. They also incorporate more explicit error handling, operating with assumptions of less external validation. These characteristics contrast with human-written code, which is often more concise and relies more heavily on context. As a result, models may adopt AI-style coding conventions that prioritize clarity and safety over the practical, succinct patterns typically found in human programming. However, this does not affect the proposed data augmentation techniques, because they focus on semantically equivalent transformations rather than stylistic details. The augmented datasets preserve structural and functional relationships, ensuring that refactoring patterns, API usage, and control flow reflect the original code. Embedding-based similarity metrics and semantic evaluations further confirm that the 

11 

_V.-A. Moldovan et al._ 

_The Journal of Systems & Software 241 (2026) 113009_ 



**Fig. 3.** Nemenyi test results. 

generated code maintains the intended behavior, mitigating any bias from LLM-specific stylistic variations. 

_Internal_ validity considers factors that can impact the obtained results. In our study, such threats might come during the augmentation process due to nondeterministic outputs of the considered LLMs, producing distinct results for same prompts. Further threats may arise from the automated detection and extraction of refactoring instances. The use of rule-based refactoring mining may introduce labeling inaccuracies, such as false positives, missed refactorings, or imprecise classification of complex edits. In addition, reconstructing affected methods through commit-level analysis and regex-based extraction may lead to minor inconsistencies in the representation of pre- and postrefactoring code fragments, which can propagate into the augmentation pipeline and influence the quality of generated samples. We tried to mitigate these threats through AST validation, GPT-4o-powered semantic checks and manual validation of a randomly selected subset of our dataset but some risks related to erroneous classification might remain. By applying each of the 4 data augmentation methods with all 4 LLMs, we aimed to mitigate the effects of the inherent non-deterministic behavior of any single model. 

_External_ validity refers to the extent of generalizing the findings of the study. We have considered open source Python projects, which possess certain characteristics, so we formulate our findings in terms of observations of this type of source code, rather than as generalized conclusions. 

The experiments considered a metric-base approach. We acknowledge that this might not hold for other refactoring detection approaches such as code learning or rule-based methods. 

### **8. Conclusions and future work** 

We investigated dataset augmentation processes for SE research, evaluating 16 augmentation configurations (4 techniques, each implemented using 4 different LLMs). Our findings highlight the importance of selecting an appropriate augmentation strategy. They also emphasize the need for a structured workflow that includes dataset validation and class balancing. 

To better understand the effects of augmentation, we examined code embeddings of the refactoring instances before and after augmentation, measuring the similarity between original and synthetic samples. This analysis helped assess the degree of structural and semantic similarity between generated code and real refactoring instances. 

Through extensive experimentation, we show that LLM-generated data can significantly improve model generalization, producing more stable and reliable refactoring-effort predictions. A key strength of our approach is its focus on code-based augmentation, rather than feature-level augmentation, which operates directly on source code. This operates directly on source code and aims to retain structural characteristics and meaningful relationships between code elements, ultimately yielding models that are more robust to previously unseen refactoring cases. 

12 

_V.-A. Moldovan et al._ 

_The Journal of Systems & Software 241 (2026) 113009_ 

Future research can build on the proposed augmentation framework by investigating predictive models for identifying potential functionlevel refactoring opportunities. Such models could leverage the augmented datasets to learn from both structural signals, such as AST patterns or control-flow complexity, and semantic cues captured in code embeddings. Another promising direction is the investigation of augmentation strategies for higher-level refactorings, including class-level and design-level transformations. These refactorings require modeling richer program context, such as inter-class dependencies, inheritance structures, and broader architectural relationships, which makes them substantially more challenging to detect, predict, and reliably augment. Addressing these challenges will help advance automated refactoring research and improve the applicability of generative augmentation techniques in complex software systems. 

### **CRediT authorship contribution statement** 

**Vasilica-Andreea Moldovan:** Writing – review & editing, Writing – original draft, Visualization, Software, Methodology, Investigation, Data curation, Conceptualization. **Rareş Pătcaş:** Writing – review & editing, Writing – original draft, Visualization, Validation, Software, Methodology, Investigation, Conceptualization. **Simona Motogna:** Writing – review & editing, Writing – original draft, Supervision, Methodology, Conceptualization. 

### **Declaration of competing interest** 

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper. 

### **Acknowledgment** 

This research was partially supported by the project ‘‘Romanian Hub for Artificial Intelligence - HRIA’’, Smart Growth, Digitization and Financial Instruments Program, 2021–2027, MySMIS no. 351416. 

### **Data availability** 

I have shared the link to our replication package in the Data Availability section (https://figshare.com/s/5df5df00f39388dd35e6). 

### **References** 

- Ralph, P. (Ed.), 2021. ACM sigsoft empirical standards for software engineering research, version 0.2.0. URL https://github.com/acmsigsoft/EmpiricalStandards. 

- Ahmad, W.U., Chakraborty, S., Ray, B., Chang, K.-W., 2023. Summarize and generate to back-translate: Unsupervised translation of programming languages. In: Vlachos, A., Augenstein, I. (Eds.), Proceedings of the 17th Conference of the European Chapter of the Association for Computational Linguistics. Association for Computational Linguistics, pp. 1528–1542. http://dx.doi.org/10.18653/v1/2023.eacl-main.112. 

- Alkharabsheh, K., Alawadi, S., Kebande, V.R., Crespo, Y., Fernandez-Delgado, M., Taboada, J.A., 2022. A comparison of machine learning algorithms on design smell detection using balanced and imbalanced dataset: A study of God class. Inf. Softw. Technol. 143, 106736. http://dx.doi.org/10.1016/j.infsof.2021.106736. 

- Alon, U., Zilberstein, M., Levy, O., Yahav, E., 2019. Code2vec: Learning distributed representations of code. Proc. ACM Program. Lang. 3 (POPL), 1–29. 

- Atwi, H., Lin, B., Tsantalis, N., Kashiwa, Y., Kamei, Y., Ubayashi, N., Bavota, G., Lanza, M., 2021. PYREF: Refactoring detection in python projects. In: 2021 IEEE 21st International Working Conference on Source Code Analysis and Manipulation. SCAM, pp. 136–141. http://dx.doi.org/10.1109/SCAM52516.2021.00025. 

- Chen, T., Guestrin, C., 2016. XGBoost: A scalable tree boosting system. Proc. ACM SIGKDD Int. Conf. Knowl. Discov. Data Min. 10 (4), 785–794. http://dx.doi.org/ 10.1145/2939672.2939785. 

- Chen, P., Lampouras, G., 2023. Exploring data augmentation for code generation tasks. In: Vlachos, A., Augenstein, I. (Eds.), Findings of the Association for Computational Linguistics: EACL 2023. Association for Computational Linguistics, pp. 1542–1550. http://dx.doi.org/10.18653/v1/2023.findings-eacl.114. 

- DeepSeek-AI, Liu, A., Feng, B., Xue, B., Wang, B., Wu, B., Lu, C., Zhao, C., Deng, C., Zhang, C., Ruan, C., Dai, D., Guo, D., Yang, D., Chen, D., Ji, D., Li, E., Lin, F., Dai, F., Luo, F., Hao, G., Chen, G., et al., 2024. DeepSeek-V3 technical report. ArXiv Preprint, arXiv:2412.19437, URL https://arxiv.org/abs/2412.19437. 

- Dong, Z., Hu, Q., Guo, Y., Zhang, Z., Zhao, J., 2023. Boosting source code learning with text-oriented data augmentation: An empirical study. In: 2023 IEEE 23rd International Conference on Software Quality, Reliability, and Security Companion. QRS-C, pp. 383–392. 

- Dou, S., Wu, Y., Jia, H., Zhou, Y., Liu, Y., Liu, Y., 2024. Cc2vec: Combining typed tokens with contrastive learning for effective code clone detection. Proc. ACM Softw. Eng. 1 (FSE), 1564–1584. 

- Edward, E., Nyamawe, A.S., Elisa, N., 2024. On the impact of refactorings on software attack surface. IEEE Access 12, 128570–128584. 

- Feng, S., Keung, J., Yu, X., Xiao, Y., Zhang, M., 2021. Investigation on the stability of SMOTE-based oversampling techniques in software defect prediction. Inf. Softw. Technol. 139, 106662. http://dx.doi.org/10.1016/j.infsof.2021.106662. 

- Fernandes, D., Matos-Carvalho, J.P., Fernandes, C.M., Fachada, N., 2025. DeepSeek-v3, GPT-4, phi-4, and LLaMA-3.3 generate correct code for LoRaWAN-related engineering tasks. Electronics 14 (7), http://dx.doi.org/10.3390/electronics14071428. 

- Fernandez, A., Garcia, S., Herrera, F., Chawla, N.V., 2018. SMOTE for learning from imbalanced data: Progress and challenges, marking the 15-year anniversary. J. Artificial Intelligence Res. 61, 863–905. http://dx.doi.org/10.1613/jair.1.11192. 

- Fowler, M., 1999. Refactoring: Improving the Design of Existing Code. Addison-Wesley, Boston, MA, USA. 

- Guo, D., Ren, S., Lu, S., Feng, Z., Tang, D., Liu, S., Zhou, L., Duan, N., Svyatkovskiy, A., Fu, S., Tufano, M., Deng, S.K., Clement, C., Drain, D., Sundaresan, N., Yin, J., Jiang, D., Zhou, M., 2021. GraphCodeBERT: Pre-training code representations with data flow. arXiv:2009.08366, URL https://arxiv.org/abs/2009.08366. 

- Hou, W., Ji, Z., 2025. Comparing large language models and human programmers for generating programming code. Adv. Sci. 12 (8), 2412279. 

- Jadhav, A., M. Mostafa, S., Elmannai, H., Karim, F.K., 2022. An empirical assessment of performance of data balancing techniques in classification task. Appl. Sci. 12 (8), http://dx.doi.org/10.3390/app12083928, URL https://www.mdpi.com/20763417/12/8/3928. 

- Leevy, J.L., Khoshgoftaar, T.M., Bauder, R.A., Seliya, N., 2018. A survey on addressing high-class imbalance in big data. J. Big Data 5 (1), 42. http://dx.doi.org/10.1186/ s40537-018-0151-6. 

- Liu, F., Li, J., Zhang, L., 2023. Syntax and domain aware model for unsupervised program translation. In: 2023 IEEE/ACM 45th International Conference on Software Engineering. ICSE, pp. 755–767. http://dx.doi.org/10.1109/ICSE48619.2023. 00072. 

- Liu, Y., Meng, R., Joty, S., silvio savarese, Xiong, C., Zhou, Y., Yavuz, S., 2025. CodeXEmbed: A generalist embedding model family for multilingual and multitask code retrieval. In: Second Conference on Language Modeling. URL https: //openreview.net/forum?id=z3lG70Azbg. 

- Lu, S., Guo, D., Ren, S., Huang, J., Svyatkovskiy, A., Blanco, A., Clement, C., Drain, D., Jiang, D., Tang, D., Li, G., Zhou, L., Shou, L., Zhou, L., Tufano, M., Gong, M., Zhou, M., Duan, N., Sundaresan, N., Deng, S.K., Fu, S., Liu, S., 2021. CodeXGLUE: A machine learning benchmark dataset for code understanding and generation. In: Thirty-Fifth Conference on Neural Information Processing Systems Datasets and Benchmarks Track (Round 1). URL https://openreview.net/forum?id= 6lE4dQXaUcb. 

- Malhotra, R., Lata, K., 2021. An empirical study to investigate the impact of data resampling techniques on the performance of class maintainability prediction models. Neurocomputing 459, 432–453. http://dx.doi.org/10.1016/j.neucom.2020. 01.120. 

- Maron, M.E., 1961. Automatic indexing: An experimental inquiry. J. ACM 8 (3), 404–417. http://dx.doi.org/10.1145/321075.321084. 

- Moldovan, V.-A., Berciu, L.-M., Patcas, R.-D., 2024. The python software quality dataset. In: 2024 50th Euromicro Conference on Software Engineering and Advanced Applications. SEAA, IEEE, pp. 395–398. 

- Moldovan, V., Patcas, R., Motogna, S., 2026. LLMs based data augmentation techniques for python code refactoring. In: Taibi, D., Smite, D. (Eds.), Software Engineering and Advanced Applications. Springer Nature Switzerland, pp. 20–36. 

- Motogna, S., Berciu, L.-M., Moldovan, V.-A., 2024. Artificial intelligence methods in software refactoring: A systematic literature review. In: 2024 50th Euromicro Conference on Software Engineering and Advanced Applications. SEAA, pp. 309–316. http://dx.doi.org/10.1109/SEAA64295.2024.00055. 

- Noei, S., Li, H., Zou, Y., 2025. Detecting refactoring commits in machine learning python projects: A machine learning-based approach. ACM Trans. Softw. Eng. Methodol. 34 (3), http://dx.doi.org/10.1145/3705309. 

- OpenAI, 2025. Introducing GPT-5 (including GPT-5-nano). https://openai.com/index/ introducing-gpt-5-for-developers/. 

- Pan, R., Ibrahimzada, A.R., Krishna, R., Sankar, D., Wassi, L.P., Merler, M., Sobolev, B., Pavuluri, R., Sinha, S., Jabbarvand, R., 2024. Lost in translation: A study of bugs introduced by large language models while translating code. In: Proceedings of the IEEE/ACM 46th International Conference on Software Engineering. ICSE ’24, Association for Computing Machinery, http://dx.doi.org/10.1145/3597503. 3639226. 

13 

_V.-A. Moldovan et al._ 

_The Journal of Systems & Software 241 (2026) 113009_ 

Parmar, A., Katariya, R., Patel, V., 2019. A review on random forest: An ensemble classifier. In: Hemanth, J., Fernando, X., Lafata, P., Baig, Z. (Eds.), International Conference on Intelligent Data Communication Technologies and Internet of Things 

   - (ICICI) 2018. Springer International Publishing, Cham, pp. 758–763. 

- Pecorelli, F., Di Nucci, D., De Roover, C., De Lucia, A., 2019. On the role of data balancing for machine learning-based code smell detection. In: Proceedings of the 3rd ACM SIGSOFT International Workshop on Machine Learning Techniques for Software Quality Evaluation. In: MaLTeSQuE 2019, Association for Computing Machinery, pp. 19–24. http://dx.doi.org/10.1145/3340482.3342744. 

- Pecorelli, F., Di Nucci, D., De Roover, C., De Lucia, A., 2020a. A large empirical assessment of the role of data balancing in machine-learning-based code smell detection. J. Syst. Softw. 169, 110693. http://dx.doi.org/10.1016/j.jss.2020.110693, URL https://www.sciencedirect.com/science/article/pii/S0164121220301448. 

- Pecorelli, F., Palomba, F., Khomh, F., De Lucia, A., 2020b. Developer-driven code smell prioritization. In: Proceedings of the 17th International Conference on Mining Software Repositories. MSR ’20, Association for Computing Machinery, New York, NY, USA, pp. 220–231. http://dx.doi.org/10.1145/3379597.3387457. 

- Rubik, M., 2024. Radon: Measure cyclomatic complexity, maintainability index, and halstead metrics in Python code. https://radon.readthedocs.io/. 

Scientific Toolworks, I., 2024. Understand: Static analysis and code visualization tool. https://www.scitools.com/. 

   - Siam, M.K., Gu, H., Cheng, J.Q., 2024. Programming with ai: Evaluating chatgpt, gemini, alphacode, and github copilot for programmers. In: Proceedings of the 3rd International Conference on Computing Advancements. pp. 346–354. 

   - StackOverflow, 2025. Technology – 2025 stack overflow developer survey. URL https://survey.stackoverflow.co/2025/technology/#most-popular-technologieslanguage-learn. 

   - Suthaharan, S., 2016. Support vector machine. In: Machine Learning Models and Algorithms for Big Data Classification: Thinking with Examples for Effective Learning. Springer US, Boston, MA, pp. 207–235. http://dx.doi.org/10.1007/9781-4899-7641-3_9. 

   - Yu, S., Wang, T., Wang, J., 2022. Data augmentation by program transformation. J. Syst. Softw. 190, 111304. http://dx.doi.org/10.1016/j.jss.2022.111304, URL https: //www.sciencedirect.com/science/article/pii/S0164121222000541. 

- Petersen, K., Feldt, R., Mujtaba, S., Mattsson, M., 2008. Systematic mapping studies in software engineering. In: Proceedings of the 12th International Conference on Evaluation and Assessment in Software Engineering. EASE ’08, BCS Learning & Development Ltd., pp. 68–77. 

14