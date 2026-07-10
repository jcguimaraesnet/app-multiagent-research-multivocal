Journal of Computer Languages 88 (2026) 101403 



Contents lists available at ScienceDirect 

# Journal of Computer Languages 

journal homepage: www.elsevier.com/locate/cola 



## VC-AWG: A Vibe Coding–based method for Automated Website Generation from heterogeneous artifacts 

Hoang-Viet Tran<sup>∗</sup> , Thi-Thanh-Truc Dang, Duc-Anh Nguyen, Pham Ngoc Hung 

_VNU University of Engineering and Technology, E3 Building, 144 Xuan Thuy st. Cau Giay Ward. Hanoi, Viet Nam_ 

### A R T I C L E I N F O 

### A B S T R A C T 

> _Keywords:_ Vibe coding is an emerging software engineering paradigm in which developers express high-level intent Vibe coding while large language models (LLMs) generate code. This paper proposes VC-AWG (Vibe Coding-based Source code generation Automated Website Generation), a method for systematically generating complete website functionalities Website generation from heterogeneous artifacts, including use case specifications, Figma-based user interface (UI) designs, API Use case specification UIAPIdesigncontract contracts,specificationsa predefinedand design-relatedcodebase,inputsand coding— suchrules.as layout,VC-AWGcolor,leveragesstyle, andLLMs’linksability— andto interpretto producestructuredcode in Codebase a controlled format. The method adopts a two-phase workflow: first, constructing structured coding prompts Coding rules from use cases, UI designs, and API contracts; second, synthesizing source code based on these prompts, the existing codebase, and coding rules. Experiments on a Personal Financial Management website show that VCAWG reduces development time to an average of 21.1 min per use case, achieving a 97.3% reduction compared to manual programming, demonstrating its effectiveness and scalability. 

#### **1. Introduction** 

Automation in software engineering has long been recognized as a key driver for improving productivity, reducing development costs, and accelerating time-to-market. A large body of research has explored the automation of various stages in the software lifecycle, reflecting its strategic importance in modern software engineering practices [1–6]. 

Existing approaches to automated code generation span multiple directions, including transformations from requirements, design models, and structured specifications. Prior studies have investigated automatic code generation from natural-language use cases and domain models [1], model-driven and metadata-based techniques [3–5], and design-to-code transformations [7–12]. While these methods have demonstrated effectiveness in specific domains, they typically rely on formalized inputs, expert-driven modeling, or deterministic transformations, which limit their flexibility and accessibility. Moreover, many approaches focus on isolated artifacts and struggle to generate complete, production-ready systems from heterogeneous inputs. A detailed discussion of these approaches is provided in Section 3. 

Recent advances in artificial intelligence, particularly large language models (LLMs), have significantly reshaped the landscape of code generation. Empirical studies and surveys show that LLMs exhibit strong capabilities in generating source code from natural language and structured inputs, while also highlighting challenges in reliability 

and scalability [13–15]. Building on these advances, the concept of _vibe coding_ has recently emerged as a paradigm in which developers express high-level intent and interact iteratively with AI systems to generate code. Prior work highlights both its potential and limitations, including issues related to constraint handling, reliability, accessibility, and production readiness [16–22]. Despite its promise, vibe coding still lacks systematic workflows and structured mechanisms to integrate diverse development artifacts in a controlled and scalable manner. 

To address these limitations, this paper proposes VC-AWG (Vibe Coding-based Automated Website Generation), a method for systematically generating complete website functionalities from heterogeneous artifacts, including use case specifications, Figma-based UI designs, API contracts, a predefined codebase, and coding rules. VC-AWG leverages the capability of LLMs to interpret structured specifications and designrelated inputs — such as layout, color, style, and links — to generate code in predefined formats. 

The proposed method adopts a two-phase workflow: (i) constructing structured coding prompts from use case specifications, UI designs, and API contracts; and (ii) generating source code based on these prompts, the predefined codebase, and coding rules. By explicitly separating prompt construction from code generation, VC-AWG improves controllability, consistency, and alignment with developer intent. The prompts 

> ∗ Corresponding author. 

_E-mail addresses:_ thv@vnu.edu.vn (H.-V. Tran), 21020414@vnu.edu.vn (T.-T.-T. Dang), nguyenducanh@vnu.edu.vn (D.-A. Nguyen), hungpn@vnu.edu.vn (P.N. Hung). 

https://doi.org/10.1016/j.cola.2026.101403 Received 23 February 2026; Received in revised form 21 April 2026; Accepted 11 May 2026 Available online 21 May 2026 

2590-1184/© 2026 Elsevier Ltd. All rights are reserved, including those for text and data mining, AI training, and similar technologies. 

_H.-V. Tran et al._ 

_Journal of Computer Languages 88 (2026) 101403_ 

capture key aspects of software functionality, including backend services, UI structure, application logic and state management, and error handling and testing, enabling more accurate code synthesis. 

We evaluate VC-AWG on a Personal Financial Management website, demonstrating that it reduces development time to an average of 21.1 min per use case, achieving a 97.3% reduction compared to manual development. These results highlight the effectiveness and scalability of the proposed approach. 

The main contributions of this paper are as follows: 

- A novel Vibe Coding-based method, VC-AWG, for automated website generation from heterogeneous software artifacts, enabling the integration of use case specifications, UI designs, API contracts, codebases, and coding rules into a unified generation process. 

- A two-phase workflow that explicitly separates prompt construction from code generation, improving controllability, consistency, and alignment with developer intent in LLM-based software development. 

- A structured coding prompt design as an intermediate representation that systematically bridges heterogeneous artifacts and source code, capturing key aspects such as backend services, UI structure, application logic, state management, and error handling. 

The rest of this paper is organized as follows. Section 2 presents some background concepts that will be used in this paper. Related works to the VC-AWG method are shown in Section 3. Details of the VC-AWG method are presented in Section 4. The experimental setup details, results, and related discussions are shown in Section 5. Finally, we conclude the paper in Section 6. 

#### **2. Background** 

In this section, we present some important concepts that will be used in this paper. 

_Vibe Coding._ Vibe Coding<sup>1</sup> is an emerging software engineering paradigm that investigates how large language models generate source code from high-level intent and descriptive specifications. Instead of requiring detailed implementation definitions, it emphasizes expressing system purpose, functional expectations, and logical structure in an abstract, human-centered manner. This approach aims to bridge the gap between problem understanding and program implementation, promoting intent-driven development that tightly integrates human reasoning with AI-based code generation, while raising critical challenges related to controllability, correctness, and reliability of generated software. 

_Prompt._ In Vibe Coding and AI-assisted software engineering, a prompt is a structured or semi-structured input that conveys developer intent to guide large language models in code generation. It encapsulates functional goals, constraints, assumptions, and expected behaviors, serving as an interface between human reasoning and machine-generated implementations. Beyond simple natural language instructions, prompts embody deliberate design choices that shape the structure and quality of generated code. As a core mechanism in Vibe Coding, prompts directly influence correctness, consistency, and reproducibility, making them a key focus of prompt engineering and software engineering research. 

_AI-powered IDEs._ AI-powered Integrated Development Environments (IDEs), such as Visual Studio Code<sup>2</sup> with AI extensions, Cursor,<sup>3</sup> and Google Antigravity,<sup>4</sup> integrate large language models directly into the software development workflow. These environments extend traditional IDEs with intelligent code completion, generation, refactoring, and contextual explanations aligned with developer intent. By enabling continuous interaction between developers and AI models, they support more efficient and exploratory development. In the context of Vibe Coding, AI-powered IDEs operationalize intent-driven development while raising challenges related to developer reliance, code comprehension, and governance of AI-generated artifacts. 

#### **3. Related works** 

_From requirements to source code generation._ Automated source code generation has been widely investigated as a means to reduce manual effort and improve software development productivity [1–6]. Existing approaches range from transforming natural-language requirements and restricted specifications into executable prototypes [1,2] to pattern, metadata-, and model-driven techniques that emphasize reuse, consistency, and automation efficiency [3–5]. Recent analytical studies further highlight the effectiveness of model-based generation in lowcode platforms [23] and identify dominant paradigms, validation gaps, and limited multilingual support in current research [6]. 

_From design to source code generation._ Research on automating the transition from software design to source code generation has a long history, aiming to reduce manual effort while improving consistency and software quality [7–12,24]. Early studies focused on generating code from design patterns and high-level architectural specifications [7,8], while subsequent work emphasized compiler techniques, domain-specific optimizations, and embedded systems synthesis [9, 12]. Model-driven software development later became a dominant paradigm, enabling systematic transformations from formal models to executable code with increasing attention to correctness and validation [10,11]. More recently, AI-driven approaches have explored the use of learning-based techniques to bridge design artifacts and web application code [24]. 

