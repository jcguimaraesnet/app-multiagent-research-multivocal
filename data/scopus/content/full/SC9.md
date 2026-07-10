Information and Software Technology 197 (2026) 108176 



Contents lists available at ScienceDirect 

# Information and Software Technology 

journal homepage: www.elsevier.com/locate/infsof 



## Exploring full and parameter-efficient fine-tuning techniques for transformer-based design pattern detection 



### Ilyes Rezgui<sup>a</sup> , Rania Mzid<sup>b,c</sup> ,<sup>∗</sup> , Tewfik Ziadi d 

a _ELTE, Eötvös Loránd University, 1117 Budapest, Hungary_ b _ISI, University of Tunis El Manar, 2 Rue Abourraihan Al Bayrouni, Ariana, Tunisia_ c _CES Lab ENIS, University of Sfax, B.P. W3, Sfax, Tunisia_ 

d _University of Doha for Science and Technology, Doha, Qatar_ 

#### A R T I C L E I N F O 

#### A B S T R A C T 

|_Keywords:_|**Context:** Design patterns offer reusable solutions to common software development problems, improving code|
|---|---|
|Software engineering<br>LLMs<br>Fine-tuning<br>GoF patterns<br>Transformer architecture<br>Seq2Seq models|quality and maintainability. Despite their significance, design pattern instances in source code are often<br>undocumented, making difficult for developers to identify and exploit them effectively. Automating pattern<br>detection can support program comprehension, refactoring, and maintenance; however, existing approaches<br>face several challenges.<br>**Objective:** This study aims to develop an approach for detecting Gang of Four (GoF) design patterns in<br>source code. The proposed approach seeks to address the limitations of previous works, which often struggle<br>with feature generalization and structural similarity among patterns. The work further explores how transfer<br>learning strategies can enhance detection performance while reducing computational cost.<br>**Methods:** In this work, we introduce a Seq2Seq modeling approach for design pattern detection, leveraging<br>the encoder-decoder architecture of CodeT5+ to capture both structural and semantic dependencies in object-<br>oriented code. Instead of treating design pattern detection as a standard classification task, we reformulate it<br>as a sequence generation problem. We propose DPD_𝐴𝑡𝑡_+, a transformer-based framework built on a Seq2Seq.<br>The model is trained on a curated dataset and fine-tuned using two strategies: full fine-tuning and parameter-<br>efficient fine-tuning using Low-Rank Adaptation (LoRA). Both strategies are empirically evaluated to compare<br>detection accuracy and computational efficiency.<br>**Results:** Experimental results show that LoRA fine tuning reduces computational cost while retaining com-<br>petitive accuracy. Full fine-tuning, however, achieves the highest overall detection performance, reaching<br>94% accuracy on GoF design pattern detection in Java codebases. Both variants of DPD_𝐴𝑡𝑡_+ outperform<br>state-of-the-art approaches in terms of precision, recall, and F1-score.<br>**Conclusion:** The findings demonstrate that transfer learning with Transformer-based architectures effectively<br>captures the structural and semantic characteristics of design patterns in code. DPD_𝐴𝑡𝑡_+, through both full<br>fine-tuning and PEFT, offers a robust solution for automated design pattern detection, contributing to more<br>intelligent software analysis and maintenance tools.|



##### **1. Introduction** 

Design patterns are generally described as solutions to recurring problems that apply within specific contexts [1]. In software engineering, the use of design patterns helps streamline the development process and improve the overall quality of software systems across various domains. Patterns may aid in the reuse of existing knowledge related to common development challenges. They offer tried and tested solutions to specific problems across different contexts. A 

common issue, however, is the absence of documentation regarding the application of design patterns in source code. Often, developers implement design patterns without properly documenting their usage. Nonetheless, being aware of their presence in a software system can enhance a developer’s understanding and provide valuable insights to aid in software refactoring and maintenance. Detecting design patterns is one approach to minimizing refactoring and maintenance costs while 

> ∗ Corresponding author at: ISI, University of Tunis El Manar, 2 Rue Abourraihan Al Bayrouni, Ariana, Tunisia. _E-mail addresses:_ rezgui.ilyes@outlook.com (I. Rezgui), rania.mzid@isi.utm.tn (R. Mzid), tewfik.ziadi@udst.edu.qa (T. Ziadi). 

https://doi.org/10.1016/j.infsof.2026.108176 

Received 11 October 2025; Received in revised form 3 April 2026; Accepted 28 April 2026 Available online 15 May 2026 

0950-5849/© 2026 Elsevier B.V. All rights are reserved, including those for text and data mining, AI training, and similar technologies. 

_I. Rezgui et al._ 

_Information and Software Technology 197 (2026) 108176_ 

improving architectural transparency. However, manually identifying and locating these patterns can be complex and time-consuming. Developers must not only identify where a pattern should be used, but also make sure it is applied correctly to get the most benefit. 

Various methods for detecting design patterns have been proposed in the literature. Some rely on intermediate representations [2,3], transforming source code into graphs or matrices for structural comparison. Metric-based approaches [4,5] quantify structural relationships in source code to identify design patterns. However, these approaches often exhibit limited performance and struggle to distinguish between structurally similar patterns. To address these limitations, feature-based methods have recently been introduced [6,7]. These approaches detect design patterns by identifying distinctive features that characterize each pattern. They are typically supported by machine learning techniques and involve two main stages: (i) extracting syntactic and semantic features from the code through static or dynamic analysis, and (ii) training a classification model. The feature extraction phase is particularly challenging, as the quality and relevance of the extracted features directly influence model performance. Moreover, this process can be time-consuming due to the variability in design pattern implementations (i.e., variants). Another key challenge lies in effectively embedding source code into representative vectors in a highdimensional space, given its structural complexity. Embedding plays a crucial role in capturing semantic information, thereby improving classification accuracy. This step relies on embedding models [8]. Existing approaches typically convert source code into a textual representation that highlights relevant features [7,9], and then apply word embedding techniques, such as word2vec [8], to generate vector representations. 

In previous work [10], we proposed an attention-based approach for detecting Gang of Four (GoF) patterns. This method leverages a transformer-based auto-encoder to convert source code into an embedding vector that captures the contextual information of the input code. The resulting embedding is then classified into one of design pattern classes in DPD _𝐴𝑡𝑡_ using a Support Vector Machine (SVM) [11] classifier. This approach suffers from two compounding limitations: first, it entirely forgoes the generative knowledge present in the decoder during pre-training; second, the discriminative classifier optimizes fixed decision boundaries tied to the training distribution, which are inherently fragile under the structural diversity characteristic of real-world design pattern implementations. Thus, the present work addresses both limitations by adopting the full encoder–decoder architecture of CodeT5+ within a sequence generation framework, with end-to-end fine-tuning of model’s parameters. Rather than relying on frozen or partially adapted representations, both the encoder and decoder are jointly optimized for the detection task allowing the encoder to develop richer, task-specific code representations while the decoder autoregressively generates pattern identities. 

The main contributions of this paper are summarized as follows: 

- We introduce an encoder–decoder (Seq2Seq) formulation for design pattern detection, casting the task as a sequence generation problem rather than a classification task. 

- We construct the _𝐷𝑃𝐷𝐴𝑡𝑡_ dataset, which extends existing datasets by adding new pattern instances, improving class balance, and performing expert validation to ensure higher quality and better reproducibility. 

- We fine-tune the CodeT5+ Seq2Seq model using two strategies [12]: full fine-tuning and parameter-efficient fine-tuning (LoRA), and provide a detailed comparison of their performance and computational trade-offs for the design pattern detection task. 

- We present DPD _𝐴𝑡𝑡_ +, a transformer-based framework that performs automated detection of GoF design patterns directly from Java source code using the fine-tuned model. 

The rest of the paper is organized as follows. In Section 2, we present background information on the context. Section 3 provides an 

**Table 1** 

GoF <u>patterns</u> considered in this <u>paper</u> and their related categories. 

|Patterns|Category|
|---|---|
|Singleton, Abstract Factory, Factory Method, Builder, Prototype|Creational|
|Adapter, Decorator, Proxy, Facade|Structural|
|Observer, Memento, Strategy, Visitor|Behavioral|



overview of related work and concludes with a discussion. Section 4 describes the proposed approach. In Section 5, we detail the experimental results. Section 6 discusses limitations and future work, Section 7 addresses threats to validity, and Section 8 concludes the paper. 

##### **2. Background** 

In this section, we first introduce the GoF design patterns. Next, we explore the foundations of Seq2Seq models. Finally, we discuss the deep transfer learning approach. 

##### _2.1. GoF design patterns_ 

Christopher Alexander introduced the concept of pattern in architecture, proposing reusable architectural patterns to construct high-quality building designs [13]. Gamma adopted this concept in software engineering in 1995 and proposed the Gang of Four design patterns, a set of 23 patterns for object-oriented programming [14]. The GoF design patterns are organized in three categories: creational, structural, and behavioral patterns. The structural patterns deal with the construction of object-oriented concepts, whereas the creational patterns are concerned with the process of creating objects. Behavior patterns define how objects communicate and distribute responsibility. In this paper, we are interested in the detection of 13 design patterns among the 23 proposed by Gamma [14]. The considered patterns in this paper are shown in Table 1 together with the categories that they belong to. 

_Motivation for the selected patterns._ The selection of this subset of design patterns is primarily intended to ensure representative coverage of the three main categories: Creational, Structural, and Behavioral. We also followed recommendations from studies such as [15,16], which highlight patterns like Observer, Strategy, Adapter, Singleton, Factory Method, and Visitor as highly prevalent in industrial codebases. In addition, we included Abstract Factory and Prototype because of their structural and dependency similarities with Factory Method [17], allowing us to test the model’s ability to distinguish subtle variations. Builder, Facade, Decorator, Proxy, and Memento were added to further enrich the dataset’s structural diversity and complexity, providing robust evaluation scenarios linked to important software quality attributes such as modularity and maintainability. Finally, this choice is strongly motivated by the prevalence of these patterns in recent related works [9,18,19], which ensures direct and fair comparison of our results. We emphasize that the remaining GoF patterns were not excluded due to lack of importance, but rather because constructing a sufficiently large and reliably annotated dataset for all 23 patterns remains challenging. We therefore focused on patterns that are both widely represented in real-world open-source projects and well covered in existing benchmarks, as a first step toward scalable end-to-end learning. 

##### _2.2. Foundation of Seq2Seq models_ 

Seq2Seq models define the conditional probability of an output sequence _𝑌_ = ( _𝑦_ 1 _, 𝑦_ 2 _,_ … _, 𝑦𝑇_ ) given an input sequence _𝑋_ = ( _𝑥_ 1 _, 𝑥_ 2 _,_ … _, 𝑥𝑆_ ) as: 



2 

_I. Rezgui et al._ 

_Information and Software Technology 197 (2026) 108176_ 

where _𝑃_ ( _𝑦𝑡_ | _𝑦_ 1∶ _𝑡_ −1 _, 𝑋_ ) represents the probability of generating the token _𝑦𝑡_ at time step _𝑡_ , conditioned on the previous tokens _𝑦_ 1∶ _𝑡_ −1 generated so far and the entire input sequence _𝑋_ . 

Seq2seq models are generally composed of an encoder and a decoder. The encoder processes the input sequence _𝑋_ and converts it into a sequence of hidden states _ℎ_ 1 _, ℎ_ 2 _,_ … _, ℎ𝑆_ . The hidden state _ℎ𝑡_ at time step _𝑡_ is computed as: 