_AI-based source code generation._ Recent research has increasingly explored the application of artificial intelligence to automatic source code generation, examining both technical capabilities and implications for developer productivity, trust, and software quality [13–15, 25,26]. Empirical studies have evaluated AI-assisted code generation within IDEs [26], assessed the performance and limitations of large language models on programming benchmarks [13], and provided systematic surveys and comparative reviews of deep learning-based techniques across the software lifecycle [14,15]. Complementary work has also emphasized developer trust and usability as critical factors for adoption [25]. 

_Vibe coding._ Vibe coding has recently emerged as an AI-assisted programming paradigm, with a growing body of research examining its reliability, accessibility, and domain-specific applications [16,17,19– 22]. Prior studies highlight challenges in constraint management and reliability [16], explore accessibility and support for non-programmers and novice developers [17,18,21], and demonstrate the feasibility of vibe coding in production-scale and domain-specific systems [19,20, 22]. 

In contrast to prior approaches that rely on isolated artifacts, deterministic transformations, or IDE-level assistance, this paper proposes VC-AWG, a Vibe Coding-based Automated Website Generation 

- 2 https://code.visualstudio.com/. 

> 3 https://cursor.com/. 

> 4 https://antigravity.google/. 

> 1 https://x.com/karpathy/status/1886192184808149383. 

2 

_H.-V. Tran et al._ 

_Journal of Computer Languages 88 (2026) 101403_ 



**Fig. 1.** An overview of the VC-AWG method. 

method that places large language models (LLMs) at the core of reasoning and synthesis. VC-AWG targets end-to-end generation of complete website functionality by unifying heterogeneous artifacts, including use case specifications, Figma-based UI designs, API contracts, existing codebases, and explicit coding rules. A key distinction is its two-phase workflow, which separates prompt construction from code generation, enabling intent-aware reasoning prior to implementation. This design improves controllability, consistency, and alignment with developer intent, and advances vibe coding toward a systematic, production-oriented software engineering workflow beyond traditional model-driven and conversational approaches. 

#### **4. The VC-AWG method** 

#### _4.1. An overview of the VC-AWG_ 

The VC-AWG method receives use case specifications, UI/UX designs developed in Figma, API contracts, the existing project codebase, and predefined coding rules as inputs, and automatically generates the corresponding functionalities’ source code. The method is organized into two successive phases: (i) coding prompt generation and (ii) source code generation. A high-level overview of the VC-AWG method is illustrated in Fig. 1. 

- Phase 1 (Generate coding prompts): Phase 1 analyzes and transforms heterogeneous artifacts — such as use case specifications, Figma UI/UX designs, prompt templates, and API contracts — into a unified, structured representation. The goal is to generate standardized coding prompts that precisely capture business logic, workflows, data constraints, and UI requirements, thereby reducing ambiguity and errors in subsequent automated code generation. 

- Phase 2 (Generate source code): This phase transforms coding prompts into executable source code by leveraging prompt semantics and contextual knowledge from the existing codebase, thereby ensuring compliance with project structure, naming conventions, and architectural constraints. Using the surrounding context, the code generation environment (e.g., Cursor) performs a holistic analysis to determine which components should be created or modified and integrates new code at appropriate locations while preserving layered architecture, modularity, and consistent error handling. Phase 2 further incorporates an automated selfvalidation and error-correction mechanism that iteratively checks syntactic, logical, data, and architectural consistency. The result 

is a deployable set of complete or incrementally updated source code artifacts ready for compilation or execution. 

Owing to its two-phase architecture, the proposed method enhances accuracy, consistency, and deployment efficiency while reducing errors and development risks. Phase 1 standardizes business requirements and user interfaces, and Phase 2 translates them into validated, architecture-compliant source code, forming an integrated end-to-end workflow that supports scalability, maintainability, and developer focus on high-level design. 

#### _4.2. Phase 1: Generation of the coding prompt_ 

The first phase focuses on transforming business specification artifacts into a structured coding prompt suitable for code generation environments such as Cursor. As a foundational stage, it bridges business requirements and implementation, directly influencing the correctness, performance, and maintainability of the source code produced in Phase 2. 

#### _4.2.1. The inputs of Phase 1_ 

To ensure accurate and comprehensive reasoning, the system simultaneously processes four distinct input streams, thereby mitigating contextual blind spots commonly associated with reliance on a single information source. 

_Use case specification._ The use case specification is a core artifact that formalizes system business logic by defining actors, behaviors, conditions, and outcomes. In automated code generation, it functions as a set of behavioral constraints enabling direct transformation into executable code, improving requirement–implementation consistency, reducing errors, shortening development cycles, and supporting testing, maintenance, and extension. The component list of a use case specification is presented in Table 1. 

For illustration, a concrete example of a use case specification and its transformation into a coding prompt is provided in Section 5.4. 

_UI/UX design in Figma._ UI design artifacts created using Figma provide essential visual and interaction context beyond use case specifications, including layout, components, states, and navigation flows. By analyzing Figma screens, the LLM decomposes interfaces into atomic elements and their display states, and maps interaction semantics (e.g., _onClick_ , _onSubmit_ , _onScroll_ ) to code-level handlers, thereby improving the accuracy, completeness, and consistency of generated source code and user experience modeling. A concrete example illustrating how Figmabased UI designs are interpreted and mapped to code-level structures is presented in Section 5.4. 

3 

_H.-V. Tran et al._ 

_Journal of Computer Languages 88 (2026) 101403_ 

**Table 1** 

Use case’s key information. 

|Component|Description|
|---|---|
|Actor|Identify the objects that interact with the system,<br>for example: User, Admin, System.|
|Main flow|It describes the standard sequence for completing<br>a function, providing the basic logic for the system.|
|Alternative &<br>exception<br>flows|This includes branching scenarios such as<br>connection loss and corrupted data, helping to<br>make the generated code fault-tolerant.|
|Pre and Post<br>conditions|Determine the system state before and after<br>execution, supporting the generation of validation<br>code and state management.|



_API contract._ In decoupled backend architectures, the API specification functions as a formal contract defining endpoints, data structures, interaction semantics, and error constraints. By providing complete and unambiguous details, it enables accurate API invocation, response handling, and error management, ensuring frontend–backend consistency and enhancing the stability, scalability, and reliability of the resulting system. 

_Standardized template prompts._ To ensure structural consistency and minimize conflicts among coding prompts, the information synthesis phase employs a fixed prompt template. The template defines mandatory elements, including functional objectives, target technology stack, programming standards, API requirements, validation and errorhandling rules, scalability considerations, and the expected output format for the code generation environment. 

A well-designed prompt template serves as a unifying mechanism that enforces structural and stylistic consistency across all coding prompts, thereby facilitating accurate interpretation by the code generation model. Accordingly, the templates are systematically organized into four primary prompt groups based on their roles and purposes. 

#### • Prompt A (Backend API Service): 

During backend development, the focus is on building middleware services and data repositories to handle API requests, data models, and business logic. Clear separation between data access and logic enhances scalability, maintainability, and testability, while server-side processing ensures robustness before responses are delivered to client applications. The detailed structure of Prompt A is presented in Listing 1. 

- 1 <mark>1. Prompt A: Backend Code Generation (NestJS Service/Controller)</mark> 

- 2 <mark>Objective: Build an API service, business logic, and server-side error handling.</mark> 

- 3 <mark>Create endpoint [API Method] [API Path] in [Controller Name] NestJS. This endpoint MUST be protected by JwtAuthGuard. REQUEST FORMAT: [Sample Request Body or Sample Query Parameters]. [Service Name] The service must write the main processing method. Logic: [Detailed description of the business steps, including validation].</mark> 

- 4 <mark>SUCCESSFUL RESPONSE FORMAT: [Sample Response successfully].</mark> 

- 5 <mark>Error Handling: If [Error Scenario occurs], throw [NestJS Exception Type] with error JSON: [Describe the correct error response].</mark> 

Listing 1: Detailed structure of Prompt A. 

- Prompt B (Structure and User Interface): 

The UI design phase defines the foundational structure of interface components and enforces standardized project organization, enabling default component initialization and future backend integration. Clear separation of screens, components, styles, and shared resources, together with consistent visual design principles, improves readability, maintainability, and extensibility and ensures a coherent user experience. The detailed structure of Prompt B is presented in Listing 2. 

- 1 <mark>2. Prompt B: Frontend Code Generation (React Component & UI/MCP)</mark> 

- 2 <mark>Objective: Build a user interface according to the Figma design.</mark> 

- 3 <mark>Create a component [FE Component Name] using React TypeScript and Tailwind CSS. This component MUST display [Description of main UI elements]. STRICTLY use the interface design from Figma MCP at the link: [Figma Link/Selection ID]. Ensure the layout and colors match the design 100%.</mark> 

Listing 2: Detailed structure of Prompt B. 

#### • Prompt C (Main Logic and State Management): 

After establishing the UI foundation, this phase integrates backend data into the presentation layer and manages application state to ensure consistency across workflows. Explicit handling of UI states, structured state management, and systematic validation and business rule enforcement enhance data accuracy, reliability, and synchronization between the interface and backend services. The detailed structure of Prompt C is presented in Listing 3. 