##### _ℎ𝑡_ = _𝑓_ enc( _ℎ𝑡_ −1 _, 𝑥𝑡_ ) 

where _𝑓_ enc is the function that processes each token in the input sequence. The decoder on the other-hands generates the output sequence _𝑌_ one token at a time. Given the context vector _𝑐_ (either the final hidden state in vanilla Seq2Seq models, or a weighted sum of hidden states in models with attention), the decoder outputs the conditional probabilities for the next token: 



where _𝑊_ and _𝑏_ are the weights and biases, and _ℎ𝑡_ is the decoder’s hidden state at time _𝑡_ . One key innovation in Seq2Seq models is the attention mechanism. This mechanism allows the model to focus on different parts of the input sequence when generating the output. Instead of relying solely on the final hidden state of the encoder, it computes a weighted sum of all encoder hidden states. The attention weights _𝛼𝑡,𝑖_ are computed as: 



where _𝑒𝑡,𝑖_ is the alignment score between the decoder’s hidden state at time step _𝑡_ and the encoder’s hidden state at position _𝑖_ . The context vector at time step _𝑡_ is then: 



Encoder-only models typically compress the entire source file into a single pooled representation. While effective for local or tokenlevel reasoning, this compression inevitably discards much of the longrange structural information required for detecting GoF design patterns, which often span multiple interacting classes and roles (e.g., Creator– Product, Subject–Observer, Visitor–Element) as it is the case for Mzid et al.’s [10]. In contrast, the Seq2Seq formulation adopted in this work enables the decoder to generate the pattern label token by token while attending to the full set of encoder states at each decoding step. Through its cross-attention mechanism, the decoder dynamically focuses on semantically relevant code regions, allowing the model to capture delegation relations, inter-class dependencies, and broader architectural intent. Various Seq2Seq architectures have been explored in software engineering tasks. For example, Chen et al. [20] used an RNN-based Seq2Seq model for code reliability prediction, while Hariharan et al. [21] applied a Seq2Seq architecture for intrusion detection. Building on this line of research, in this work, we fine-tune a transformer-based Seq2Seq model pre-trained on source code using the _𝐷𝑃𝐷𝐴𝑡𝑡_ dataset, adapting both the encoder and decoder to the specifics of GoF pattern detection. This fine-tuning enables the encoder to produce contextual representations that encode structural and semantic cues relevant to design patterns, while the decoder leverages these representations to generate the correct pattern label. 

##### _2.3. Deep transfer learning_ 

Transfer learning refers to the process of leveraging knowledge acquired from one domain or task to enhance learning in another. As illustrated by Keller et al. [22], this concept can be compared to learning a new musical instrument: for instance, an individual proficient in playing the guitar can apply their existing musical knowledge when learning the piano. Although mastering the piano still requires effort, prior experience provides a foundational advantage, reducing 

the need to start from scratch. In the context of detecting Gang of Four design patterns, training a neural network model from scratch is a viable approach but may not be the most efficient or practical. Such a model would need to learn both the structural and semantic intricacies of the programming language, including source code syntax, semantics, and the distinguishing features required to classify a code fragment into a specific design pattern. Given the inherent complexity of source code, this process is computationally expensive and resource-intensive. A more effective alternative is to leverage a pre-trained model that has already been trained on source code, thereby eliminating the need for learning fundamental representations from scratch. This pre-trained model captures general-purpose source code features, which can then be adapted to the specific task of GoF pattern detection through deep transfer learning (DTL). By fine-tuning the pre-trained model, the approach benefits from previously acquired knowledge, improving both efficiency and accuracy in detecting design patterns. Various techniques have been developed for DTL, which can be categorized into four main approaches: instance-based, feature-based, model-based (or parameter-based), and relational-based methods. 

- Instance-based transfer learning [23] involves selecting specific instances or subsets of data from the source domain and adapting them for the target domain using various weighting strategies. This approach ensures that relevant instances contribute effectively to the learning process in the target domain. 

- Feature-based methods [24] focus on transforming features from both the source and target domains into a unified representation, enhancing compatibility and facilitating knowledge transfer. 

- Model-based (or parameter-based) [25] techniques leverage pretrained models by utilizing their learned parameters. This adaptation can involve freezing certain layers, fine-tuning others, or introducing additional layers to tailor the model to the target task. 

- Relational-based approaches [26], including adversarial methods, extract transferable features by leveraging logical relationships or predefined rules learned in the source domain. Additionally, adversarial techniques, inspired by Generative Adversarial Networks (GANs), refine feature adaptation to improve generalization across domains. 

In this paper, we propose a model-based transfer learning approach for detecting GoF patterns in source code. Specifically, we select a large language model as our base model and fine-tune it using our GoF dataset by iteratively updating its parameters, making it suitable for pattern detection. Unlike instance-based methods, which rely on selecting the ‘‘right’’ instances, model-based techniques adapt feature representations, leading to better generalization. Additionally, while feature-based methods require explicit and often complex transformations, model-based approaches leverage learned representations from pre-trained models, eliminating the need for such transformations. Furthermore, using pre-trained models as base models reduces computational costs, as training does not start from scratch. 

##### **3. Related work** 

This section first reviews design pattern detection approaches, ranging from traditional structural methods to recent machine learning techniques. Then, we discuss fine-tuning strategies for software engineering tasks, particularly code-related tasks, to position our contribution within the broader software engineering landscape. At the end, we conclude with a discussion. 

##### _3.1. Traditional pattern detection methods_ 

In this section, we review traditional structural approaches for detecting design patterns. 

Graph-based techniques model software systems and design patterns as graphs to enable structural matching. Early work by Seemann 

3 

_I. Rezgui et al._ 

_Information and Software Technology 197 (2026) 108176_ 

et al. [27] focused on a limited set of patterns, followed by approaches based on vertex similarity [28] and similarity scoring [29]. Similarity Scoring Approach (SSA) proposed by Tsantalis et al. [29] represents software using UML class diagrams, converts them into binary matrices, and compares them with predefined pattern matrices to compute similarity scores. While this approach automates detection and improves scalability, it relies solely on static structural features, requires partial manual validation, and may struggle with large models or structurally diverse patterns. To overcome this, later works introduced subgraph matching techniques, such as template matching [30] and branchand-bound algorithms with backtracking [31]. Other contributions incorporate more advanced strategies, including difference calculation for incomplete pattern recovery [32] and metamodel-based matching [33]. Despite these improvements, graph-based methods remain computationally expensive and sensitive to structural variations. 

Tool-based approaches extend this idea by integrating static analysis. For instance, the MARPLE-DPD plugin [19] parses Java source code into abstract syntax trees (ASTs), extracts structural micro-features such as class hierarchies and method interactions, and groups them into candidate pattern instances. A classifier is then used to assess their similarity to known design patterns. Although effective, such approaches still depend heavily on handcrafted structural features. 

Rule-based approaches rely on manually defined representations of design patterns, such as structural rules, conceptual signatures, or declarative queries. Some methods combine static analysis with execution traces to capture both structural and behavioral aspects [34], while others use conceptual signatures to better generalize across pattern variants [35]. Although these approaches can improve accuracy, they require significant manual effort and domain expertise to define and maintain the detection rules. 

##### _3.2. Machine learning-based pattern detection techniques_ 

Machine learning-based approaches have emerged as an alternative to traditional structural methods, aiming to capture semantic, behavioral, and statistical patterns in source code through learned representations and data-driven models. This section reviews existing machine learning techniques for design pattern detection, including probabilistic approaches and feature-based methods. 

Bozorgvar et al. [15] proposed a two-phase method combining machine learning and probabilistic modeling. In the first phase, features derived from design pattern signatures are used to train a MultiLayer Perceptron (MLP) to estimate the likelihood of pattern roles. In the second phase, source code is converted into a graph to identify candidate instances. A Bayesian network is then used to model dependencies between roles and improve detection accuracy. However, this approach still depends on feature engineering and predefined pattern representations. 

Feature-based approaches are widely used for design pattern detection. They extract syntactic and semantic features from source code and use them to train machine learning models. For example, Zaharia et al. [36] proposed a language-independent method based on control-flow and data-flow representations combined with embedding techniques. Komolov et al. [37] used source code metrics with several machine learning models to detect architectural patterns. Other work [38] combines feature selection with graph matching to improve detection. Several studies focus on GoF design patterns by transforming source code into textual representations enriched with structural and semantic information [7,9]. These representations are then embedded using techniques such as word2vec and used to train supervised classifiers. In [10], the authors use an autoencoder to generate embeddings, followed by an SVM classifier. Despite their effectiveness, these approaches face key challenges. High-dimensional embeddings can lead to widely dispersed feature vectors, making pattern identification difficult [39]. In addition, pre-trained language models may generalize poorly to out-of-distribution data [40], limiting their robustness in real-world scenarios. 

##### _3.3. Fine-tuning approaches for software engineering tasks_ 

Recent studies have explored fine-tuning large language models (LLMs) to address software engineering tasks. Silva et al. [41] proposed RepairLLaMA, a program repair approach based on parameter-efficient fine-tuning. It uses a small LoRA adapter on top of a frozen model to generate code patches, reducing computational cost and limiting overfitting. Nashaat et al. [42] introduced CodeMentor, an LLM finetuned for code review tasks such as code refinement and bug report summarization. Their approach relies on datasets built from real development data and is improved using reinforcement learning with human feedback. Hoffmann et al. [43] focused on test case generation for mobile applications using supervised fine-tuning of transformerbased models. Their method produces correct and executable test cases while remaining efficient enough for standard hardware. Mohammad et al. [44] proposed a full fine-tuning approach based on code mutation. It improves the generation of diverse and semantically correct code variants while preserving correctness through unit testing. Overall, these works explore both full and parameter-efficient fine-tuning. However, they do not consider smaller models, nor do they address design pattern detection in source code. 

##### _3.4. Discussion_ 

Traditional design pattern detection approaches include, graphbased, tool-based, and rule-based methods [19,29–31,34,35]. While these approaches provide structured ways to analyze software systems, they remain largely dependent on handcrafted representations and struggle to capture the full complexity of design patterns, particularly their behavioral aspects and structural variability. 

Machine learning-based approaches, including probabilistic and feature-based methods [7,9,10,15,44], aim to overcome these limitations by learning representations from data. Despite their effectiveness, they often rely on complex feature engineering or high-dimensional embeddings, and face challenges related to generalization and robustness, especially when dealing with diverse or unseen code structures [45]. 

Recent work on fine-tuning large language models for software engineering tasks [41–43] shows promising results but remains underexplored for design pattern detection. In this context, our work proposes a different perspective by reformulating pattern detection as a sequence generation task. We investigate both full fine-tuning and parameter-efficient strategies within a Transformer-based encoder– decoder architecture, enabling end-to-end learning of semantic and structural relationships in source code. 

Finally, we acknowledge the strong capabilities of general-purpose LLMs, such as GPT-4, DeepSeek, and similar frontier models, in code understanding tasks [46]. While these models may achieve competitive performance in zero-shot or few-shot settings, they present limitations in our context, including lack of transparency and reproducibility, high inference costs, and dependence on proprietary infrastructures. In contrast, our work focuses on a complementary setting: resourceefficient, open, and fully reproducible fine-tuned models that can be deployed in practical environments. 