- 1 <mark>3. Prompt C: Generating Frontend Logic Code (State \& API Connections)</mark> 

- 2 <mark>Objective: Connect the interface to the API and successfully implement the user experience flow.</mark> 

- 3 <mark>Continue working on [FE Component Name]. Add the necessary state variables. Implement the asynchronous function [Processing Function Name] to send requests to the API</mark> 

- 4 <mark>[Method and path created in Prompt A]. REQUEST CONTENT: Prepare the payload based on [The given Sample Request Body] from the Form state. If successful, use the structure [The successful Sample Response] to execute [Describe the following successful steps, e.g., Save accessToken, Navigate, Update state].</mark> 

Listing 3: Detailed structure of Prompt C. 

- Prompt D (Error Handling and Testing): 

To ensure reliable operation, error handling and testing are performed alongside core logic implementation. API calls are encapsulated within structured exception mechanisms to manage failures systematically, while concise, user-oriented error messages are delivered through appropriate interface elements to preserve user experience. The detailed structure of Prompt D is presented in Listing 4. 

- 1 <mark>4. Prompt D: Exception Handling (Client-side Validation & Error Handling)</mark> 

- 2 <mark>Objective: To improve error handling, client-side data validation, and load state.</mark> 

4 

_H.-V. Tran et al._ 

_Journal of Computer Languages 88 (2026) 101403_ 



**Fig. 2.** Details of Phase 1. 

- 3 <mark>Refine the [Processing Function Name] function in the FE Component: Loading State: Disable/Disable Spinner when isLoading is true. API Errors: If the API returns an error (e.g., 400/500), display the correct error message: [Detailed Error Message or General Error Message] at [Error Display Location]. FE Validation: Add client-side input validation (e.g., [FE Validation Rule Description, e.g., check password match, field not empty]) before calling the API.</mark> 

- 6 <mark>Generate the result according to the template and meet the requirements</mark> **<mark>in</mark>** <mark>the use</mark> **<mark>case</mark>** <mark>.’;</mark> 

- 7 <mark>//Calling Gemini API</mark> 8 <mark>const model = genAI.getGenerativeModel({ model: ’gemini-2.5-pro’ });</mark> 

- 9 <mark>const result = await model.generateContent(prompt);</mark> 

- 10 <mark>const response = await result.response;</mark> 11 <mark>const text = response.text();</mark> 12 <mark>//Return the result</mark> 13 <mark>res.json({success: true, result: text, usecase: usecase, template: template});</mark> 

Listing 4: Detailed structure of Prompt D. 

Listing 5: The code snippet calling Gemini API 

The system is evaluated through unit and integration testing to verify functional correctness, component interaction, and systematic error handling, supported by logging mechanisms for reliability improvement. Additionally, standardized prompt templates enable controlled, repeatable code generation, ensuring consistency, structural coherence, and enhanced stability across the software system. 

#### _4.2.2. Processing procedure_ 

All input artifacts are synthesized by an internal intermediary tool<sup>5</sup> implemented as a Node.js/Express API, which normalizes and aggregates context to generate coding prompts for the Gemini<sup>6</sup> model. Inputs include use cases, Figma UI/UX designs, and API contracts, producing prompts directly importable into Cursor (Fig. 2). 

Listing 5 describes the VC-AWG-Coding Prompt Generation Tool, a Node.js<sup>7</sup> and Express.js<sup>8</sup> –based middleware that bridges high-level specifications and the LLM. The tool analyzes use case specifications and UI designs, decomposes workflows, maps UI interactions to backend logic, and defines validation, error handling, and response states, producing structured, semantically coherent coding prompts for Phase 2. 

- 1 <mark>const prompt = ‘Based on the use</mark> **<mark>case</mark>** <mark>specification and the following output template, generate the appropriate result:</mark> 

- 2 <mark>**Original Prompt:**</mark> 

- 3 <mark>${usecase}</mark> 

- 4 <mark>**Output Template:**</mark> 5 <mark>${Prompt A + Prompt B + Prompt C + Prompt D}</mark> 

> 5 https://github.com/vietth2004/VC-AWG-CodingPromptGenTool. 

This phase employs the Google Generative AI SDK to connect with the Gemini-2.5-pro model, using standardized prompts that encode architectural constraints and coding conventions. Asynchronous API processing improves throughput, while the closed-loop VC-AWG workflow ensures accurate, controlled code generation, reducing human error and enhancing code quality, extensibility, and long-term sustainability. 

#### _4.2.3. The outputs of Phase 1_ 

The Phase 1 output is a comprehensive coding prompt directly importable into Cursor,<sup>9</sup> encoding business logic, UI states, API interactions, and their semantic relationships. By embedding architectural guidelines and coding standards, the prompt enables accurate Zero-shot or Few-shot code generation by models such as Claude 4.5 Sonnet or GPT-4o, ensuring Clean Code compliance and immediate IDE usability. 

#### _4.3. Phase 2: Website source code generation_ 

In Phase 2, source code generation is guided by the Phase 1 prompt, the existing codebase, and predefined architectural rules, provided to an LLM such as Gemini. The model generates context-aware code that is iteratively validated for syntactic, semantic, and structural correctness until all errors are resolved. This iterative validation is supported by a context-aware development environment (e.g., Cursor), which monitors generated code and enables continuous feedback and refinement during the generation process. Although the current implementation leverages a specific development environment (e.g., Cursor), the proposed VCAWG method is tool-agnostic and can be applied to other LLM-based development environments that support contextual code generation and iterative refinement. An overview of the Phase 2 workflow is illustrated in Fig. 3. 

> 6 https://gemini.google.com/. 

> 7 https://nodejs.org/. 

> 8 https://expressjs.com/. 

> 9 https://cursor.com/. 

5 

_H.-V. Tran et al._ 

_Journal of Computer Languages 88 (2026) 101403_ 







**Fig. 3.** Details of Phase 2. 

#### _4.3.1. Inputs of Phase 2_ 

_Coding prompt._ In Phase 2 of the proposed method, the coding prompt serves as the core technical specification for automated source code generation, functioning as a comprehensive and systematically structured document rather than a collection of isolated requirements. It explicitly defines the business objectives, scope, and expected outcomes of the target function, thereby aligning the code generation model with the system’s operational and architectural context. The prompt further specifies the logical processing flow, detailing data validation, propagation, exception handling, and consistency across execution paths, which reduces ambiguity and improves the faithful realization of business logic. For UI-related functionalities, it additionally describes interface structure, behavior, and validation rules in accordance with the Figma design. Overall, the coding prompt acts as an intermediary artifact bridging business analysis and automated implementation, where a rigorously structured and semantically complete specification enhances code generation accuracy, minimizes iterative corrections, and improves the efficiency of the Phase 2 development process. 

_Project codebase._ In Phase 2, in addition to the coding prompt, the existing project codebase serves as a core input by providing essential technical and architectural context for automated source code generation. Rather than merely acting as an initial baseline, the codebase functions as a structural blueprint that conveys project organization, naming conventions, and interaction patterns, enabling newly generated code to be seamlessly integrated without violating architectural constraints. At the server layer, it defines foundational infrastructure, data models, configurations, and security mechanisms, thereby offering a standardized scaffold for consistently generating Controllers, Services, and Data Transfer Objects (DTOs). At the presentation layer, it establishes routing, state management, shared components, API invocation services, and reusable utilities, ensuring consistency in layout and interaction patterns. Overall, the codebase provides stable architectural constraints that support incremental functional expansion while ensuring that Phase 2 code generation remains aligned with system-wide standards, scalability requirements, and architectural principles. 

In practice, the codebase is provided as a complete project directory, including source files, configurations, and dependency definitions, which are directly accessible by the code generation environment 

(e.g., Cursor). The system leverages this directory-level representation to infer architectural patterns, module boundaries, and naming conventions. A concrete example of the project codebase structure used in the experiments is described in Section 5.2. 

_Code generation rules._ In addition to the coding prompt and the existing project codebase, the proposed method introduces a set of mandatory code generation rules that act as strict constraints governing all generated source code. These rules explicitly define the technology stack, software frameworks, architectural model, layer separation principles, directory structure, state management strategies, and naming conventions, thereby ensuring consistency across system components. They prescribe a modular, dependency-injection-based architecture at the server layer and a component-based paradigm at the presentation layer, while clearly delineating responsibilities and interaction boundaries among logical layers. The rules further standardize directory organization, coding conventions, and procedures for state management, error handling, and inter-layer communication. Overall, these code generation rules function as a technical contract for Phase 2, enforcing architectural compatibility, improving maintainability and scalability, and minimizing structural inconsistencies across code generation iterations. 

In the current implementation, these rules are specified as structured Markdown-based configuration files (e.g., .mdc) that define architectural constraints, coding conventions, and technology-specific guidelines. These rule files are loaded as part of the project context and interpreted by the code generation environment during synthesis. Concrete examples of these rules are provided in Section 5.3. 

#### _4.3.2. Code generation process_ 