##### **4. Proposed approach** 

The proposed approach is organized into three fundamental components: the Data Collection Block, the Model Development Block, and the Pattern Detector Block. The Data Collection Block is responsible for acquiring, curating, and labeling raw Java files to construct a clean dataset suitable for training. This phase includes collecting additional files, verifying labels through expert review, and ensuring the dataset’s balance and coverage. The Model Development Block builds on this curated dataset and includes both pre-processing and model fine-tuning. In this step, the source code files are preprocessed by tokenizing and removing comments to reduce file length while preserving structural 

4 

_I. Rezgui et al._ 

_Information and Software Technology 197 (2026) 108176_ 



**Fig. 1.** An overview of the proposed approach. 

and semantic information. The preprocessed data is then used to finetune a pre-trained Seq2Seq transformer model, adapting it to detect GoF design patterns directly from source code without manual feature engineering. Finally, the Pattern Detector Block packages and stores the trained model, enabling automatic detection of GoF design patterns in unseen Java code. Fig. 1 illustrates the overall workflow of the proposed approach. 

##### _4.1. Data collection and preparation_ 

This section explain in detail the data collection and preparation block. The effective training of any machine learning model requires a substantial volume of high-quality data. In our specific research context and to identify GoF design patterns within Java source code, we opted for class-level detection as it is the lowest possible level of granularity that may capture design patterns. We started by conducting an extensive search for an open-source dataset suitable for our study. This led us to the corpus by Nazar et al. [9], known as _𝐷𝑃𝐷𝐹_ , which is one of the few publicly available design pattern detection datasets. _𝐷𝑃𝐷𝐹_ builds upon P-MART [47], a well-established benchmark containing Java classes from nine open-source projects (e.g., QuickUML, Lexi, JRefactory, NetBeans, JUnit, JHotDraw, MapperXML, Apache Nutch, and PMD). Each file in _𝐷𝑃𝐷𝐹_ was labeled by at least three annotators with expertise in Java development and design patterns, including research and teaching experience in software engineering. The dataset covers 12 GoF design patterns, Singleton, Abstract Factory, Factory Method, Builder, Prototype, Adapter, Decorator, Proxy, Facade, Observer, Memento, and Visitor, in addition to an ‘‘unknown’’ label. As shown in Fig. 2, _𝐷𝑃𝐷𝐹_ served as the starting point for constructing our _𝐷𝑃𝐷𝐴𝑡𝑡_ dataset. First, we curated the original corpus by examining all files, removing redundant entries, and retaining only those with valid GitHub URLs and a ‘‘.java’’ file extension. This step resulted in a cleaned subset of 943 labeled examples, with an imbalanced distribution of instances across the covered design patterns. Next, we expanded the refined _𝐷𝑃𝐷𝐹_ corpus by collecting additional Java files from opensource GitHub repositories, covering both the original 12 GoF patterns and an additional pattern, Strategy. This expansion followed the data collection strategy proposed by Gelman et al. [48]. We selected repositories that explicitly document the use of GoF design patterns, provide a re-distributable license, and have at least 10 GitHub stars to ensure code quality. All newly collected files were manually reviewed and validated by domain experts (faculty members and researchers) to confirm the correctness of the pattern annotations. The inclusion of the Strategy pattern was motivated by its frequent occurrence in real-world software systems and its importance in related work [34,49,50], despite being absent from the original _𝐷𝑃𝐷𝐹_ dataset. All Strategy instances were collected exclusively during this expansion phase from newly identified GitHub repositories and do not originate from the original _𝐷𝑃𝐷𝐹_ projects. This process expands the baseline dataset, balances the distribution across patterns (see Table 2), and brings the total number of labels to 14, including the ‘‘unknown’’ label, resulting in a final corpus of 1645 labeled Java files. This Table reports the exact number of instances per design pattern class in both DPD_F and the final _𝐷𝑃𝐷𝐴𝑡𝑡_ dataset, confirming the inclusion of the newly added Strategy pattern and the resulting class balance. 



**Fig. 2.** Data construction pipeline for the _𝐷𝑃𝐷𝐴𝑡𝑡_ dataset. 

**Table 2** 

Comparison of DPD_F and _𝐷𝑃𝐷𝐴𝑡𝑡_ for GoF patterns. 

|GoF pattern|DPD_F|_𝐷𝑃𝐷𝐴𝑡𝑡_|
|---|---|---|
|Builder|91|123|
|Prototype|76|142|
|Observer|84|131|
|Facade|80|113|
|Strategy|0|129|
|Decorator|60|109|
|Adapter|53|113|
|Proxy|73|116|
|AbstractFactory|51|103|
|Singleton|76|108|
|Visitor|77|112|
|Memento|122|105|
|FactoryMethod|105|123|
|Unknown|98|155|



##### _4.2. Model development_ 

This section provides a detailed overview of the selected base model and the methodology employed for fine-tuning it to enable the detection of GoF design patterns. 

##### _4.2.1. Base model_ 

The base model serves as the foundation for the fine-tuning process, providing the initial parameters that are adapted to the target task. Since fine-tuning requires updating the weights of a pre-trained neural network, selecting a model with an appropriate balance between capacity and computational efficiency was essential. Several models are available for source code representation learning, each with specific characteristics, as discussed in [51]. In our work, we selected CodeT5+ 

5 

_I. Rezgui et al._ 

_Information and Software Technology 197 (2026) 108176_ 



**Fig. 3.** Pre-processing pipeline for design pattern detection. 

with 220 million parameters as the base model. This choice was motivated by multiple factors: the relatively small size of our dataset (1645 instances), the available computational resources (c.f., Section 5.2), the open-source accessibility of the model, and the alignment of its architecture with the design pattern detection task. Opting for a model of moderate size also helps mitigate the risk of overfitting on the _𝐷𝑃𝐷_  𝐴𝑡𝑡_ dataset [10], thus supporting better generalization to unseen code. 

##### _4.2.2. Preprocessing_ 

Since source code in its raw form cannot be directly used for finetuning, several preprocessing steps were necessary. Fig. 3 illustrates the overall pipeline implemented in this study. First, we applied a cleaning step to remove comments from the source files. This reduction in file length ensured that only the structural and semantic elements relevant for design pattern detection were retained, optimizing the input size for training. Next, we formatted the cleaned corpus into a structure compatible with the tokenization step. We then tokenized the source code field using CodeT5’s specialized code tokenizer [52]. This tokenizer, specifically designed for programming languages, converts the source code from its raw textual format into a tensor of integer tokens that the model can process during training and inference. This specific tool accounts for the syntactic and structural intricacies of source code as it is built for code tokenization purposes. By doing so, it ensures accurate transformation of source code and avoids mapping tokens to unknown values. CodeT5’s tokenizer follows a Byte-level BPE (Byte Pair Encoding) approach, as described by Radford et al. [53], and employs a vocabulary of 32,000 tokens, optimized for handling code. We also gave a numerical label for each design pattern so that the model could compare its predictions with the ground truth during training (see Fig. 4). 

Furthermore, we have applied padding to ensure all tokenized sequences, whether input or output, had a consistent length, which is crucial for efficient batch processing. Shorter sentences or code snippets were padded with a special [PAD] token, making all inputs uniform in size, which is essential for GPU computation. Next, we employed truncation to prevent input sequences from exceeding the model’s maximum allowed length, ensuring that overly long text was cut off at the defined threshold, retaining only the most relevant portion of the sequence. To avoid penalizing the model for predicting padding tokens, we replaced [PAD] tokens in the labels with -100, ensuring the loss function ignored them. The final output of this pipeline is a fully preprocessed corpus, ready for the fine-tuning phase. 



**Fig. 4.** An example of a Java class ‘‘DataBase’’ to which the Singleton pattern is applied. 



**Fig. 5.** Overview of the training, testing and evaluation phases for design pattern detection. 

As shown in Fig. 5, after preprocessing, the dataset is divided into training and testing subsets. The training set is used to fine-tune the model (either through full fine-tuning or LoRA), guided by the crossentropy loss. The testing set is then employed for model inference, where predictions are generated and quantitative metrics (accuracy, precision, recall, F1-score) are computed. Finally, beyond these metrics, the evaluation phase validates the approach on real-world software projects, providing qualitative insights into the practical applicability of the proposed method. 

##### _4.2.3. Model fine-tuning_ 

In this paper, we investigate two fine-tuning strategies for design pattern classification [54]: (i) full model fine-tuning, and (ii) a parameter-efficient fine-tuning approach based on Low-Rank Adaptation (LoRA). Both strategies optimize the model using the standard cross-entropy loss over the generated token sequence, 



where _𝑥_ is the tokenized input Java class and _𝑦𝑡_ is the target token at step _𝑡_ . The target sequence is the textual label of the design pattern (e.g., ‘‘Singleton’’, ‘‘Observer’’). 

_Full model fine-tuning._ The fine-tuning process, which involves adapting the pre-trained base model to learn the semantic and structural characteristics of the _𝐷𝑃𝐷_  𝐴𝑡𝑡_ dataset, is illustrated in Fig. 6. We began by loading all pre-trained weights of the CodeT5+ base model, denoted as the initial _𝑊_ 0 matrices in the figure. Each weight matrix was stored in 32-bit floating-point format. The parameters were first loaded into CPU RAM and then transferred to GPU VRAM using CUDA. Once the model was loaded and the input data preprocessed, training proceeded 

6 

_I. Rezgui et al._ 

_Information and Software Technology 197 (2026) 108176_ 



**Fig. 6.** Full model’s fine-tuning for design pattern detection. 

iteratively in mini-batches. For each batch, a forward pass was executed using the fixed architecture and the pre-trained parameters _𝑊_ 0. During this pass, intermediate activations were stored in GPU memory for use in the backward pass. In the backward pass, the gradient of the loss with respect to each weight, _𝜕𝑊_<sup>_𝜕𝐿_,wascomputed.Thesegradientswere</sup> then used by the optimizer to update the weights according to the rule: 



This forward–backward process was repeated for multiple epochs until convergence, producing the fine-tuned parameters _𝑊_<sup>∗</sup> . Since all base model parameters are trainable in full fine tuning, the pre-trained knowledge is progressively adapted with each epoch. The number of epochs refers to how many times our _𝐷𝑃𝐷𝐴𝑡𝑡_ dataset is passed through the model during training, including both the forward and backward passes. 

_LoRA fine-tuning._ The LoRA fine-tuning process aims to effectively adapt the pre-trained CodeT5+ model for the task of GoF design pattern detection. As illustrated in Fig. 7, instead of fine-tuning all the parameters of CodeT5+, which consists of hundreds of millions of parameters, LoRA selectively updates a small subset of additional parameters by injecting low-rank trainable matrices into the existing weights of key transformer layers, primarily within the self-attention modules. In our implementation, LoRA adapters are applied symmetrically to all attention layers of both the encoder and the decoder components of CodeT5+ plus the feed-forward layers, this includes Self-Attention in the Encoder, Self-Attention in the Decoder, CrossAttention where the Decoder looks at the Encoder’s output and the Position-wise Feed-Forward Networks across the entire model, ensuring that parameter-efficient adaptation affects not only code representation learning in the encoder but also the cross-attention-driven decoding process. Formally, consider a weight matrix _𝑊_ 0 ∈ R<sup>_𝑑_×</sup><sup>_𝑘_</sup> representing a linear transformation in one of the model’s layers, where _𝑑_ is the input dimension and _𝑘_ is the output dimension. Rather than updating _𝑊_ 0 directly during fine-tuning, we keep it frozen and learn an additive low-rank update: 

_𝛥𝑊_ = _𝐴𝐵, 𝑊_<sup>′</sup> = _𝑊_ 0 + _𝛥𝑊,_ 

where 



and _𝑟≪_ min( _𝑑, 𝑘_ ). This decomposition reduces the number of trainable parameters from _𝑑_ × _𝑘_ to _𝑟_ × ( _𝑑_ + _𝑘_ ). 

During the forward pass, for an input vector _𝑥_ ∈ R<sup>_𝑑_</sup> , the adapted transformation is: 

_𝑦_ = _𝑊_<sup>′</sup> _𝑥_ = _𝑊_ 0 _𝑥_ + _𝐴_ ( _𝐵𝑥_ ) _._ 

Here, _𝐵𝑥_ ∈ R<sup>_𝑟_</sup> projects the input into a low-dimensional subspace, and _𝐴_ ( _𝐵𝑥_ ) ∈ R<sup>_𝑘_</sup> maps it back to the output space, capturing task-specific adaptation. The model learns to modify the original transformation by adjusting only the low-rank matrices _𝐴_ and _𝐵_ , preserving the pre-trained knowledge in _𝑊_ 0. 

After training for multiple epochs, the final fine-tuned model is represented by the merged weights: 



which combine the frozen pre-trained parameters with the learned task-specific adaptation. 

_Discussion._ The computational overhead of fine-tuning can be approximated by the number of trainable parameters, which directly determines memory usage for gradient updates and optimizer states [12]. For the full fine-tuning setting for design pattern detection, exactly 222,882,048 parameters were updated using backpropagation during the fine-tuning process. In contrast, the LoRA strategy keeps the base weights _𝑊_ 0 frozen and introduces lightweight low-rank adaptation matrices _𝛥𝑊_ , resulting in only fine-tuned 12,976,128 trainable parameters out of the 220 million total parameters, which is approximately 5.5% of the model’s parameters. 

##### _4.3. Pattern detector_ 

The Pattern Detector block encapsulates the fine-tuned CodeT5+ model, enabling automatic GoF design pattern detection on unseen Java source code. Once fine-tuning is complete, the adapted weights ( _𝑊_<sup>∗</sup> for full fine-tuning or _𝑊_ merged = _𝑊_ 0 + _𝛥𝑊_ for LoRA) are serialized and saved to disk, producing a reusable artifact that can be loaded and queried without retraining. 

At inference time, the saved model accepts a raw Java code and applies the same preprocessing pipeline described in Fig. 3; comment removal, tokenization, padding, and truncation before being fed to the model. The detection is then treated as a conditional text generation task: given the encoder’s contextual representation of the input Java class, the decoder autoregressively generates a textual sequence token by token until the end-of-sequence ([EOS]) token is produced. Since each training target is one of the 14 class label strings, the model learns to generate exactly one label from _𝐷𝑃𝐷𝐴𝑡𝑡_ as its output. The generated sequence is then detokenized and matched against the classes via exact string matching to yield the final predicted category _̂𝑐_ . This generationbased formulation is a key characteristic of the proposed approach: rather than relying on a fixed classification head, the model leverages the semantic alignment between label strings and code concepts learned during pre-training. A normalization step (lowercasing and whitespace trimming) handles edge cases, with any unresolved output falling back to the Unknown category. 

7 

_I. Rezgui et al._ 

_Information and Software Technology 197 (2026) 108176_ 



**Fig. 7.** LoRA fine tuning for design pattern detection. 

##### **5. Experimentation and evaluation** 

##### _5.2. Hardware configuration_ 

This section presents the experimental setup and evaluation results. We begin by defining the performance metrics used for assessment, followed by a discussion of the parameters selected for fine-tuning. Finally, we provide a detailed analysis of the results obtained from our approach. 

##### _5.1. Evaluation metrics_ 

To evaluate our model, we used standard metrics, including accuracy, precision, recall, and F1-score. These metrics are derived from a confusion matrix, which categorizes model predictions into four fundamental outcomes: 

- **True Positive (TP):** The model correctly identifies a specific GoF pattern when it is actually present in the code. 

- **True Negative (TN):** The model correctly identifies that a specific GoF pattern is not present. 

- **False Positive (FP):** The model incorrectly flags a pattern that does not exist. 

- **False Negative (FN):** The model fails to detect a pattern that is actually present. 

Using these outcomes, we assessed performance both globally and for each individual GoF pattern. The metrics are defined as follows: 

- **Accuracy:** The ratio of correctly predicted outputs to the total number of predictions, measuring the overall effectiveness of the model. 

   - TP + TN 

Accuracy = 

   - TP + TN + FP + FN 

- **Precision:** The ratio of correctly predicted positive instances to the total predicted positive instances, highlighting the model’s ability to minimize false positives. 

- TP 

- Precision = 

   - TP + FP 

- **Recall:** The ratio of correctly predicted positive instances to the total actual positive instances, reflecting the model’s ability to identify all relevant outputs. 

TP Recall = 

##### TP + FN 

- **F1-Score:** The harmonic mean of precision and recall, providing a balanced measure of the model’s performance, especially for imbalanced datasets. 

- F1-Score = 2 ⋅<sup>Precision ⋅Recall</sup> Precision + Recall 

The training and evaluation of the proposed _𝐷𝑃𝐷𝐴𝑡𝑡_ + model were conducted using the Google Colab cloud platform, using an NVIDIA T4 GPU with 16 GB of VRAM. This environment provided the necessary high-parallelization capabilities and accelerated computational resources required for the efficient fine-tuning of the transformerbased architecture and the execution of our LoRA-enhanced detection experiments. 

##### _5.3. Training configurations_ 

Both the full fine-tuning and LoRA fine-tuning were conducted using the same base training configuration wherever possible. For reproducibility, the common training hyperparameter configurations used for both the full and LoRA fine-tuning strategies are summarized in Table 3. To ensure the model learns robust pattern semantics rather than project-specific stylistic cues, we implemented a project-level splitting strategy where all 1645 instances were first grouped by their original GitHub repositories. These project units were then partitioned into three disjoint subsets 80% for training, 10% for validation, and 10% for testing, ensuring that no repository appeared in more than one split. This approach prevents information leakage by isolating project-specific conventions, such as naming styles and architectural templates, while maintaining a consistent distribution of pattern classes and comparable codebase diversity across all partitions. By using the validation set exclusively for monitoring loss and checkpoint selection and holding out the test set for final performance reporting, we provide a more realistic assessment of the model’s ability to generalize to entirely unseen software projects. For the baseline full fine-tuning, we used the Hugging Face Transformers library with standard Seq2Seq training arguments. The model was trained for 10 epochs with a perdevice batch size of 8 and gradient accumulation over 4 steps, resulting in an effective batch size of 32. We used a learning rate of 5e−5, 200 warmup steps, and a weight decay of 0.01 to encourage generalization. Mixed-precision training (fp16 = True) was enabled to reduce memory usage, allowing us to run the experiments on the available hardware. Evaluation and checkpointing were performed at each epoch, keeping only the two most recent checkpoints. The best-performing model was restored at the end of training. Logging occurred every 10 steps, and predictions were generated using the decoder of the fine-tuned model. 

All hyper-parameters were fixed _a priori_ based on commonly adopted values in prior work on transformer-based code understanding models that also fine-tunes T5 models as a base model. [51,55,56] For the LoRA fine-tuning, we configured LoRA adapters using the 

8 

_I. Rezgui et al._ 

_Information and Software Technology 197 (2026) 108176_ 

###### **Table 3** 

Summary of fine-tuning hyper-parameters. 

###### **Table 4** 

Classification results for design <u>pattern</u> recognition. 

|Parameter|Value|Design pattern|Precision|Recall|F1-score|
|---|---|---|---|---|---|
|Model|CodeT5+|Abstract Factory|1.00|0.79|0.88|
|Total trainable parameters|222,882,048|Adapter|0.95|0.79|0.86|
|Number of epochs|10|Builder|0.94|1.00|0.97|
|Per-device batch size|8|Decorator|1.00|1.00|1.00|
|Effective batch size|32|Facade|0.95|0.86|0.90|
|Gradient accumulation steps|4|Factory Method|0.77|1.00|0.87|
|Learning rate|5e−5|Memento|0.88|0.93|0.90|
|Warm-up steps|200|Observer|1.00|1.00|1.00|
|Weight decay|0.01|Prototype|1.00|1.00|1.00|
|Mixed precision (FP16)|Enabled|Proxy|1.00|0.88|0.94|
|Evaluation strategy|Epoch|Singleton|1.00|1.00|1.00|
|Checkpoint save strategy|Epoch|Strategy|0.88|1.00|0.94|
|Max saved checkpoints|2|Visitor|1.00|1.00|1.00|
|Best model reload|Enabled|**Accuracy**|||**0.94**|
|Prediction with generate<br> Logging steps|Enabled<br>Every 10 steps|**Weighted** **Avg**|**0.95**|**0.94**|**0.94**|
|Logging first step|Enabled|||||



LoraConfig class from the PEFT library, while keeping the same base training parameters described above. Each LoRA-specific parameter was selected to balance model expressiveness, generalization, and resource constraints. We apply various experiments on the parameters by varying the rank _𝑟_ = 8, 16, and 32, controlling the dimensionality of the low-rank matrices injected into the attention layers. This determines the number of trainable parameters per adapted layer, with a lower rank reducing memory usage and training time while preserving taskspecific adaptation capacity. The scaling factor _𝑙𝑜𝑟𝑎_  𝑎𝑙𝑝ℎ𝑎_ = 16 was used to amplify the impact of the low-rank updates, compensating for the reduced rank. A dropout rate of 0.1 was applied inside the LoRA modules for regularization. The task type was set to _𝑆𝐸𝑄_ _2 𝑆𝐸𝑄_  𝐿𝑀_ to ensure that adapters were correctly inserted into the encoder– decoder layers. No bias terms in the original model were modified; only the LoRA-specific weights were trainable, with the rest of the model kept frozen. Finally, the LoRA configuration was applied using _𝑔𝑒𝑡_  𝑝𝑒𝑓𝑡_  𝑚𝑜𝑑𝑒𝑙_ , transforming the base model into a parameter-efficient version in which only a small subset of additional weights was optimized. This configuration reduced the number of trainable parameters while maintaining strong detection performance. We have also worked around the layers in which the parameters are being updated by ablating some layers and focusing on the performance of the others across the epochs . 

##### _5.4. Performance of our approach (RQ1)_ 

This section details our findings for the two fine-tuning methods we propose in this paper. Specifically, we evaluate the performance of the full fine-tuning and the LoRA fine-tuning using the metrics defined earlier. 

##### _5.4.1. Full model’s fine-tuning detection evaluation_ 

The classification results demonstrate the model’s high efficacy in identifying design patterns, achieving a robust weighted average F1-score of 0.94. Perfect F1-scores were obtained for the Decorator, Observer, Prototype, Singleton, and Visitor patterns, suggesting that the model successfully captured the distinct structural signatures and unique boilerplate code associated with these specific implementations. While performance remained strong across the dataset, a slight performance trade-off is observed within creational patterns; specifically, the Factory Method exhibited a lower precision (0.77) despite a perfect recall, indicating a tendency for the model to over-classify similar structures into this category. Conversely, Abstract Factory and Adapter both showed a lower recall (0.79), suggesting that more complex or varied implementations of these patterns occasionally bypassed detection. Despite these minor discrepancies likely stemming from the shared 