The Phase 2 code generation process follows a sequential and repeatable workflow to ensure consistency across iterations. Initially, Cursor loads the full project context, including coding prompts, source structure, configurations, modules, and predefined architectural rules, to build an internal architectural model. Based on this context, it identifies components to be created or selectively updated while preserving naming conventions, layer separation, and minimizing unnecessary changes. Cursor then synthesizes coherent source code implementing business logic, data flow, APIs, and UI rendering, with systematic 

6 

_H.-V. Tran et al._ 

_Journal of Computer Languages 88 (2026) 101403_ 

refinement of imports, declarations, inter-layer data flow, module dependencies, and coding standards. A core feature of Phase 2 is an automated self-correction loop that re-evaluates generated code against prompts, rules, and the existing codebase. In the current implementation, this loop is primarily supported by the code generation environment (e.g., Cursor), which continuously monitors generated code for syntactic errors, logical inconsistencies, and architectural violations. 

When such issues are detected, the environment automatically formulates targeted sub-prompts that incorporate error context, code fragments, and relevant constraints derived from the coding prompt, project codebase, and generation rules. These sub-prompts are then used to iteratively refine the generated code until functional correctness and architectural compliance are achieved, as illustrated in Fig. 3. 

#### _4.3.3. Output of Phase 2_ 

The output of Phase 2 is a complete and executable set of source code artifacts, including newly generated and modified files that collectively satisfy the specified functional requirements. The generated code encompasses business logic, data processing, user interface components, and system configurations, all organized in accordance with the predefined project structure and architectural principles. In parallel, the system automatically records a structured list of created and modified files, providing traceability across generation cycles and supporting impact assessment in automated development settings. Overall, Phase 2 produces a ready-to-use codebase that enables immediate execution, testing, or integration, while establishing a stable and reliable baseline for subsequent development phases. 

#### _4.4. Exception handling_ 

#### _4.4.3. Data model error_ 

Data model errors occur when request or response structures are incompatible with corresponding Data Transfer Objects (DTOs) or entities, leading to deserialization failures or type inconsistencies during execution. To resolve these issues, Cursor performs data flow analysis to detect missing or inconsistent fields across system boundaries and proposes corresponding DTO modifications. After developer validation, the tool automatically adjusts field definitions and data types, ensuring consistent and synchronized data models between client and server components. 

#### _4.4.4. Source code and structure conflict error_ 

Code and structural conflicts occur when bug fixes or new features interfere with existing logic or project organization, such as duplicating files or modifying overlapping components. To maintain code integrity, Cursor performs pre-write validation, analyzes structural differences, and proposes safe merging strategies, thereby preventing data loss, preserving architectural consistency, and supporting efficient conflict resolution. 

#### _4.4.5. Interface and logic error/mismatch_ 

Logic–interface mismatches occur when user interface behavior does not reflect the outcomes or state changes produced by underlying business logic, such as successful backend persistence without corresponding frontend updates. To resolve this issue, Cursor compares developer-provided screenshots of observed behavior with expected outputs, analyzes state management, event handling, and callback logic, and recommends targeted corrections, including state updates, rendering adjustments, or data-binding fixes between business logic and interface components. 

#### **5. Experiments** 

In modern software development, exceptions and errors are inevitable and typically reflect deficiencies in business logic, data modeling, or component interactions, making their timely identification and handling critical to system robustness and development efficiency. Context-aware programming support tools, such as Cursor, contribute to this process by analyzing source code within its execution and architectural context, localizing root causes, and recommending corrective actions. Classifying errors by their characteristics and underlying causes further supports effective maintenance and fault management. Accordingly, the following section outlines common error categories in modern application architectures and their corresponding handling mechanisms. 

#### _4.4.1. Network communication and security errors (CORS)_ 

Cross-Origin Resource Sharing (CORS) errors occur when browsers block cross-origin HTTP requests that violate the same-origin policy and are typically identified via browser console diagnostics. Resolving these issues requires server-side configuration of response headers such as Access-Control-Allow-Origin and Access-Control-Allow-Methods. Context-aware programming tools like Cursor can analyze server configurations or middleware and automatically apply the necessary adjustments, enabling efficient and automated resolution of CORS-related issues without disrupting development workflows. 

#### _4.4.2. API configuration and routing errors_ 

API configuration and routing errors arise when client-invoked endpoints do not match server-defined routes, typically resulting in HTTP 404 Not Found responses. To address this issue, Cursor analyzes the project source code by comparing client-side API definitions with backend routing configurations, automatically detecting inconsistencies and suggesting corrections. This automated synchronization improves alignment between the presentation layer and business logic, thereby reducing client–server integration errors. 

To evaluate the effectiveness and practical feasibility of the proposed VC-AWG method, we implemented a prototype system and conducted an experimental study. The experiment was carried out on a machine with the following specifications: Microsoft Windows 11 Home operating system, an Intel<sup>®</sup> Core<sup>TM</sup> i7-13650HX processor, and 16 GB of RAM. 

The target application for code generation is a Personal Financial Management (PFM) website, selected as a representative, moderately complex web-based system. The application comprises 16 use cases (shown in Table 5), 16 user interface screens designed in Figma, and 16 RESTful API endpoints, covering core functionalities such as transaction management, budgeting, reporting, and user authentication. In addition, the system follows a multi-tier architecture involving frontend components, backend services, and API integration, requiring the coordination of heterogeneous artifacts. 

This level of complexity reflects a typical real-world business web application and is sufficient to evaluate the capability of VC-AWG in handling diverse inputs, including use case specifications, UI designs, and API contracts. Although the evaluation is conducted on a single case study, a comprehensive report covering experiments across all use cases is publicly available here,<sup>10</sup> providing additional transparency and empirical evidence. The selected application encompasses a wide range of functional and structural elements commonly found in modern web systems, thereby offering a meaningful basis for assessing the general applicability of the proposed approach. Furthermore, the VCAWG method is designed to be domain-independent, as it operates on abstract software artifacts rather than domain-specific logic, which further supports the transferability of the results. Future work will include evaluations on multiple applications from different domains to further validate the generalizability of the proposed method. 

> 10 https://github.com/vietth2004/VC-AWG-Demo_FinalCode/blob/main/ TechnicalReport.pdf. 

7 

_H.-V. Tran et al._ 

_Journal of Computer Languages 88 (2026) 101403_ 



**Fig. 4.** Description of the PFM codebase. 

Collectively, these specifications ensure cross-layer architectural alignment and enable reliable, standards-compliant code generation and maintenance. 

In the experimental setup, coding rules are specified as structured Markdown-based configuration files (i.e., .mdc format) that define architectural constraints, naming conventions, and framework-specific guidelines. These rules are incorporated into the code generation context and systematically enforced during synthesis. 

To provide a concrete illustration, Listings 6, 7, and 8 present simplified examples of coding rule specifications for the overall project, as well as for the backend and frontend components used in our experiments. More comprehensive rule definitions can be found in the .cursor directory of the project repository.<sup>14</sup> 

- 1 <mark>---</mark> 

- 2 <mark>alwaysApply: true</mark> 

- 3 <mark>---</mark> 

#### _5.1. System requirement_ 

The Personal Financial Management (PFM) system is a web-based application that enables users to track cash flows, manage assets, analyze expenses, and define long-term financial goals through an integrated view of transactions, accounts, and visual analytics. Functionally, the architecture comprises four core modules: account and balance management, transaction management, expense and bill analysis, and goal management, each corresponding to essential financial use cases. Supported operations include user authentication, transaction and account management, category-based expense analysis, bill tracking, goal setting, and savings visualization. The user interface is adopted from a design<sup>11</sup> created in Figma. This paper focuses on the Login use case, while detailed implementations are reported separately.<sup>12</sup> 

#### _5.2. Codebase setup_ 

The project employs a modern TypeScript/Node.js–centric technology stack to ensure performance, maintainability, and extensibility. An overview is shown in Fig. 4, and the full codebase is publicly available on GitHub.<sup>13</sup> The frontend is implemented with React using a component-based architecture, supported by Vite for rapid builds, Zustand for lightweight state management, and Tailwind CSS for flexible styling. The backend is developed with Node.js and NestJS, following a modular architecture, with TypeORM and MySQL for persistence and JWT-based authentication via Passport. 

In addition to the technology stack, the project codebase is provided to VC-AWG as a complete source directory, including backend and frontend modules, configuration files, and dependency definitions. This directory is directly loaded into the code generation environment (e.g., Cursor), enabling the system to analyze architectural patterns, module structures, and integration points. 

#### _5.3. Coding rules_ 

In the project codebase, the .cursor directory acts as a centralized repository of coding rules and project-specific conventions used by Cursor to guide automated code generation and refactoring. It consolidates global engineering standards, backend and frontend development rules, and database schema documentation, covering coding style, architecture, security, state management, and data consistency. 

> 11 https://www.figma.com/files/team/1304700395800107622/resources/ community/file/1227525441534506928. 