**Fig. 8.** Train and validation losses for the full fine-tuning. 

architectural characteristics of factory-based patterns the consistent macro and micro averages of 0.95 and 0.94 respectively validate the model’s reliability and generalization across the majority of the studied design patterns (see Table 4). 

Since we are treating the GoF patterns detection as a generation task rather than a supervised-learning based classification, the decoder did generate one surplus class in the full fine-tuning case, that was labeled as a ‘‘Protocol’’. Even tho this class was generated by the decoder, only two files from the test set (250 files) were attributed to this class, which showcases that the Base-model was influenced well enough by the GoF patterns dataset to learn to generate code within the domain of the classes that it was trained on. The overall accuracy of the Fully finetuned model is 94%, and both for both the Recall and F1-scores 94% were achieved. 

To ensure that the model did not overfit the data, we conducted an analysis of the training and validation loss over 10 epochs. Specifically, the model was trained for multiple epochs, and the corresponding loss values were recorded at each step. The learning curve, presented in Fig. 8, shows a significant decrease in training loss and in validation loss, with both curves converging around a loss value of 1. This convergence indicates that the model successfully learned the underlying data distribution without overfitting and was able to stabilize. The parallel decline in both training and validation losses suggests good generalization, as the model’s performance improves consistently on unseen validation samples. Moreover, the absence of divergence between the two loss curves provides additional evidence that the model maintained stability and avoided memorization of the training data. 

##### _5.4.2. LoRA model’s fine-tuning detection evaluation_ 

The transition to a sequence-to-sequence generation framework using LoRA reveals a distinct shift in model behavior, characterized by a 

9 

_I. Rezgui et al._ 

_Information and Software Technology 197 (2026) 108176_ 

**Table 5** 

Classification results for design <u>pattern</u> recognition with LoRA. 

|Design pattern|Precision|Recall|F1-score|
|---|---|---|---|
|Abstract Factory|0.17|0.05|0.08|
|Adapter|0.95|0.83|0.88|
|Builder|0.94|0.94|0.94|
|Decorator|1.00|0.89|0.94|
|Facade|1.00|0.94|0.97|
|Factory Method|0.55|0.35|0.43|
|Memento|1.00|0.83|0.91|
|Observer|1.00|0.96|0.98|
|Prototype|0.94|1.00|0.97|
|Proxy|1.00|0.70|0.82|
|Singleton|1.00|0.92|0.96|
|Strategy|1.00|0.76|0.86|
|Visitor|1.00|0.95|0.98|
|**Accuracy**|||**0.88**|
|**Weighted** **Avg**|**0.88**|**0.78**|**0.82**|





**Fig. 9.** Train and validation losses for LoRA fine-tuning. 

notable increase in vocabulary volatility compared to full fine-tuning. While the model maintains high structural fidelity for behavioral patterns like Observer and Visitor (F1-scores of 0.98), the generative nature of the task introduces several out-of-distribution classes such as abstract module, publisher, and provider which lack support in the ground-truth dataset. This phenomenon is particularly detrimental to creational patterns; for instance, Abstract Factory saw an F1-score collapse to 0.08, as the model’s probability mass was fragmented across synonymous but technically incorrect generated tokens like ‘abstract’ or ‘factory’. These results suggest that while parameter-efficient finetuning via LoRA preserves the core architectural signatures of most patterns, the lack of a constrained classification head allows the model to prioritize semantic plausibility over taxonomic rigidity, necessitating post-hoc label mapping or constrained decoding to restore precision in generative pattern recognition tasks. Overall the model was able to give good results though. In fact a 93% of precision was achieved if we omit the out-of-vocabulary classes, and a 85% of F1-score was maintained. These results are shown in the confusion matrix in Fig. 15 We also studied the learning curve for the LoRA fine tuning process. Both losses steadily decreased, showing that the model was learning effectively and generalizing well. Most of the improvement happened in the first 5 epochs, after which the model’s performance stabilized. Given that, this point serves as a suitable candidate for saving the best-performing checkpoint to avoid overfitting and ensure efficient training. Fig. 9 shows the loss trend across the epochs. 

_Ablation study of LoRA rank._ To further investigate why the LoRA fine-tuned model exhibits the performance trends shown in Table 5, we conducted a principled ablation study exploring the impact of key LoRA hyper-parameters. This analysis evaluates the low-rank dimension _𝑟_ ∈{8 _,_ 16 _,_ 32} and different target module configurations 

###### **Table 6** 

Trainable <u>parameter</u> breakdown for different LoRA target layers. 

|Target layers|Trainable parameters|Total parameters|% Trainable|
|---|---|---|---|
|Encoder|2,359,296|225,241,344|1.0475%|
|Decoder|3,538,944|226,420,992|1.5630%|
|Q, V projections|1,769,472|224,651,520|0.7877%|
|All Attention + FFN|12,976,128|224,651,520|5.5017%|



(Q/V, all attention projections, encoder-only, and decoder-only and all attention modules). All experiments were performed using the base training configuration described earlier, modifying only LoRA-specific parameters. 

- **Effect of rank and scaling factor :** Fig. 10 shows that very small ranks (e.g., _𝑟_ = 8) has lower results compared to higher rank value. In fact when increasing the rank the performance steadily improves . A mid-range setting of _𝑟_ = 16 yields the best performance–cost trade-off, while _𝑟_ = 32 produces only marginal additional gains at a higher memory cost. The LoRA settings proposed in RepairLLaMA [41] (rank 16) fall within our search grid, and we observe that they provide reasonable but not optimal performance for design pattern detection. This difference aligns with the nature of the task: program repair mostly involves localized edits at the line or statement level, whereas detecting design patterns requires modeling long-range semantic and structural dependencies across entire files and class hierarchies. Our ablations confirm that higher ranks (e.g., _𝑟_ = 32) better capture such global relationships, whereas lower ranks suffice for localized tasks such as repair. 

- **Effect of applying LoRA to different layers in the Architecture :** To evaluate the impact of Low-Rank Adaptation (LoRA) on model performance and efficiency, we conducted a comparative study by targeting four specific architectural components: the attention layers of the encoder only, the attention layers of the decoder only, the Query/Value (Q, V) Projections, and all of the attention-layers all together in both the encoder and the decoder. Each configuration was trained for 10 epochs to observe convergence rates and final loss metrics. The distribution of trainable parameters varies depending on the targeted layers. As shown in the comparison below, targeting the attention projections (Q, V) represents the most lightweight approach, while targeting all attention layers and the Position wise Feed-Forward Networks (FFN) layers requires the largest parameter overhead. Applying LoRA to the encoder layers yielded a stable training trajectory, starting at a validation loss of 0.601 and reaching a final value of 0.49032 as it is shown in Fig. 11. This suggests that the encoder holds critical semantic information that benefits from fine-tuning. Interestingly, the decoder-only configuration performed the poorest despite having the highest percentage of trainable parameters. It concluded with a validation loss of 0.52894, indicating that fine-tuning the decoder alone may be less effective for this specific task. Targeting the attention mechanism’s Query and Value matrices within both the encoder and decoder proved to be the most effective strategy. Despite utilizing only 0.7877% of the total parameters, it achieved the lowest final validation loss of 0.48938. 

To conclude, the ablation study demonstrates a clear correlation between the breadth of LoRA target modules and the model’s ultimate convergence stability. While the Encoder-only and All layers configurations initially exhibited similar trajectories, the extended 10-epoch analysis reveals that the All layers approach achieves the superior global minimum, reaching a validation loss of 0.478. This suggests that while the encoder is fundamental for capturing the structural nuances of the input code, the simultaneous adaptation of the decoder allows 

10 

_I. Rezgui et al._ 

_Information and Software Technology 197 (2026) 108176_ 



**Fig. 10.** Loss per value of rank on both training and validation data. 



**Fig. 11.** Ablation study of the architectural layers of the neural network architecture. 

for a more refined alignment between the internal code representations and the target sequence generation. Conversely, the performance gap observed in the QV-only and Decoder-only experiments indicates that focusing solely on attention projections or the output stage is insufficient for the complex task of multi-class design pattern detection. Ultimately, the fine tuning all attention layers in addition to the FFN provides the most robust optimization surface, effectively mitigating the label hallucination issues observed in more restricted parameterefficient fine-tuning setups. As a final architectural choice, we apply LoRA to fine-tune the residual Feed-Forward Networks and all attention layers (including Query, Key, Value, and Output projections) across the entire transformer stack. 

##### _5.4.3. Case study on real-world projects_ 

To complement the quantitative evaluation, we conduct a case study to analyze the behavior of _𝐷𝑃𝐷𝐴𝑡𝑡_ + on concrete software examples. The objective is to provide deeper insights into the model’s strengths, generalization capability, and practical applicability. 

We first evaluate our model on a set of representative design pattern implementations used in [34]. The results are reported in Table 7. _𝐷𝑃𝐷𝐴𝑡𝑡_ + correctly detects all considered design patterns. This indicates that the model effectively captures the core structural characteristics of GoF patterns, even in the presence of implementation variability. 

To further assess generalization, we evaluated _𝐷𝑃𝐷𝐴𝑡𝑡_ + on an independent GitHub repository<sup>1</sup> containing implementations of GoF design 

###### **Table 7** 

Detection results on representative examples in [34]. 

|Design pattern|Project name|#Files|Detected pattern|
|---|---|---|---|
|AbstractFactory|Gourmet PizzaFactory|5|AbstractFactory|
|Adapter|Csv Adapter|13|Adapter|
|Builder|Construction House|3|Builder|
|Decorator|Flower Bouquet|5|Decorator|
|Facade|Order Controller|3|Facade|
|FactoryMethod|Pizza Factory|3|FactoryMethod|
|Memento|Employee Originator|5|Memento|
|Observer|Product Bidder|10|Observer|
|Prototype|Document Prototype|3|Prototype|
|Proxy|Report Generator|8|Proxy|
|Singleton|Singleton Demo|3|Singleton|
|Strategy|Encryptor|9|Strategy|
|Visitor|Mail Client Visitor|8|Visitor|



###### **Table 8** 

Generalization <u>performance</u> on independent GitHub <u>pattern</u> implementations. 

|Design pattern|#Files|Predicted pattern|Correct|
|---|---|---|---|
|AbstractFactory|9|AbstractFactory|Yes|
|Adapter|6|Adapter|Yes|
|Builder|4|Builder|Yes|
|Decorator|5|Decorator|Yes|
|Facade|7|Facade|Yes|
|FactoryMethod|5|FactoryMethod|Yes|
|Memento|3|Memento|Yes|
|Observer|4|Observer|Yes|
|Prototype|3|Prototype|Yes|
|Proxy|3|Proxy|Yes|
|Singleton|1|Singleton|Yes|
|Strategy|5|Strategy|Yes|
|Visitor|7|Visitor|Yes|



patterns, where each project corresponds to a specific pattern. Table 8 summarizes the results at the pattern level. 

For all evaluated patterns, the model correctly identified the corresponding design pattern, despite variations in coding style and implementation details. These results demonstrate the robustness of the learned representations and confirm the model’s ability to generalize to unseen code bases. 

##### _5.4.4. Computational analysis_ 

We also investigated the computational cost associated with the fine-tuning process. Specifically, we compared GPU memory usage and training time between the full fine-tuning approach and the parameterefficient LoRA method. Fig. 12 illustrate the differences in resource consumption and execution time between the two strategies with respect to the size of the dataset inputted. 

We began by constructing four datasets of varying sizes, starting with the full dataset of 1645 instances and creating subsets corresponding to 75%, 50%, and 25% of the original data. As shown in Fig. 12, fine-tuning the model using LoRA required less execution time compared to full fine-tuning. This result is expected, as LoRA updates only a small subset of parameters, reducing computational overhead in terms of training time. 

We can also see in Fig. 12 that fine-tuning the model using LoRA consumes less GPU resources compared to full model fine-tuning. LoRA’s reduced GPU resource usage can be attributed to several factors. First, the majority of the base model’s weights remain frozen during fine-tuning, eliminating the need to compute gradients or store gradient information for those large parameters, which greatly reduces memory consumption. 

Second, since only a small subset of low-rank matrices are trained, the storage and computation of gradients are greatly reduced, further decreasing GPU memory usage. Third, the low-rank structure of LoRA often allows for more efficient matrix operations, improving overall computational efficiency. Lastly, in distributed training setups, 

> 1 https://github.com/dstar55/100-words-design-patterns-java. 

11 

_I. Rezgui et al._ 

_Information and Software Technology 197 (2026) 108176_ 



**Fig. 12.** The GPU usage of the fully fine-tuned model vs LoRA based model with respect to the dataset size. 



**Fig. 13.** Inference Time of the LoRA-based model using Aswath’s [34] benchmark for GoF patterns detection. 

the smaller number of trainable parameters reduces communication overhead between GPUs, contributing to faster training and lower resource demands. Storage requirements further highlight the efficiency of LoRA. Since model size scales with the number of trainable parameters, the fully fine-tuned model requires 898.25 MB for storage, whereas the LoRA-adapted model requires only 34.55 MB, making it substantially easier to store, share, and deploy. Fig. 13 illustrates the inference time of the LoRA-based model across Java projects proposed by [34] as a benchmark for evaluating models on GoF pattern detection. As shown in the figure, the LoRA-based model exhibits inference times that are nearly identical across all project sizes and are less than 1 s per project. This behavior can be explained by the fact that LoRA affects only the training phase through low-rank adaptations; at inference time, the adapted weights are merged into the base model without altering the depth or structure of the computation graph. Consequently, LoRA provides substantial gains in training efficiency and storage footprint without introducing additional inference overhead. 

Both models can be executed in CPU-only environments for inference purposes, although inference latency is higher on GPU, as commonly observed for Transformer-based architectures [57]. This makes the proposed approach suitable for integration into continuous integration pipelines or large-scale post-hoc code analysis tools. For interactive or real-time scenarios, GPU acceleration or additional model compression techniques would be required. Overall, the latency–accuracy trade-off in our setting lies between full fine-tuning, which achieves the highest detection accuracy, and LoRA-based fine-tuning, which enables efficient training, reduced storage footprint, and lightweight deployment at the cost of lower detection performance. 

##### _5.4.5. Discussion_ 

To quantitatively assess the trade-offs between full fine-tuning and parameter-efficient fine-tuning via LoRA, we compared both approaches across standard classification metrics. The fully fine-tuned 

model achieved superior results with an F1 score of 0.94 and a precision of 0.95, clearly outperforming the LoRA-based model, which attained an F1 score of 0.85 and a precision of 0.93. While LoRA demonstrated relatively high precision, its recall remained limited, suggesting difficulty in consistently identifying all relevant instances. 

Error analysis revealed that the performance gap is largely attributable to misclassifications between semantically similar design patterns, particularly Abstract Factory and Factory Method. We hypothesize that this limitation arises from LoRA’s low-rank adaptation mechanism, which constrains the effective parameter space and thus reduces the model’s capacity to fully differentiate between fine-grained structural variations, especially when such distinctions rely on deeper representational changes that may not be sufficiently captured without updating the full parameter set. More specifically, GoF design pattern detection is a structurally intensive task that requires modeling long-range dependencies across multiple classes, roles, and interaction pathways. Fully fine-tuning the encoder–decoder architecture allows both the encoder representations and the decoder’s cross-attention mechanisms to adapt jointly to these structural cues. In contrast, LoRA restricts updates to low-rank projections injected into a subset of layers, limiting the model’s ability to reshape internal representations that are critical for capturing subtle role-level distinctions. 

A notable observation in our fine-tuning-based approach is the tendency of the model to hallucinate class labels, particularly under PEFT with LoRA. Unlike a classification head, which predicts from a fixed set of labels, the decoder generates labels token by token. This makes it more flexible, but it can also produce outputs that look correct linguistically while being semantically incorrect. This behavior is reflected in the confusion matrices (Figs. 15 and 14). Indeed, under LoRA fine-tuning, the abstract factory class prediction was scattered across hallucinated labels such as abstract, factory, and abstract method, all of which are compositional fragments of the original class name rather than valid design pattern categories. Similarly, factory method suffers notable leakage into the spurious factory column. These hallucinated labels appear as predicted columns in the LoRA confusion matrix 15 despite having no corresponding ground-truth rows, confirming that the model is generating outputs outside the intended label space. In contrast, as shown in Fig. 14, full fine-tuning substantially suppresses this behavior, as the complete update of all model weights overrides the decoder’s generative priors and enforces tighter alignment with the target vocabulary. Abstract factory, for instance, had no hallucinated predictions. 

In parallel, our comparative analysis of computational overhead demonstrated clear resource savings with LoRA, as illustrated in Fig. 12 and Table 6. This efficiency gain is due to LoRA’s parameter-efficient design, which freezes the base model’s weights and updates only a small low-rank component, lowering gradient storage and computational overhead. 

Given the detection performance gap observed in our experiments, we conclude that the fully fine-tuned model still offers the best results for our goal of achieving high detection accuracy across GoF design patterns, but the LoRA-based model can still perform well while updating less parameters. Based on these results, we selected the fully fine-tuned model as our _𝐷𝑃𝐷𝐴𝑡𝑡_ + detector for comparison with stateof-the-art methods in the next section, addressing the second research question. 

##### _5.5. Comparison with SOTA (RQ2)_ 

In this section, we address the second research question by comparing our approach with related work. As discussed in the previous section, the _𝐷𝑃𝐷𝐴𝑡𝑡_ + detector used for this comparison is based on the full fine-tuning strategy. 

As it is shown in Tables 9, 10, and 11 our proposed approach, DPD _𝐴𝑡𝑡_ +, surpasses existing state-of-the-art methods in detecting GoF design patterns by fully fine-tuning all parameters of a pretrained 

12 

_I. Rezgui et al._ 

_Information and Software Technology 197 (2026) 108176_ 



**Fig. 14.** Confusion matrix for the Full fine-tuning approach. 



**Fig. 15.** Confusion Matrix for the detected patterns by LoRA fine-tuned model. 

13 

_I. Rezgui et al._ 

_Information and Software Technology 197 (2026) 108176_ 

**Table 9** 

Comparison of the _𝐷𝑃𝐷𝐴𝑡𝑡_ + in terms of F1-score per design pattern with the state-of-the-art. 

|Design pattern|FeatureMap [18]|MARPLE-DPD [19]|DPD_𝐹_ [9]|DPD_𝐴𝑡𝑡_ [10]|DPD_𝐴𝑡𝑡_+|
|---|---|---|---|---|---|
|Singleton<br>|0.66|0.72|0.74|0.83|**1.00**|
|Observer|0.49|0.51|0.85|0.89|**1.00**|
|Builder|0.61|0.55|0.83|0.58|**0.97**|
|Abstract Factory|0.52|0.76|0.93|**1.00**|0.88|
|Factory Method|0.55|0.81|0.78|**0.98**|0.87|
|Adapter|0.33|0.82|0.69|**0.88**|0.86|
|Decorator|0.23|0.59|0.78|0.83|**1.00**|
|Visitor|0.65|0.63|0.94|0.94|**1.00**|
|Unknown|0.72|0.54|0.73|0.92|**1.00**|
|Memento|–|–|0.87|0.89|**0.90**|
|Proxy|–|–|0.63|**0.94**|**0.94**|
|Prototype|–|–|0.83|0.95|**1.00**|
|Facade|–|–|0.71|0.87|**0.90**|
|Strategy|–|–|–|0.93|**0.94**|



seq2seq model on the _𝐷𝑃𝐷𝐴𝑡𝑡_ dataset. This comprehensive fine-tuning enables the model to deeply capture the semantic and structural nuances of source code that other approaches often overlook. In contrast, FeatureMap compresses high-dimensional micro-structure vectors into feature maps but suffers from information loss, leading to poor performance on complex patterns such as Decorator and Adapter. Our end-to-end learning strategy preserves rich contextual information, which results in perfect F1-scores on patterns like Singleton, Observer, and Decorator. MARPLE-DPD, while effective at mechanically extracting metrics and basic architectural elements, lacks the capacity for deeper semantic understanding, causing inconsistent detection accuracy, especially on patterns like Builder where it attains only moderate results. The DPD _𝐹_ approach attempts to improve this by constructing semantic representations and applying word-space embeddings through Word2Vec; however, since Word2Vec is pretrained on non-technical corpora and combined with conventional classifiers, it struggles to fully exploit sequence and syntactic information, leading to varied performance across patterns. Similarly, DPD _𝐴𝑡𝑡_ leverages pretrained embeddings and an SVM classifier to enhance detection of patterns like Abstract Factory and Proxy, but its reliance on fixed encoder representations limits its ability to generalize to more complex interactions found in patterns such as Builder. By contrast, DPD _𝐴𝑡𝑡_ + achieves consistently stronger performance across most patterns, including data-sparse cases such as Memento and Strategy where competing approaches lack sufficient coverage. Although DPD _𝐴𝑡𝑡_ slightly surpasses our model on a few patterns like Abstract Factory and Factory Method, the overall results demonstrate that full fine-tuning allows DPD _𝐴𝑡𝑡_ + to better capture structural and semantic relationships, overcoming the constraints of feature compression and static embedding models. 

Notably, the improvement observed with DPD _𝐴𝑡𝑡_ + over the encoderonly baseline DPD _𝐴𝑡𝑡_ highlights the benefit of the Seq2Seq formulation. In this task, the decoder’s contribution does not only stem from its generative capacity, but also from its ability to leverage cross-attention at every decoding step. This mechanism allows the decoder to dynamically attend to different code regions while generating the label token-by-token, providing a richer inductive bias for modeling longrange structural dependencies that are often lost when the encoder is compressed into a single pooled vector. Thus, the decoder primarily enhances structural representation learning rather than generating new variants, though its structured decoding could support variant detection in future extensions. 

We also evaluated the overall performance of our approach compared to state-of-the-art methods across the main families of design patterns, as illustrated in Fig. 16. Our model consistently outperforms previous methods in all three major families creational, structural, and behavioral demonstrating strong generalization and adaptability to different pattern characteristics. While the model experiences relatively lower performance in detecting Abstract Factory and Factory Method, it still maintains superior F1-scores compared to competing approaches, indicating a more robust feature representation and better 