- 4 <mark>## 1. General Rules</mark> 5 <mark>### Coding Convention</mark> 6 <mark>- **camelCase** → variable, function.</mark> 

- 7 <mark>- **PascalCase** → class, component, entity.</mark> 

- 8 <mark>- **kebab-case** →</mark> folder, file (except React component). 

- 9 <mark>- API prefix: ‘/api/...‘</mark> 

- 10 <mark>- Standard JSON response format:</mark> 11 <mark>‘‘‘json</mark> 12 <mark>{ "success": true, "message": "OK", "data": { ... } }</mark> 13 <mark>‘‘‘</mark> 14 <mark>### Error & Logging</mark> 15 <mark>* Handle errors via ‘GlobalExceptionFilter‘ (NestJS).</mark> 16 <mark>* Do not log sensitive information.</mark> 17 <mark>* All API errors return:</mark> 18 <mark>‘‘‘json</mark> 19 <mark>{ "success": false, "message": "Error message" }</mark> 20 <mark>‘‘‘</mark> 21 <mark>## 2. Cursor AI Rules</mark> 22 <mark>> Rules specific to **Cursor IDE** for generating standard code automatically.</mark> 

- 23 <mark>### General Behavior</mark> 24 <mark>* When creating a new module (NestJS): always generate all of the following:</mark> 

- 25 <mark>‘controller‘, ‘service‘, ‘entity‘, ‘dto‘, ‘module‘.</mark> 26 <mark>* When creating a CRUD API: generate all the following functions:</mark> 

- 27 <mark>‘create‘, ‘findAll‘, ‘findOne‘, ‘update‘, ‘delete‘.</mark> 28 <mark>* When creating a React component: export defaults, use Tailwind, and place them in the correct folder.</mark> 

- 29 <mark>* When creating a React API: generate functions in ‘src/api/‘ and call them using AxiosInstance.</mark> 

- 30 <mark>* Do not place business logic in controllers or UI components.</mark> 

- 31 <mark>* If unsure of the requirements, **ask the user instead of guessing**.</mark> 

- 32 <mark>* Always add short comments describing the meaning of the class/function.</mark> 

- 33 <mark>### Example Prompts</mark> 34 <mark>* Create NestJS module for user management (CRUD).</mark> 35 <mark>* Add authentication module with JWT in NestJS.</mark> 36 <mark>* Generate React page to list users with pagination.</mark> 37 <mark>* Connect React form to NestJS endpoint via Axios.</mark> 38 <mark>---</mark> 39 <mark>## 3. API Convention</mark> 40 <mark>* All backend APIs start with ‘/api/...‘</mark> 41 <mark>* Standard Response:</mark> 42 <mark>‘‘‘json</mark> 43 <mark>{ "success": true, "message": "Fetched successfully", "data": [...] }</mark> 

> 12 https://github.com/vietth2004/VC-AWG-Demo_FinalCode/blob/main/ TechnicalReport.pdf. 

> 13 https://github.com/vietth2004/VC-AWG-Demo_Codebase. 

> 14 https://github.com/vietth2004/VC-AWG-Demo_Codebase. 

8 

_H.-V. Tran et al._ 

_Journal of Computer Languages 88 (2026) 101403_ 

|44|‘‘‘|
|---|---|
|45|* Error Return:|
|46|‘‘‘json<br>|
|47|{ "success": false, "message": "Resource not found" }|
|48|‘‘‘|
|49|* Use appropriate HTTP statuses:|
|50|* ‘200 OK‘|
|51|* ‘201 Created‘|
|52|* ‘400 Bad Request‘|
|53|* ‘401 Unauthorized‘|
|54|* ‘404 Not Found‘|
|55|* ‘500 Internal Server Error‘|



Listing 6: Example of general coding rules specification (.mdc format) 

   - 9 <mark>|-- assets/ # images, icons</mark> 

   - 10 <mark>|-- components/ # reusable components</mark> 

   - 11 <mark>|-- hooks/ # custom hooks</mark> 

   - 12 <mark>|-- pages/ # main pages (Home, Login, Dashboard, ...)</mark> 

   - 13 <mark>|-- context/ # React context (auth, theme, ...)</mark> 14 <mark>|-- router/ # route definition</mark> 15 <mark>|-- utils/ # helper functions</mark> 

   - 16 <mark>|-- App.jsx</mark> 

   - 17 <mark>\-- main.jsx</mark> 18 <mark>‘‘‘</mark> 19 <mark>### Detailed Rules</mark> 

   - 20 <mark>* Use functional components + React Hooks.</mark> 

   - 21 <mark>* Manage state using the Context API or Zustand.</mark> 

   - 22 <mark>* Call APIs via the Axios instance in ‘src/api/‘.</mark> 

   - 23 <mark>* Do not call URLs directly in components.</mark> 

   - 24 <mark>* Use TailwindCSS for UI, avoid inline styles.</mark> 

- 1 <mark>---</mark> 2 <mark>alwaysApply: false</mark> 

- 3 <mark>---</mark> 4 <mark>## Backend Rules (NestJS)</mark> 5 <mark>### Folder Structure</mark> 6 <mark>‘‘‘</mark> 7 <mark>src/</mark> 8 <mark>|-- main.ts</mark> 9 <mark>|-- app.module.ts</mark> 

- 10 <mark>|-- config/ # DB, CORS, env config</mark> 11 <mark>|-- common/ # Decorators, guards, interceptors, utils</mark> 12 <mark>|-- modules/ # Each feature is a separate module</mark> 13 <mark>| |-- user/</mark> 14 <mark>| | |-- user.module.ts</mark> 

- 15 <mark>| | |-- user.controller.ts</mark> 16 <mark>| | |-- user.service.ts</mark> 17 <mark>| | |-- user.entity.ts</mark> 18 <mark>| | |-- dto/</mark> 19 <mark>| | \-- interfaces/</mark> 20 <mark>|-- filters/ # Exception filters</mark> 21 <mark>|-- interceptors/ # Logging, response transform</mark> 22 <mark>|-- database/ # ormconfig.ts</mark> 23 <mark>\-- main.ts</mark> 24 <mark>‘‘‘</mark> 25 <mark>### Detailed rules</mark> 26 <mark>* Each module includes:</mark> 27 <mark>* ‘controller.ts‘: handle HTTP request, call service.</mark> 28 <mark>* ‘service.ts‘: contains business logic.</mark> 29 <mark>* ‘entity.ts‘: database table mapping.</mark> 30 <mark>* ‘dto/‘: defines request/response (using ‘class-validator‘).</mark> 

31 <mark>* Business logic **is only in the service**.</mark> 32 <mark>* Controller only **receives requests → calls the service →</mark> returns a response**. 33 <mark>* Uses the ‘Repository‘ pattern of TypeORM.</mark> 34 <mark>* Modules only import necessary modules (avoiding import loops).</mark> 35 <mark>* Configure ‘.env‘ via ‘@nestjs/config‘.</mark> 36 <mark>* Consistent response format:</mark> 37 <mark>‘‘‘</mark> 38 <mark>return { success: true, message: ’User created’, data: user };</mark> 39 <mark>‘‘‘</mark> 

Listing 7: Example of backend coding rules specification (.mdc format) 

- 1 <mark>---</mark> 

- 2 <mark>alwaysApply: false</mark> 3 <mark>---</mark> 4 <mark>## Frontend Rules (React + TailwindCSS + Typescripts)</mark> 5 <mark>### Folder Structure</mark> 6 <mark>‘‘‘</mark> 7 <mark>src/</mark> 8 <mark>|-- api/ # axios instance, endpoint functions</mark> 

- 25 <mark>* Each page/component has a clear role:</mark> 

- 26 <mark>* UI component → display only.</mark> 

- 27 <mark>* Logic component → process data, call APIs.</mark> 

- 28 <mark>* Use PropTypes or TypeScript to define props.</mark> 29 <mark>* Routing using React Router v6.</mark> 30 <mark>* Always handle loading and error state.</mark> 31 <mark>* Separate UI and logic if the component is complex.</mark> 

Listing 8: Example of frontend coding rules specification (.mdc format) 

#### _5.4. Experimental result for login page_ 

In the limited scope of this paper, we present the experiment results for a common Login use case of the website. Other experimental results can be found in the technical report at this link: https://github.com/v ietth2004/VC-AWG-Demo_FinalCode/blob/main/TechnicalReport.pdf 

_Use case specification._ Table 2 presents the Login use case specification, which allows users to access the system with valid credentials. 

_UI design in Figma._ The UI design of the login function is shown in this link. 

https://www.figma.com/design/iE0nfper0rck0R1b0MQBzo/Fineba nk ---Financial-Management-Dashboard-UI-Kits--Community-?node-id= 137-7 477&t=cxgXQfkGoLMfxW48-4 

_API contract._ The API contract of the Login use case is shown in Listing 9. 

_Coding prompt._ The resulting coding prompt of Phase 1 for the login use case is shown in Listing 10. 