**Fig. 16.** Comparison with state-of-the-art per family of patterns using harmonic mean. 

contextual understanding. The improved performance across behavioral and structural families further highlights the model’s ability to leverage sequential code context and long-range dependencies, surpassing techniques relying on shallow embeddings or manual feature extraction. 

##### **6. Limitations and future work** 

Although the proposed approach presents competitive performance, several limitations open opportunities for future work. 

- Our analysis focused primarily on full fine-tuning and LoRAbased parameter-efficient adaptation. While this provides valuable insight into how LoRA behaves on global, structure-oriented tasks, it does not fully establish whether the observed limitations are specific to LoRA or reflect broader challenges for PEFT in design pattern detection. Evaluating alternative PEFT techniques (such as Prefix-Tuning) would [12] require additional architectural integration, hyperparameter tuning, and extensive re-training to ensure a fair comparison. Conducting such an expanded experimental study represents an important direction for future research. 

- To assess practical generalization, we evaluated the fully finetuned _𝐷𝑃𝐷𝐴𝑡𝑡_ + on an independent dataset by Aswathy et al. [34], in addition to GitHub projects. Despite differing coding conventions, the model successfully detected all unseen instances (Tables 7 and 8), suggesting a reliance on structural and semantic cues rather than stylistic patterns. While these results demonstrate promising cross-project transferability, we recognize that a rigorous leave-one-project-out (LOPO) protocol and further investigation into LoRA’s generalization limits are necessary. Developing a repository-level benchmark for comprehensive LOPO evaluation remains a key objective for future work. 

14 

_I. Rezgui et al._ 

_Information and Software Technology 197 (2026) 108176_ 

**Table 10** 

Comparison of the _𝐷𝑃𝐷𝐴𝑡𝑡_ + in terms of Recall per design pattern with the state-of-the-art. 

|Design pattern|FeatureMap [18]|MARPLE-DPD [19]|DPD_𝐹_ [9]|DPD_𝐴𝑡𝑡_ [10]|DPD_𝐴𝑡𝑡_+|
|---|---|---|---|---|---|
|Singleton<br>|0.67|0.69|0.68|0.79|**1.00**|
|Observer|0.48|0.48|0.90|0.91|**1.00**|
|Builder|0.60|0.51|0.84|0.90|**1.00**|
|Abstract Factory|0.50|0.77|0.92|**0.91**|0.79|
|Factory Method|0.50|0.81|0.82|0.97|**1.00**|
|Adapter|0.32|0.78|0.67|0.73|**0.79**|
|Decorator|0.25|0.58|0.75|0.94|**1.00**|
|Visitor|0.8|0.66|0.92|0.95|**1.00**|
|Unknown|0.79|0.56|0.75|0.82|**1.00**|
|Memento|–|–|0.87|**0.97**|0.93|
|Proxy|–|–|0.63|0.83|**0.88**|
|Prototype|–|–|0.83|0.95|**1.00**|
|Facade|–|–|0.71|0.59|**0.86**|
|Strategy|–|–|–|0.87|**1.00**|



**Table 11** 

Comparison of the _𝐷𝑃𝐷𝐴𝑡𝑡_ + in terms of Precision per design pattern with the state-of-the-art. 

|Design pattern|FeatureMap [18]|MARPLE-DPD [19]|DPD_𝐹_ [9]|DPD_𝐴𝑡𝑡_ [10]|DPD_𝐴𝑡𝑡_+|
|---|---|---|---|---|---|
|Singleton|0.65|0.74|0.82|0.88|**1.00**|
|Observer|0.50|0.53|0.81|0.94|**1.00**|
|Builder|0.62|0.59|0.83|0.76|**0.94**|
|Abstract Factory|0.56|0.76|0.93|0.94|**1.00**|
|Factory Method|0.61|0.83|0.74|**0.90**|0.77|
|Adapter|0.35|0.86|0.72|0.80|**0.95**|
|Decorator|0.21|0.60|0.81|0.81|**1.00**|
|Visitor|0.55|0.60|0.97|0.78|**1.00**|
|Unknown|0.70|0.51|0.71|0.64|**1.00**|
|Memento|–|–|**0.90**|0.87|0.88|
|Proxy|–|–|0.69|0.97|**1.00**|
|Prototype|–|–|0.86|0.94|**1.00**|
|Facade|–|–|0.68|0.90|**0.95**|
|Strategy|–|–|–|**1.00**|0.88|



- While our current study establishes a robust baseline for parameter-efficient design pattern detection, several avenues for further exploration remain. Specifically, we intend to investigate hybrid fine-tuning strategies, such as combining a fully fine-tuned encoder with a LoRA-adapted decoder. While such configurations could potentially offer a unique trade-off between structural understanding and generative flexibility, they require substantial architectural modifications and specialized optimization schedules that were beyond the scope of this work. Our primary objective in this research was to provide the first comprehensive analysis of the impact of full Seq2Seq architectures and LoRA finetuning specifically on GoF pattern detection. Future iterations of this work will build upon these foundational results to explore whether hybrid parameter-efficient methods can further push the boundaries of cross-project generalization in software engineering tasks. 

##### **7. Threats to validity** 

##### _Construct validity._ 

- Pattern coverage: Our study focuses on 13 GoF design patterns that are frequently reported in prior empirical studies and sufficiently represented in publicly available repositories. While these patterns cover all three GoF categories (Creational, Structural, Behavioral), they do not exhaust the full catalog of 23 patterns. As a result, the findings may not fully capture the diversity of pattern usage in all real-world systems. Extending the dataset to additional patterns remains an important direction for future work. 

- Class-level granularity: We perform detection at the class level, as it represents the lowest granularity that may capture a complete design pattern. While some GoF patterns involve collaborations across multiple classes, class-level analysis provides a practical 

and consistent unit of analysis that is well-established in prior work. We acknowledge that boundary cases may arise, and extending to multi-class detection remains a valuable direction for future research. 

- Evaluation metrics: Model performance is assessed using Precision, Recall, and F1-score, which are standard metrics for multiclass classification. Per-class results are reported alongside weighted averages to allow pattern-specific performance to be examined, particularly for structurally related patterns such as Factory Method and Abstract Factory. 

- Real-world representativeness: To further validate our model beyond standard metrics, we tested it on a set of real-world projects. The model correctly identified all 13 design patterns across these projects, providing additional confidence in the reliability of the reported results beyond what the held-out test set alone can demonstrate. 

##### _Internal validity._ 

- Dataset construction and annotation bias: All instances were manually verified by domain experts (faculty members and researchers) and sourced from repositories explicitly documenting pattern usage. To further support annotation consistency, we grounded the baseline in the well-established DPD_F corpus, which was originally labeled by at least three annotators with expertise in Java development and design patterns. 

- Hyperparameter sensitivity: The performance of both fine-tuning strategies (full fine-tuning and LoRA) may be influenced by hyperparameter choices such as learning rate, number of training epochs, batch size, etc. To promote robustness, we followed hyperparameter ranges established in prior CodeT5+ work and conducted preliminary tuning on a held-out validation set, with the final configuration fixed prior to evaluation. 

15 

_I. Rezgui et al._ 

_Information and Software Technology 197 (2026) 108176_ 

- Data leakage: Since CodeT5+ was pre-trained on large public code corpora, there is a possibility that some evaluation instances appeared in pre-training data. To reduce this risk, expansion instances were sourced from repositories identified during our collection phase, and we included external examples from prior work as an additional out-of-distribution probe. 

- Pipeline correctness: Preprocessing outputs and metric computations were cross-validated against manually inspected examples. Our code and datasets are made publicly available to support independent replication. 

_External validity._ Our experiments are conducted exclusively on Java source code, which may limit generalization to other object-oriented languages such as C++ or Python. Moreover, data collection from GitHub repositories introduces a selection bias toward welldocumented and popular projects. To assess generalization beyond the curated dataset, we evaluated the model on representative external examples from prior work, but broader cross-language and cross-domain validation remains future work. 

##### **8. Conclusion** 

In this paper, we introduced _𝐷𝑃𝐷𝐴𝑡𝑡_ +, an end-to-end Seq2Seq framework for detecting GoF design patterns from Java source code. By casting the task as sequence generation rather than simple classification, our model leverages the encoder–decoder architecture of CodeT5+ to capture both structural and semantic dependencies across classes. This enables more expressive architectural reasoning compared to traditional feature-engineering pipelines or encoder-only approaches. 

We fine-tuned CodeT5+ using two strategies, full fine-tuning and parameter-efficient fine-tuning with LoRA and provided a detailed comparison of their performance and computational characteristics. Our experiments show that full fine-tuning achieves the highest detection accuracy, while LoRA offers substantial efficiency benefits but faces challenges with structurally similar patterns. We also offer the DPD_Att dataset which extends existing datasets by adding new pattern instances, improving class balance, and performing expert validation to ensure reproducibility. This dataset supports the empirical evaluation of the proposed framework and contributes to the broader research community. Our empirical evaluation demonstrates that the proposed model outperforms existing state-of-the-art approaches, achieving 94% accuracy across 13 GoF patterns and exhibiting particularly strong performance on patterns with consistent structural signatures. Overall, this work provides: (i) a Seq2Seq formulation for design pattern detection, (ii) a comprehensive study of full versus parameter-efficient fine-tuning for structural code tasks, and (iii) a curated dataset for reproducible evaluation. 

As future work, we plan to investigate alternative PEFT methods such as Adapters and Prefix-Tuning to determine whether the limitations observed with LoRA are method-specific or inherent to parameter-efficient strategies in global structural reasoning tasks. Additionally, a promising avenue for further research involves employing feature location techniques [58] to not only recognize design patterns in code but also identify the specific features that characterize them, thus enhancing our understanding of the underlying structures and behaviors. 

##### **CRediT authorship contribution statement** 

**Ilyes Rezgui:** Writing – review & editing, Writing – original draft, Validation, Software, Methodology, Conceptualization. **Rania Mzid:** Writing – review & editing, Writing – original draft, Supervision, Methodology, Conceptualization. **Tewfik Ziadi:** Writing – review & editing, Supervision, Conceptualization. 

##### **Declaration of competing interest** 

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper. 

##### **Data availability** 

Data will be made available on request. 

##### **References** 

- [1] M. Richards, N. Ford, Fundamentals of Software Architecture: An Engineering Approach, O’Reilly Media, 2020. 

- [2] J. Dong, Y. Zhao, Y. Sun, A matrix-based approach to recovering design patterns, IEEE Trans. Syst. Man, Cybern. A: Syst. Humans 39 (6) (2009) 1271–1282. 

- [3] G. Rasool, I. Philippow, P. Mäder, Design pattern recovery based on annotations, Adv. Eng. Softw. 41 (4) (2010) 519–526. 

- [4] A.K. Dwivedi, A. Tirkey, S.K. Rath, Applying software metrics for the mining of design pattern, in: 2016 IEEE Uttar Pradesh Section International Conference on Electrical, Computer and Electronics Engineering, UPCON, IEEE, 2016, pp. 426–431. 

- [5] I. Issaoui, N. Bouassida, H. Ben-Abdallah, Using metric-based filtering to improve design pattern detection approaches, Innov. Syst. Softw. Eng. 11 (2015) 39–53. 