_The generated login page at glance._ The final experimental website source code is publicly available on GitHub.<sup>15</sup> Fig. 5 presents the generated Login page of the ‘‘Personal Financial Management’’ website (FINEbank.IO), implemented in accordance with the provided Figma specification. The interface follows a clean, minimalist layout, featuring a branded header, a central login form with standard authentication options, and alternative sign-in links, ensuring usability and consistency with the original UI design. 

#### _5.5. The generated source code_ 

#### _5.5.1. The generated source code in backend project_ 

Table 3 summarizes the backend folders containing generated files, reflecting the modular structure of the system. Each directory represents a domain-specific API group. The table describes the purpose of each module and maps it to supported use cases, illustrating how backend services enable authentication, data management, transactions, analytics, and financial planning features. 

> 15 https://github.com/vietth2004/VC-AWG-Demo_FinalCode. 

9 

_H.-V. Tran et al._ 

_Journal of Computer Languages 88 (2026) 101403_ 

##### **Table 2** 

The specification of the Log in use case. 

|Use case name|Login|
|---|---|
|Description|Allows the user to authenticate their identity using email and password to access the system.<br>Supports the ‘‘Save login information’’ option.|
|Actor|User|
|Main flow|The user accesses the Login button on the Homepage.<br>The system redirects to the Login page.<br>The user enters their email and password.<br>Clicks the ‘‘Login’’ button.<br>The system checks for validity.<br>If valid: establish a login session.<br>Redirects to the Homepage and displays ‘‘Logout’’.|
|Exception flow|If the email or password is incorrect: displays the error ‘‘Incorrect email or password’’.<br>The user remains on the Login screen.|
|Alternative flow|The user selects ‘‘Save login information’’.<br>If successful, the system remembers the login session.|
|Precondition|The user is on the Homepage.<br>A valid account is already present.|
|Postcondition|Success: Login and redirects to the Homepage.<br>Failure: An error is displayed.|



- 1 <mark>Endpoint: POST /api/auth/login</mark> 

- 2 <mark>Request Body:{"email":"johndoe@email.com","password":"mypassword"}</mark> 

3 <mark>Response upon success: {"accessToken":"JWT_TOKEN","user":{"id": 1,"fullName":"John Doe","email":"johndoe@email.com"}}</mark> 4 <mark>Error response: {"error": "Incorrect email or password."}</mark> 

Listing 9: The API contract of Login use case. 

##### **Table 3** 

The <u>generated</u> folders in the backend <u>project.</u> 

|Module|Purpose|Supported use cases|
|---|---|---|
|modules/auth/|Login/registration API|Login, register|
|modules/account/|API for performing CRUD operations for account|View/add/edit/delete account|
|modules/transaction/|API for transactions|View, create transactions|
|modules/bill/|API for bills|View the list of bills|
|modules/category/|API for categories|View the category list|
|modules/expenses/|Expense analysis API|View monthly expenses, detailed by category|
|modules/goal/|API performs CRUD operations for the target|View, create, edit goals|
|modules/savings/|API aggregation for cost savings|View the overall chart|
|modules/user/|Schema for the ‘Users’ table|Login, register|





**Fig. 5.** The generated Login screen. 

#### _5.5.2. The generated source code in frontend project_ 

Table 4 summarizes the generated frontend files, their purposes, and related use cases. Each .tsx file corresponds to a UI component or page. Form and Modal components support user input and management tasks, Page components render core application views, Chart and Summary components provide financial visualizations, and the Toast component delivers global notifications across the system. 

#### _5.6. Experimental results_ 

This section evaluates the VC-AWG approach using use case specifications, UI designs, API contracts, the project codebase, and coding rules, with a focus on automated generation of website functionality. Experiments were conducted on 16 use cases of the Personal Financial Management website, measuring the number of sub-prompts, AI-assisted editing time via Cursor, additional manual correction time, and estimated fully manual development effort based on feedback from four experienced developers. Table 5 summarizes the required effort per use case. The results show that the average VC-AWG development time (i.e., Cursor time + Manual correction time) is _𝑚𝑒𝑎𝑛_ = 21 _._ 1 min per use case (standard deviation _𝑆𝐷_ = ~~√~~ _𝑛_ −11 ~~∑~~ _𝑛𝑖_ =1<sup>(</sup><sup>_𝑥𝑖_−</sup><sup>_̄ 𝑥_)2= 6</sup><sup>_._5min),with</sup> a median of 20 min and values ranging from 13 to 34 min. The moderate standard deviation, together with the close alignment between the 

10 

_H.-V. Tran et al._ 

_Journal of Computer Languages 88 (2026) 101403_ 

|1<br>2<br>3|1. Prompt A: Backend code generation (NestJS Service/Controller)<br><br>Objective: To build API services, business logic, and server error handling for the login functionality..<br><br>Create a POST endpoint api/auth/login in NestJS’s AuthController. This endpoint is a public route and does not<br>require Guard authentication.|
|---|---|
|4<br>5<br>6<br>7<br>8<br>9<br>10|Request format: {"email": "string","password":"string"}<br><br>AuthService processing logic:<br><br>Receive email and password from the request body.<br><br>Find the user in the database using the email.<br><br>If not found or the password does not match, processing fails.<br><br>If correct, create a JSON Web Token (JWT) containing the user’s identifier.<br><br>Return the token and the user’s basic information.|
|11|Successful Response format:{ "accessToken":"JWT_TOKEN","user": {"id": 1,"fullName":"John<br>Doe","email":"johndoe@email.com"}}|
|12<br>13|Error Handling: If the email does not exist or the password is incorrect, the system throws an UnauthorizedException<br>with the following JSON error: {"error": "Incorrect email or password." }<br><br>2. Prompt B: Generate Frontend Code (React Component & UI/MCP)|
|14<br>15<br>16<br>17<br>18|Objective: Build the login interface according to Figma’s design.<br><br>Create the LoginForm component using React TypeScript and Tailwind CSS. The form includes: Email input field,<br>Password input field, "Save login information" checkbox, "Login" button, "Forgot password?" link.<br><br>Please adhere strictly to the Figma MCP design at the following link:<br><br>https://www.figma.com/design/iE0nfper0rck0R1b0MQBzo/Finebank<br>---Financial-Management-Dashboard-UI-Kits--Community-? node-id=137-7 477&t=Jwl8SfgcguZ5Gicc-4<br><br>3. Prompt C: Generate Frontend Logic Code (State & API Connections)|
|19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>29<br>30<br>31<br>32|Objective: Connect the UI form to the API and handle the successful login flow.<br><br>Add states: email: string, password: string, rememberMe: boolean. Implement the asynchronous handleSubmit function<br>to send a POST request to api/auth/login.<br><br>Payload sent:{"email": "johndoe@email.com", "password": "mypassword"}<br><br>Upon successful login: Save the accessToken to localStorage.<br><br>Save user information to the global state (Context API / Redux / Zustand).<br><br>Redirect the user to the homepage /.<br><br>4. Prompt D: Exception Handling (Client-side Validation & Error Handling)<br><br>Objective: To improve client-side error handling, loading, and validation.<br><br>Upgrade the handleSubmit function with the following features:<br><br>Loading State: Add the state ‘isLoading’. While processing, disable the Login button and display a spinner.<br><br>API Error Handling: If the API returns a ‘401’ error, display the message: "Incorrect email or password."<br><br>FE Validation: Email cannot be blank and must be in the correct format.<br><br>Password cannot be blank.<br><br>If an error occurs, display a message directly below the input field.|



Listing 10: The coding prompt of login use case. 

mean and median, indicates a relatively consistent performance across use cases. 

To assess the statistical significance of the observed differences, we conducted a paired t-test comparing VC-AWG and estimated manual development times across the 16 use cases. The standard deviation of the paired differences is computed as _𝑠𝑑_ = ~~√~~ _𝑛_ −11 ~~∑~~ _𝑛𝑖_ =1<sup>(</sup><sup>_𝑑𝑖_−</sup><sup>_̄ 𝑑_)2,</sup> where _𝑑𝑖_ , _̄𝑑_ , and _𝑛_ are the estimated manual development time - VCAWG time, the average of all _𝑑𝑖_ , and 16, respectively, resulting in _𝑠𝑑_ ≈229 _._ 5 min. As a result, _𝑡_ = _𝑠𝑑_ ∕ _𝑑_ ~~√~~ _𝑛_<sup>=</sup> 229788 _._ 5∕ _._ 94 ~~√~~ 16<sup>=13</sup><sup>_._75.Theresults</sup> 

indicate a highly significant reduction in development time, confirming that the performance improvement achieved by VC-AWG is statistically robust. In addition, a non-parametric Wilcoxon signed-rank test yields consistent results ( _𝑝<_ 0 _._ 001), further supporting the validity of the observed differences. The large effect size and consistent differences across all use cases further indicate that the improvement is not only statistically significant but also practically meaningful. 

#### _5.7. Discussions_ 

#### _5.7.1. Performance and efficiency analysis_ 

Based on Table 5, VC-AWG demonstrates substantial efficiency gains over manual development. The average AI-assisted development time, including manual edits, is 21.1 min per use case, compared to 786 min for fully manual implementation, corresponding to a time reduction of approximately 97.3%. When categorized by complexity, simple CRUD use cases require 13–20 min, while complex statistical functions take 

20–34 min. Notably, across all 16 use cases, VC-AWG consistently achieves speed-ups of 24–69 times relative to manual development, indicating robust effectiveness for both basic CRUD operations and more complex, data-intensive functionalities. 

Experimental results indicate that VC-AWG, grounded in use case specifications, API contracts, UI designs, project codebase, and coding rules, delivers substantial benefits. It reduces development time by up to 97.3%, improves code consistency through structured generation, minimizes copy–paste errors, and significantly accelerates development, particularly for large-scale systems with numerous APIs, highlighting its potential to standardize and streamline software engineering workflows. 

#### _5.7.2. Practical implications and scalability_ 

The use of multiple expert estimates helps mitigate individual bias and provides a more reliable approximation of real-world development effort. Notably, even for more complex use cases with higher estimated manual effort, VC-AWG maintains relatively low execution times, suggesting good scalability with respect to functional complexity. For instance, use cases such as _View transaction history_ , _View expenses by month_ , and _View the summary chart savings_ involve non-trivial data aggregation, filtering, and visualization logic, while _Create a new transaction_ and _Adjusting monthly goals_ require coordinated handling of validation, state management, and backend integration. Despite these varying levels of complexity, VC-AWG consistently generates functional implementations within a comparable time range, indicating its ability to generalize across different classes of application logic. 

11 

_H.-V. Tran et al._ 

_Journal of Computer Languages 88 (2026) 101403_ 

##### **Table 4** 

Generated files in the frontend <u>project.</u> 

|File|Purpose|Related use cases|
|---|---|---|
|LoginForm/<br>LoginForm.tsx|Login form|Log in|
|SignUpForm/<br>SignUpForm.tsx|Registration form|Register|
|AddTransactionForm/<br>AddTransactionForm.tsx|Add transaction form|Create a new<br>transaction|
|AddAccountForm/<br>AddAccountForm.tsx|Add account form|Add account|
|AccountEditForm/<br>AccountEditForm.tsx|Account editing form|Edit account|
|DeleteAccountModel/<br>DeleteAccountModal.tsx|Modal deletes account|Delete account|
|UpcomingBills/<br>UpcomingBills.tsx|Upcoming invoice<br>display|View the list of<br>invoices|
|ExpensesBreakdown/<br>ExpensesBreakdown.tsx|Expenditure details<br>by category|View spending<br>details|
|ExpenseSummaryChart/<br>ExpenseSummaryChart.tsx|Monthly spending<br>chart|View inventory<br>spending month|
|SavingsSummaryChart/<br>SavingsSummaryChart.tsx|Savings chart|View savings chart|
|CreateGoalModal/<br>CreateGoalModal.tsx|Goal creation modal|Set new goals|
|AdjustGoalModal/<br>AdjustGoalModal.tsx|Modal for adjusting<br>targets|Adjust the target|
|Toast/Toast.tsx|Display quick (toast)<br>notifications|The whole website|
|AddTransaction/<br>AddTransactionPage.tsx|Add transaction page|Create a new<br>transaction|
|AccountList/<br>AccountListPage.tsx|Account list page|View the list of<br>assets|
|AccountDetail/<br>AccountDetailPage.tsx|Account details page|View account<br>details|
|AddAccount/<br>AddAccountPage.tsx|Add account page|Add account|
|Expenses/<br>ExpensesPage.tsx|Expense analysis page|View monthly<br>expenses, detailed<br>by category.|



From a practical standpoint, reducing development time from several hours to under half an hour per use case can significantly accelerate development cycles and support rapid prototyping. It should be noted that the selected use cases are representative of common functional categories in web applications, including CRUD operations (e.g., _Add/Edit/Delete bank account_ ) and data visualization (e.g., _View expenses by month_ ). The reported manual development times are based on expert estimates rather than controlled implementation experiments; however, such estimates reflect common industrial practice and remain a reasonable baseline for comparison. 

#### _5.7.3. Code quality, maintainability, and limitations_ 

In addition to development time, the quality and practical usability of the generated code are important considerations. Based on our experimental observations, VC-AWG produces code that is generally consistent with the predefined codebase and coding rules, resulting in a relatively uniform structure and naming conventions across different use cases. This structured generation process contributes positively to code readability and maintainability, as developers can more easily understand and extend the generated artifacts. 

Furthermore, by leveraging API contracts and UI design specifications, the generated code adheres closely to functional requirements and interface definitions, reducing integration inconsistencies. However, the approach does not explicitly guarantee advanced quality 

attributes such as security robustness or comprehensive test coverage. While basic functional correctness is typically achieved, additional validation, code review, and testing are still required before deployment in production environments. 

From a maintainability perspective, although the generated code follows consistent patterns, some outputs may exhibit fragmented logic or limited abstraction, particularly in more complex use cases. This suggests that human oversight remains necessary to refactor and optimize the generated components. 

VC-AWG significantly improves development efficiency while providing a reasonable baseline level of code quality. Nevertheless, future work will focus on incorporating automated quality assessment, security checks, and test generation mechanisms to further enhance the reliability and practical applicability of the approach. 

#### _5.7.4. Comparison with existing AI-assisted development tools_ 

To further contextualize the proposed approach, it is useful to compare VC-AWG with existing AI-assisted development tools such as GitHub Copilot<sup>16</sup> and Qodo (formerly Codium).<sup>17</sup> These tools primarily operate at the code level, generating snippets based on local context and developer prompts. While effective for accelerating lowlevel coding tasks, they typically rely on unstructured inputs and do not explicitly integrate heterogeneous software artifacts such as use case specifications, UI designs, and API contracts. 

In contrast, VC-AWG adopts a structured, multi-artifact approach, transforming high-level specifications into systematically constructed prompts and subsequently generating complete functional modules. This enables end-to-end automation of website functionality rather than incremental code suggestions. Moreover, the use of predefined codebases and coding rules allows VC-AWG to enforce consistency in architecture, naming conventions, and integration patterns, which is often not guaranteed in general-purpose AI coding assistants. 

From a workflow perspective, existing tools are primarily reactive, assisting developers during manual coding, whereas VC-AWG provides a proactive and systematic generation pipeline. This distinction is particularly important in large-scale or structured software projects, where coordination across multiple artifacts is required. 

While tools like Copilot and Qodo are highly effective for developer productivity at the code level, VC-AWG targets a different level of abstraction by automating the transformation from structured software artifacts to complete implementations, thereby offering complementary capabilities. 

#### **6. Conclusion** 

This paper presented VC-AWG, a Vibe Coding-based approach for automated website generation that uses large language models to transform high-level software artifacts into executable web applications. By integrating use case specifications, UI designs, API contracts, predefined codebases, and coding rules, VC-AWG organizes code generation into two phases: prompt synthesis and source code generation. This separation enables effective interpretation of heterogeneous inputs and improves the accuracy and consistency of generated backend and frontend components. Experiments on a Personal Financial Management website show that VC-AWG can reduce development effort by up to 97.3%, demonstrating the practicality of Vibe Coding for accelerating modern web development. 

Future work will focus on standardizing use case specifications, introducing automated logic consistency checking, integrating testing into the generation pipeline, combining Vibe Coding with formal verification, and designing a dedicated development process to support industrial-scale adoption of the VC-AWG method. Although the current 

> 16 https://github.com/features/copilot. 

> 17 https://www.qodo.ai. 

12 

_H.-V. Tran et al._ 

_Journal of Computer Languages 88 (2026) 101403_ 

**Table 5** 

Required time for developing each use case. 

|No.|Use case|Sub-prompts|Cursor (min)|Manual (min)|Estimate (h)|
|---|---|---|---|---|---|
|1|Register an account|2|5|15|10|
|2|Log in|2|5|15|8|
|3|View transaction history|3|3|10|15|
|4|Create a new transaction|4|3|10|12|
|5|View list of bank accounts|2|4|15|15|
|6|Add a bank account|3|4|10|10|
|7|Edit bank account|3|5|15|12|
|8|Delete bank account|2|3|10|8|
|9|View bank account details|2|4|25|15|
|10|View expenses by month|3|4|30|18|
|11|View expense details by category|3|4|20|20|
|12|View invoice list|2|3|20|14|
|13|View goal items by month|2|3|25|17|
|14|Create a new goal|3|4|15|10|
|15|Adjusting monthly goals|3|3|15|12|
|16|View the summary chart savings|3|5|25|20|



implementation leverages the built-in self-correction capabilities of the code generation environment, the generation and control of refinement sub-prompts remain largely implicit. We will investigate more explicit and systematic mechanisms for controlling these sub-prompts, including strategies for prompt optimization, error classification, and adaptive refinement, to improve transparency, controllability, and efficiency of the iterative code generation process, enabling a semi-autonomous correction process guided by contextual reasoning. 