- [6] A. Nacef, S. Bahroun, A. Khalfallah, S.B. Ahmed, Features and supervised machine learning based method for singleton design pattern variants detection, in: H. Kaindl, M. Mannion, L.A. Maciaszek (Eds.), Proceedings of the 18th International Conference on Evaluation of Novel Approaches to Software Engineering, ENASE 2023, SCITEPRESS, 2023, pp. 226–237. 

- [7] M. Kouli, A. Rasoolzadegan, A feature-based method for detecting design patterns in source code, Symmetry 14 (7) (2022) 1491. 

- [8] K.W. Church, Word2Vec, Nat. Lang. Eng. 23 (1) (2017) 155–162. 

- [9] N. Nazar, A. Aleti, Y. Zheng, Feature-based software design pattern detection, J. Syst. Softw. 185 (2022) 111179. 

- [10] R. Mzid, I. Rezgui, T. Ziadi, Attention-based method for design pattern detection, in: European Conference on Software Architecture, Springer, 2024, pp. 86–101. 

- [11] R. Cao, L. Bao, K. Zhao, P. Zhangsun, ETune: Efficient configuration tuning for big-data software systems via configuration space reduction, J. Syst. Softw. 209 (2024) 111936. 

- [12] Z. Han, C. Gao, J. Liu, J. Zhang, S.Q. Zhang, Parameter-efficient fine-tuning for large models: A comprehensive survey, 2024, arXiv preprint arXiv:2403.14608. 

- [13] C. Alexander, A Pattern Language: Towns, Buildings, Construction, Oxford university press, 1977. 

- [14] E. Gamma, R. Helm, R. Johnson, J. Vlissides, Design Patterns: Elements of Reusable Object-Oriented Software, Pearson Deutschland GmbH, 1995. 

- [15] N. Bozorgvar, A. Rasoolzadegan, A. Harati, Probabilistic detection of GoF design patterns, J. Supercomput. 79 (2) (2023) 1654–1682. 

- [16] S. Jeanmart, Y.-G. Gueheneuc, H. Sahraoui, N. Habra, Impact of the visitor pattern on program comprehension and maintenance, in: 2009 3rd International Symposium on Empirical Software Engineering and Measurement, IEEE, 2009, pp. 69–78. 

- [17] A. Ampatzoglou, A. Chatzigeorgiou, S. Charalampidou, P. Avgeriou, The effect of GoF design patterns on stability: A case study, IEEE Trans. Softw. Eng. 41 (8) (2015) 781–802. 

- [18] H. Thaller, L. Linsbauer, A. Egyed, Feature maps: A comprehensible software representation for design pattern detection, in: 2019 IEEE 26th International Conference on Software Analysis, Evolution and Reengineering, SANER, IEEE, 2019, pp. 207–217. 

- [19] M. Zanoni, F.A. Fontana, F. Stella, On applying machine learning techniques for design pattern detection, J. Syst. Softw. 103 (2015) 102–117. 

- [20] L. Chen, J. Zheng, H. Okamura, T. Dohi, Software reliability prediction through encoder-decoder recurrent neural networks, Int. J. Math. Eng. Manag. Sci. 7 (3) (2022) 325. 

- [21] S. Hariharan, Y.A. Jerusha, G. Suganeshwari, S.S. Ibrahim, U. Tupakula, V. Varadharajan, A hybrid deep learning model for network intrusion detection system using Seq2Seq and ConvLSTM-subnets, IEEE Access (2025). 

- [22] P. Keller, A.K. Kaboré, L. Plein, J. Klein, Y. Le Traon, T.F. Bissyande, What you see is what it means! semantic representation learning of code based on visualization and transfer learning, ACM Trans. Softw. Eng. Methodol. (TOSEM) 31 (2) (2021) 1–34. 

- [23] A. Asgarian, P. Sobhani, J.C. Zhang, M. Mihailescu, A. Sibilia, A.B. Ashraf, B. Taati, A hybrid instance-based transfer learning method, 2018, arXiv preprint arXiv:1812.01063. 

- [24] J. Zhao, S. Shetty, J.W. Pan, Feature-based transfer learning for network security, in: MILCOM 2017-2017 IEEE Military Communications Conference, MILCOM, IEEE, 2017, pp. 17–22. 

16 

_Information and Software Technology 197 (2026) 108176_ 

###### _I. Rezgui et al._ 

- [25] Y. He, H. Tang, Y. Ren, A. Kumar, A deep multi-signal fusion adversarial model based transfer learning and residual network for axial piston pump fault diagnosis, Measurement 192 (2022) 110889. 

- [26] M. Iman, H.R. Arabnia, K. Rasheed, A review of deep transfer learning and recent advancements, Technologies 11 (2) (2023) 40. 

- [27] J. Seemann, J.W. von Gudenberg, Pattern-based design recovery of java software, ACM SIGSOFT Softw. Eng. Notes 23 (6) (1998) 10–16. 

- [28] V.D. Blondel, A. Gajardo, M. Heymans, P. Senellart, P. Van Dooren, A measure of similarity between graph vertices: Applications to synonym extraction and web searching, SIAM Rev. 46 (4) (2004) 647–666. 

- [29] N. Tsantalis, A. Chatzigeorgiou, G. Stephanides, S.T. Halkidis, Design pattern detection using similarity scoring, IEEE Trans. Softw. Eng. 32 (11) (2006) 896–909. 

- [30] J. Dong, Y. Sun, Y. Zhao, Design pattern detection by template matching, in: Proceedings of the 2008 ACM Symposium on Applied Computing, 2008, pp. 765–769. 

- [31] J. Singh, M. Gupta, Design pattern detection using dpdetect algorithm, Int. J. Innov. Technol. Explor. Eng. (IJITEE) 8 (7) (2019). 

- [32] S. Wenzel, U. Kelter, Model-driven design pattern detection using difference calculation, in: Workshop on Pattern Detection for Reverse Engineering, Citeseer, 2006. 

- [33] M.L. Bernardi, M. Cimitile, G. Di Lucca, Design pattern detection using a DSL-driven graph matching approach, J. Softw.: Evol. Process. 26 (12) (2014) 1233–1266. 

- [34] A. Mohan, S. Jayaraman, B. Jayaraman, A declarative approach to detecting design patterns from Java execution traces and source code, Inf. Softw. Technol. 171 (2024) 107457. 

- [35] Z. Shahbazi, A. Rasoolzadegan, Z. Purfallah, S. Jafari Horestani, A new method for detecting various variants of GoF design patterns using conceptual signatures, Softw. Qual. J. 30 (3) (2022) 651–686. 

- [36] S. Zaharia, T. Rebedea, S. Trausan-Matu, Machine learning-based security pattern recognition techniques for code developers, Appl. Sci. 12 (23) (2022) 12463. 

- [37] S. Komolov, G. Dlamini, S. Megha, M. Mazzara, Towards predicting architectural design patterns: A machine learning approach, Computers 11 (10) (2022) 151. 

- [38] S. Dewangan, R.S. Rao, Design pattern detection by using correlation feature selection technique, in: 2022 IEEE 11th International Conference on Communication Systems and Network Technologies, CSNT, IEEE, 2022, pp. 641–645. 

- [39] X. Mo, H. Chen, A new classification framework for high-dimensional data, 2023, arXiv preprint arXiv:2306.15199. 

- [40] S. Ghanbarzadeh, H. Palangi, Y. Huang, R.C. Moreno, H. Khanpour, Improving pre-trained language models’ generalization, 2023, arXiv preprint arXiv:2307. 10457. 

- [41] A. Silva, S. Fang, M. Monperrus, Repairllama: Efficient representations and fine-tuned adapters for program repair, IEEE Trans. Softw. Eng. (2025). 

   - [43] J. Hoffmann, D. Frister, Generating software tests for mobile applications using fine-tuned large language models, in: Proceedings of the 5th ACM/IEEE International Conference on Automation of Software Test, AST 2024, 2024, pp. 76–77. 

   - [44] M. Setak, P. Madani, Fine-tuning llms for code mutation: A new era of cyber threats, in: 2024 IEEE 6th International Conference on Trust, Privacy and Security in Intelligent Systems, and Applications, TPS-ISA, IEEE, 2024, pp. 313–321. 

   - [45] M. Budnikov, A. Bykova, I.P. Yamshchikov, Generalization potential of large language models, Neural Comput. Appl. 37 (4) (2025) 1973–1997. 

   - [46] X. Hou, Y. Zhao, Y. Liu, Z. Yang, K. Wang, L. Li, X. Luo, D. Lo, J. Grundy, H. Wang, Large language models for software engineering: A systematic literature review, ACM Trans. Softw. Eng. Methodol. 33 (8) (2024) 1–79. 

   - [47] Y.-G. Guéhéneuc, P-mart: Pattern-like micro architecture repository, in: Proceedings of the 1st Europlop Focus Group on Pattern Repositorie, ACM, 2007, pp. 1–3. 

   - [48] B. Gelman, B. Obayomi, J. Moore, D. Slater, Source code analysis dataset, Data Brief 27 (2019) 104712. 

   - [49] S. Jüngling, M. Peraic, C. Zhu, Using the strategy design pattern for hybrid AI system design, in: AAAI Spring Symposium: MAKE, 2022. 

   - [50] M. Take, S. Alpers, C. Becker, C. Schreiber, A. Oberweis, Software design patterns for AI-systems, in: EMISA, 2021, pp. 30–35. 

   - [51] Y. Wang, H. Le, A.D. Gotmare, N.D. Bui, J. Li, S.C. Hoi, Codet5+: Open code large language models for code understanding and generation, 2023, arXiv preprint arXiv:2305.07922. 

   - [52] Y. Wang, W. Wang, S. Joty, S.C. Hoi, Codet5: Identifier-aware unified pre-trained encoder-decoder models for code understanding and generation, 2021, arXiv preprint arXiv:2109.00859. 

   - [53] A. Radford, J. Wu, R. Child, D. Luan, D. Amodei, I. Sutskever, et al., Language models are unsupervised multitask learners, OpenAI Blog 1 (8) (2019) 9. 

   - [54] A. Davila, J. Colan, Y. Hasegawa, Comparison of fine-tuning strategies for transfer learning in medical image classification, Image Vis. Comput. 146 (2024) 105012. 

   - [55] S. Nursapa, A. Samuilova, A. Bucaioni, P.T. Nguyen, ROSE: Transformer-based refactoring recommendation for architectural smells, 2025, arXiv preprint arXiv: 2507.12561. 

   - [56] S. Greiner, N. Bühlmann, M. Ohrndorf, C. Tsigkanos, O. Nierstrasz, T. Kehrer, Automated generation of code contracts: Generative AI to the rescue? in: Proceedings of the 23rd ACM SIGPLAN International Conference on Generative Programming: Concepts and Experiences, 2024, pp. 1–14. 

   - [57] C. Raffel, N. Shazeer, A. Roberts, K. Lee, S. Narang, M. Matena, Y. Zhou, W. Li, P.J. Liu, Exploring the limits of transfer learning with a unified text-to-text transformer, J. Mach. Learn. Res. 21 (140) (2020) 1–67. 

   - [58] L. Di Grazia, M. Pradel, Code search: A survey of techniques for finding code, ACM Comput. Surv. 55 (11) (2023) 1–31. 

- [42] M. Nashaat, J. Miller, Towards efficient fine-tuning of language models with organizational data for automated software review, IEEE Trans. Softw. Eng. (2024). 

17