The current implementation of VC-AWG is realized using a specific AI-assisted development environment (e.g., Cursor). While this environment provides good support for iterative code generation and refinement, the proposed method itself is not tied to any particular tool. Future work will investigate the applicability and performance of VCAWG across different development environments and LLM platforms to further validate its generality and robustness. 

#### **CRediT authorship contribution statement** 

**Hoang-Viet Tran:** Writing – review & editing, Writing – original draft, Visualization, Validation, Project administration, Methodology, Funding acquisition, Formal analysis, Conceptualization. **Thi-ThanhTruc Dang:** Writing – original draft, Software, Methodology, Conceptualization. **Duc-Anh Nguyen:** Writing – review & editing, Writing – original draft, Validation, Conceptualization. **Pham Ngoc Hung:** Writing – review & editing, Validation, Resources, Project administration, Methodology, Conceptualization. 

#### **Declaration of generative AI and AI-assisted technologies in the manuscript preparation process** 

During the preparation of this work, the author(s) used ChatGPT in order to revise English writing. After using this tool/service, the author(s) reviewed and edited the content as needed and take(s) full responsibility for the content of the published article. 

#### **Declaration of competing interest** 

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper. 

#### **Acknowledgments** 

This research was funded by the research project QG.25.09 of Vietnam National University, Hanoi. 

#### **Data availability** 

No data was used for the research described in the article. 

#### **References** 

- [1] J. Francu, P. Hnetynka, Automated code generation from system requirements in natural language, E Inform. Softw. Eng. J. 3 (1) (2009) 72–88, URL http://www. e-informatyka.pl/attach/e-Informatica_-_Volume_3/eInformatica2009Art5.pdf. 

- [2] J.P. Alfonso Hoyos, F. Restrepo-Calle, Automatic source code generation for webbased process-oriented information systems, in: Proc. of the 12th Int. Conf. on Eval. of Novel Approaches To Soft. Eng. - ENASE, INSTICC, SciTePress, 2017, pp. 103–113, http://dx.doi.org/10.5220/0006333901030113. 

- [3] S.-S. Yang, H.-J. Kim, N.-U. Lee, S.-C. Park, Design of automatic source code generation based on user pattern definition, in: Adv. in Comp. Sci. and Ubi. Comp., Springer Singapore, 2018, pp. 1434–1439. 

- [4] H. Chen, Design and implementation of automatic code generation method based on model driven, J. Phys.: Conf. Ser. 1634 (1) (2020) 012019, http: //dx.doi.org/10.1088/1742-6596/1634/1/012019. 

- [5] Y. Yang, X. Li, W. Ke, Z. Liu, Automated prototype generation from formal requirements model, IEEE Trans. Reliab. 69 (2) (2020) 632–656, http://dx.doi. org/10.1109/TR.2019.2934348. 

- [6] M. Alharbi, M. Alshayeb, Automatic code generation techniques: A systematic literature review, Autom. Softw. Eng. 33 (1) (2025) 4, http://dx.doi.org/10. 1007/s10515-025-00551-3. 

- [7] F.J. Budinsky, M.A. Finnie, J.M. Vlissides, P.S. Yu, Automatic code generation from design patterns, IBM Syst. J. 35 (2) (1996) 151–171, http://dx.doi.org/10. 1147/sj.352.0151. 

- [8] J. Tsay, C. Hylands, E. Lee, A code generation framework for Java componentbased designs, in: Proc. of the 2000 Int. Conf. on Comp., Arch., and Syn. for Emb. Sys., CASES ’00, Association for Computing Machinery, 2000, pp. 18–25, http://dx.doi.org/10.1145/354880.354884. 

- [9] S. Bhartacharyya, R. Leupers, P. Marwedel, Software synthesis and code generation for signal processing systems, IEEE Trans. Cir. Sys. II: Ana. Dig. Sig. Proc. 47 (9) (2000) 849–875, http://dx.doi.org/10.1109/82.868454. 

- [10] M. Völter, T. Stahl, J. Bettin, A. Haase, S. Helsen, Model-Driven Software Development: Technology, Engineering, Management, John Wiley & Sons, 2013. 

- [11] S. Bonfanti, A. Gargantini, A. Mashkoor, Design and validation of a C++ code generator from abstract state machines specifications, J. Soft.: Evol. Pro. 32 (2) (2020) e2205, http://dx.doi.org/10.1002/smr.2205, e2205 smr.2205. 

- [12] Z. Su, D. Wang, Y. Yang, Y. Jiang, W. Chang, L. Fang, W. Li, J. Sun, Code synthesis for dataflow-based embedded software design, IEEE Trans. Comput.Aided Des. Integr. Circuits Syst. 41 (1) (2022) 49–61, http://dx.doi.org/10.1109/ TCAD.2021.3055487. 

- [13] D. Yan, Z. Gao, Z. Liu, A closer look at different difficulty levels code generation abilities of ChatGPT, in: 38th IEEE/ACM Int. Conf. on Auto. Soft. Eng., 2023, pp. 1887–1898, http://dx.doi.org/10.1109/ASE56229.2023.00096. 

- [14] A. Ahmed, S. Azab, Y. Abdelhamid, Source-code generation using deep learning: A survey, in: N. Moniz, Z. Vale, J. Cascalho, C. Silva, R. Sebastião (Eds.), Prog. in Art. Int., 2023, pp. 467–482. 

- [15] A. Odeh, N. Odeh, A.S. Mohammed, A comparative review of AI techniques for automated code generation in software development: Advancements, challenges, and future directions, TEM J. 13 (1) (2024) 726–739. 

- [16] J. Mitchell, Y. Shaaban, Position: Vibe coding needs vibe reasoning: Improving vibe coding with formal verification, LMPL ’25, Association for Computing Machinery, 2025, pp. 84–90, http://dx.doi.org/10.1145/3759425.3763390. 

- [17] M. Chow, O. Ng, From technology adopters to creators: Leveraging AI-assisted vibe coding to transform clinical teaching and learning, Med. Teach. 47 (12) (2025) 1927–1929, http://dx.doi.org/10.1080/0142159X.2025.2488353, PMID: 40202513. 

13 

_H.-V. Tran et al._ 

_Journal of Computer Languages 88 (2026) 101403_ 

- [18] M. Fortes-Ferreira, M.S. Alam, P. Bazilinskyy, Vibe coding in practice: Building a driving simulator without expert programming skills, in: Adjunct Proc. of the 17th Int. Conf. on Auto. UI and Int. Veh. App., in: Auto. Adj. ’25, 2025, pp. 60–66, http://dx.doi.org/10.1145/3744335.3758482. 

- [19] J.G. Meyer, Vibe coding omics data analysis applications, J. Proteome Res. (2026) http://dx.doi.org/10.1021/acs.jproteome.5c00984, PMID: 41492971. 

- [20] C. Guo, H. Yan, C. Chen, X. Li, H. Yang, Y. Yan, Automatic code generation method for building a co-simulation platform integrating building automatic systems and EnergyPlus, Energy Build. 351 (2026) 116667, http://dx.doi.org/ 10.1016/j.enbuild.2025.116667. 

- [21] S. Madan, S. Surabiyil Bindu, V. Potluri, Accessibility heuristics for vibe coding interfaces, in: Proc. of the 27th Int. ACM SIGACCESS Conf. on Comp. and Acce., ASSETS ’25, Association for Computing Machinery, 2025, http://dx.doi.org/10. 1145/3663547.3759729. 

- [22] G. Kim, S. Yegge, D. Amodei, Vibe Coding: Building Production-Grade Software With GenAI, Chat, Agents, and Beyond, IT Revolution, 2025, URL https://books. google.com.vn/books?id=ktVcEQAAQBAJ. 

- [23] B. Uyanık, A. Sayar, Analysis and comparison of automatic code generation and transformation techniques on low-code platforms, in: Proc. of the 5th Int. Conf. on Soft. Eng. and Dev., ICSED ’23, Association for Computing Machinery, 2024, pp. 17–27, http://dx.doi.org/10.1145/3637792.3637795. 

- [24] V.H. Muthazhagu, S. B, Exploring the role of AI in web design and development: A voyage through automated code generation, in: 2024 International Conference on Intelligent and Innovative Technologies in Computing, Electrical and Electronics, IITCEE, 2024, pp. 1–8, http://dx.doi.org/10.1109/IITCEE59897. 2024.10467409. 

- [25] R. Wang, R. Cheng, D. Ford, T. Zimmermann, Investigating and designing for trust in AI-powered code generation tools, in: Proc. of the 2024 ACM Conf. on Fair., Acc., and Trans., FAccT ’24, Association for Computing Machinery, 2024, pp. 1475–1493, http://dx.doi.org/10.1145/3630106.3658984. 

- [26] F.F. Xu, B. Vasilescu, G. Neubig, In-IDE code generation from natural language: Promise and challenges, ACM Trans. Softw. Eng. Methodol. 31 (2) (2022) http://dx.doi.org/10.1145/3487569. 

14