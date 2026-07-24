- [Home](https://learnopencv.com/ "Home")
- \>
- [Agentic AI](https://learnopencv.com/category/agentic-ai/ "Agentic AI")
- \>
- LangGraph: Building Self-Correcting RAG Agent for Code Generation

[Bhomik Sharma](https://learnopencv.com/author/bhomik/)

- on July 29, 2025

# LangGraph: Building Self-Correcting RAG Agent for Code Generation

Welcome back to our LangGraph series! In our previous post, we explored the fundamental concepts of LangGraph by building a Visual Web Browser Agent that could navigate, see, scroll, and summarize web pages. We saw how nodes, edges, state, and conditional routing come together to create intelligent workflows. Today, we’re taking it a step further. What

- [Agentic AI](https://learnopencv.com/category/agentic-ai/), [AI Art Generation](https://learnopencv.com/category/ai-art-generation/), [Computer Vision](https://learnopencv.com/category/computer-vision/), [Generative AI](https://learnopencv.com/category/generative-ai/), [Generative Models](https://learnopencv.com/category/generative-models/), [Hugging Face Transformers](https://learnopencv.com/category/hugging-face-transformers/), [Multimodal Models](https://learnopencv.com/category/generative-models/multimodal-models/), [Vision Language Models](https://learnopencv.com/category/generative-ai/vision-language-models/)

![](https://cdn.learnopencv.com/wp-content/uploads/2025/07/04081445/LangGraph_796.jpg)

- [Facebook](https://bigvision.ai/expert-ai-solution-builders?utm_source=lopcv&utm_medium=post-icon)

Welcome back to our LangGraph series! In our [previous post](https://learnopencv.com/langgraph-building-a-visual-web-browser-agent/ "previous post"), we explored the fundamental concepts of LangGraph by building a Visual Web Browser Agent that could navigate, see, scroll, and summarize web pages. We saw how **nodes**, **edges**, **state**, and **conditional routing** come together to create intelligent workflows.

Today, we’re taking it a step further. What if an agent needs to do more than just follow a predefined path? What if it needs to **try something, check if it worked, and if not, try again with improvements?** This is the essence of **self-correction** and **iterative behavior**, and LangGraph is perfectly designed for it.

In this article, we’ll dive into building a Diffusers Code Generation Agent using self correcting RAG agent. This agent’s task is to write Python code using the Hugging Face diffusers library. But here’s the twist: it will then attempt to _execute_ the code it generated. If the code fails, the agent will **reflect** on the error and use that insight to generate an improved version, looping until it succeeds or reaches a retry limit.

1. [Beyond One-Shot Generation](https://learnopencv.com/langgraph-self-correcting-agent-code-generation/#heading-1 "Beyond One-Shot Generation")
2. [The Self-Correcting Agent’s Blueprint](https://learnopencv.com/langgraph-self-correcting-agent-code-generation/#heading-2 "The Self-Correcting Agent's Blueprint")
3. [LangGraph Concepts (Advanced)](https://learnopencv.com/langgraph-self-correcting-agent-code-generation/#heading-3 "LangGraph Concepts (Advanced)")
1. [Agent State (AgentState)](https://learnopencv.com/langgraph-self-correcting-agent-code-generation/#heading-3.1 "Agent State (AgentState)")
2. [Structured Output with Pydantic](https://learnopencv.com/langgraph-self-correcting-agent-code-generation/#heading-3.2 "Structured Output with Pydantic")
3. [Retrieval Augmented Generation (RAG): Specialized Knowledge for LLM](https://learnopencv.com/langgraph-self-correcting-agent-code-generation/#heading-3.3 "Retrieval Augmented Generation (RAG): Specialized Knowledge for LLM")
4. [Different Types of Messages (BaseMessage and Subclasses)](https://learnopencv.com/langgraph-self-correcting-agent-code-generation/#heading-3.4 "Different Types of Messages (BaseMessage and Subclasses)")
5. [Nodes (The Agent’s Actions)](https://learnopencv.com/langgraph-self-correcting-agent-code-generation/#heading-3.5 "Nodes (The Agent's Actions)")
6. [Edges (The Control Flow Loop)](https://learnopencv.com/langgraph-self-correcting-agent-code-generation/#heading-3.6 "Edges (The Control Flow Loop)")
4. [Running the Agent](https://learnopencv.com/langgraph-self-correcting-agent-code-generation/#heading-4 "Running the Agent")
5. [Conclusion](https://learnopencv.com/langgraph-self-correcting-agent-code-generation/#heading-5 "Conclusion")
6. [References](https://learnopencv.com/langgraph-self-correcting-agent-code-generation/#heading-6 "References")

## Beyond One-Shot Generation

Large Language Models (LLMs) are incredibly powerful at generating code. You can ask them to write a script, and often, they’ll give you something impressive. However, generated code isn’t always perfect. It might have syntax errors, logical bugs, or simply not do what was intended.

For critical applications, a “one-shot” code generation isn’t enough. We need a feedback loop:

1. **Generate** a solution.
2. **Execute/Test** the solution.
3. **Evaluate** the result (did it work? did it error?).
4. If there’s an issue, **reflect** on the problem.
5. Use the reflection to **regenerate** a better solution.
6. Repeat.

This iterative process is naturally mapped by LangGraph’s ability to create cycles in its workflow.

## The Self-Correcting Agent’s Blueprint

Our Diffusers Code Generation Agent workflow consists of three main operational nodes and a crucial conditional router:

1. **Generate:** The LLM generates the initial code.
2. **Check Code:** Attempts to execute the generated code.
3. **Reflect:** If the code fails, the LLM reflects on the error to understand what went wrong.

These nodes form a self-correction loop. Here’s how it looks:

[![langgraph, code generation, rag, rag agent](https://cdn.learnopencv.com/wp-content/uploads/2025/07/04081513/agent_flow_diagram_self_correcting-1024x202.png)](https://cdn.learnopencv.com/wp-content/uploads/2025/07/04081513/agent_flow_diagram_self_correcting-scaled.png)

This diagram illustrates the core iterative cycle: generate, check, and if there’s an error, reflect and regenerate.

## LangGraph Concepts (Advanced)

Let’s explore how our rag\_agent.py script leverages LangGraph to implement this robust self-correction mechanism.

### Agent State (AgentState)

As we learned, the AgentState (TypedDict) is the central hub for all information in our graph. For this code generation agent, we need to track the conversation, the generated output, and crucial flags for our loop:

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11 | `from``typing``import``TypedDict, Annotated, Sequence`<br>`from``langchain_core.messages``import``BaseMessage``# Base class for all message types`<br>`from``langgraph.graph``import``add_messages``# The reducer function`<br>`class``AgentState(TypedDict):`<br>```error:``str``# Flag: "yes" if code failed, "no" if successful`<br>```messages: Annotated[Sequence[BaseMessage], add_messages]``# Full conversation history`<br>```output:``str``# The generated code snippet`<br>```description:``str``# Description of the generated code`<br>```explanation:``str``# Explanation of the generated code`<br>```iterations:``int``# Counter for retry attempts` |

- **error**: This simple string acts as a crucial flag, telling our conditional edge whether the last code execution was successful.
- **messages**: Once again, Annotated\[…, add\_messages\] is a powerful LangGraph reducer. It ensures that every BaseMessage object returned by a node (whether from a HumanMessage input, an AIMessage from the LLM, or a ToolMessage result) is automatically appended to this list, maintaining a full conversational history for the LLM to refer to.
- **output, description, explanation**: These fields store the structured output generated by our LLM, which we’ll discuss next.
- **iterations**: This integer counter is vital for preventing infinite loops in our self-correction process.

### Structured Output with Pydantic

Generating a raw text response from an LLM can be unstructured. For code generation, we need specific fields: the code itself, a description, and an explanation. This is achieved using **Pydantic models** and PydanticOutputParser from LangChain.

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9 | `from``pydantic``import``BaseModel`<br>`from``langchain.output_parsers``import``PydanticOutputParser`<br>`class``DiffuserCodeOutput(BaseModel):`<br>```description:``str`<br>```code:``str`<br>```explanation:``str`<br>`parser``=``PydanticOutputParser(pydantic_object``=``DiffuserCodeOutput)` |

We instruct the LLM in the system prompt to output a JSON string conforming to this DiffuserCodeOutput structure (parser.get\_format\_instructions()). The generate node then uses parser.parse(response\_text) to safely extract the description, code, and explanation into Python objects, which are then stored in our AgentState. This ensures reliable data extraction from the LLM’s raw text response.

### Retrieval Augmented Generation (RAG): Specialized Knowledge for LLM

While LLMs have vast general knowledge, they might not be up-to-date or highly specialized in very specific domains, like the nuances of a particular library’s API. This is where **Retrieval Augmented Generation (RAG)** comes into play.

RAG is a technique that allows an LLM to access, retrieve, and condition its response on specific, external, and up-to-date information. Instead of relying solely on the model’s pre-trained knowledge, we augment its capabilities by providing relevant context at inference time.

In our `rag_agent.py` script, this is implemented by:

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11 | `from``langchain_community.document_loaders.recursive_url_loader``import``RecursiveUrlLoader`<br>`from``bs4``import``BeautifulSoup as soup``# Used for parsing HTML content`<br>`url``=``'https://huggingface.co/docs/diffusers/stable_diffusion'`<br>`loader``=``RecursiveUrlLoader(`<br>```url``=``url,`<br>```max_depth``=``20``,``# How deep to go in finding linked pages`<br>```extractor``=``lambda``x: soup(x,``'html.parser'``).text``# Extract plain text from HTML`<br>`)`<br>`docs``=``loader.load()``# Load all documents from the URL`<br>`concatenated_content``=``"\n\n\n --- \n\n\n"``.join([doc.page_content``for``doc``in``docs])` |

- **Loading Documentation:** We use LangChain’s `RecursiveUrlLoader` to fetch content from the official Hugging Face diffusers documentation URL.
- **Concatenating Content:** The loaded documents (each doc containing page\_content) are then joined into a single, large string. The `concatenated_content` holds a significant portion of the `diffusers` library’s documentation.
- **Injecting into the System Prompt:** Finally, the below given chunk of specialized knowledge is injected directly into the `SystemMessage` that guides our LLM.

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19 | `system_message``=``SystemMessage(`<br>```content``=``f``"""<instructions>`<br>``You are an expert coding assistant specializing in the Hugging Face `diffusers` library.``<br>`Your task is to answer the user's question by generating a complete, executable Python script.`<br>``Here is the relevant `diffusers` documentation to help you:``<br>`-------`<br>`{concatenated_content}`<br>`-------`<br>`You must respond in a **JSON format** with the following fields:`<br>`{parser.get_format_instructions()}`<br>`Strictly follow this structure:`<br>``1. `description`: A one-line summary of what the script does.``<br>``2. `code`: A full working Python script (no markdown formatting).``<br>``3. `explanation`: A short paragraph explaining key parameters and decisions.``<br>`</instructions>"""`<br>`)` |

By providing this concatenated\_content in the system prompt, we are giving the LLM immediate access to highly relevant, up-to-date, and specific information about diffusers. This significantly improves the accuracy and relevance of the generated code, making the agent a true “expert” in this domain, even if the underlying LLM itself wasn’t explicitly trained on the very latest version of the documentation. This is a fundamental pattern for building knowledge-aware LLM applications.

### Different Types of Messages (BaseMessage and Subclasses)

Within your agent’s messages field (and often summaries if storing them as message objects), you’ll use different types of messages to represent different roles in a conversation or interaction. All message types inherit from BaseMessage:

- **HumanMessage**: Represents input directly from a human user. Used for the initial task, for providing error messages back to the LLM (as seen in code\_check), or any direct user interaction within the workflow.
- **AIMessage**: Represents output from an AI model (like an LLM). The LLM’s response to a prompt, including any generated text or requested tool calls, comes back as an AIMessage.
- **SystemMessage**: Provides global context or instructions to the AI model, often at the beginning of a conversation or at specific points in the workflow to guide the model’s behavior for the next step. Our system\_message containing the RAG context is a prime example.
- **ToolMessage**: Represents the _result_ of a tool call requested by the AI. (Less prominent in this specific rag\_agent.py as exec() is a direct Python function, not a LangChain tool, but crucial for agents using external APIs).

Understanding these message types is crucial for building agents that interact with LLMs, as models like those from Google Gemini or OpenAI expect inputs in this format and return outputs using AIMessage (which might contain tool calls).

### Nodes (The Agent’s Actions)

Each node is a Python function that processes the state and returns updates:

- **generate(state: AgentState) -> AgentState**:
  - This is where the LLM (gemini-2.5-pro) is invoked to produce the initial (or revised) code solution.
  - It receives the messages history (including previous errors if any), the iterations count, and the error flag.
  - If there was a previous error (state\[“error”\] == “yes”), it adds a HumanMessage like “Try again. Fix the code…” to prompt the LLM for correction.
  - It then calls llm.invoke(messages) and parses the structured output using our parser.
  - Updates the output, description, explanation, messages (via add\_messages), and iterations in the state.
- **code\_check(state: AgentState) -> AgentState**:
  - This node takes the code generated by the generate node.
  - It uses the built-in Python function exec() to attempt to run the Python code directly. exec() is powerful for dynamic code execution.
  - The exec() function takes the code string and a globals() dictionary. **globals() is a built-in Python function that returns the current global symbol table as a dictionary.** When exec() is called with globals(), it means that any variables, functions, or imports defined within the generated code will be executed within the _current script’s global scope_. This is important because if the generated code needs to, for example, import diffusers or define helper functions, it will do so in an environment where they can be accessed.
  - A try-except block is essential here to catch any runtime errors that occur when executing the generated code.
  - If exec() succeeds, the error flag in the state is set to “no”. If it fails, error is set to “yes”, and the exception message is added to the messages history as a `HumanMessage` for the LLM to see in the next iteration.

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7 | `try``:`<br>```exec``(code,``globals``())``# Attempt to run the code`<br>`except``Exception as e:`<br>```# If an error occurs during execution`<br>```print``(``"Code execution failed:"``, e)``# Log the error`<br>```messages.append(HumanMessage(content``=``f``"Your solution failed: {e}"``))``# Add error to messages`<br>```return``{``*``*``state,``"messages"``: messages,``"error"``:``"yes"``}``# Set error flag` |

- **reflect(state: AgentState) -> AgentState**:
  - This node is only hit if code\_check reports an error and the should\_continue router decides to reflect.
  - It adds a simple HumanMessage like “Reflect on the error and try again.” to the messages list.
  - It then invokes the LLM again, providing the full messages history (including the previous error details). The LLM’s response (its reflection) is added back to messages.
  - This step allows the LLM to “think” about the problem before attempting to regenerate code, potentially leading to better fixes by allowing it to explicitly process the error context.

### Edges (The Control Flow Loop)

The power of iteration lies in how we connect these nodes.

- workflow.add\_edge(START, “generate”): The graph begins by generating a solution.
- workflow.add\_edge(“generate”, “check\_code”): Always check the generated code after it’s generated.

Now, the crucial part: the conditional edge after check\_code.

- **should\_continue(state: AgentState) -> str**:
  - This is our **router function**. It examines the state to decide the next step.
  - It checks state\[“error”\] (did the code run successfully?) and state\[“iterations”\] (have we tried too many times?).
  - If error == “no” (success) OR iterations >= max\_iterations (retry limit reached), it returns “end”.
  - Otherwise (code failed and still within limits), it returns “reflect” (to go to the reflection step) or “generate” (to go straight to regeneration, if a specific flag is set for skipping reflection).
  - workflow.add\_edge(“reflect”, “generate”): This completes the self-correction loop! After reflecting on an error, the agent goes back to the generate node to produce a new version of the code.

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5 | `workflow.add_conditional_edges(``"check_code"``, should_continue, {`<br>```"end"``: END,``# If "end", the graph finishes`<br>```"reflect"``:``"reflect"``,``# If "reflect", go to the reflection node`<br>```"generate"``:``"generate"``# If "generate", go back to generation immediately (skipping reflection if needed)`<br>`})` |

This setup ensures that the agent will keep trying, learning from its mistakes, until it produces working code or reaches a predefined attempt limit.

## Running the Agent

**Download Code**
To easily follow along this tutorial, please download code by clicking on the button below. It's FREE!

Download Code

![](https://cdn.learnopencv.com/wp-content/uploads/2021/10/04093413/cropped-favicon-512x512-1-150x150.png)

Click here to download the source code to this post

To execute this agent, you provide an initial\_state with the system prompt, the user’s question, and initial iteration count.

|     |     |
| --- | --- |
| 1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20 | `initial_question``=``"generate image of an old man in 20 inference steps"`<br>`initial_state``=``{`<br>```"messages"``: [`<br>```system_message,`<br>```HumanMessage(content``=``initial_question)`<br>```],`<br>```"iterations"``:``0``,`<br>```"error"``: "",`<br>```"output"``: "",`<br>```"description"``: "",`<br>```"explanation"``: "",`<br>`}`<br>`solution``=``app.invoke(initial_state)``# Run the graph`<br>`# Print final structured output`<br>`print``(``"\n--- FINAL RESULT ---"``)`<br>`print``(``"📝 Description:\n"``, solution[``"description"``])`<br>`print``(``"\n📄 Code:\n"``, solution[``"output"``])`<br>`print``(``"\n🔍 Explanation:\n"``, solution[``"explanation"``])` |

When you run this agent, you’ll see a dynamic process:

1. The agent generates code.
2. It attempts to run the code.
3. If there’s a problem, you’ll see “Code execution failed” in your terminal, and the agent will then enter the reflection phase.
4. It then goes back to generate a new, hopefully corrected, version of the code.
5. This continues until the code runs successfully, at which point the final structured output is printed.

This demonstrates how LangGraph enables truly intelligent, resilient, and iterative agent behavior.

## Conclusion

In this second post of our LangGraph series, we moved beyond linear workflows to build a sophisticated **Self-Correcting Code Generation Agent**. We reinforced our understanding of **State** (including structured fields like output and control flags like error and iterations), learned how to leverage **Pydantic for structured LLM outputs**, and most importantly, explored how **Retrieval Augmented Generation (RAG)** empowers our agent with specialized knowledge. Finally, we saw how **conditional edges** are used to create powerful **iterative loops** that enable agents to learn from feedback and self-correct.

The ability to build agents that can try, fail, learn, and retry is a game-changer for reliability in AI applications. LangGraph provides the perfect framework to design and manage these complex, dynamic behaviors.

Experiment with this agent! Give it different code generation tasks, introduce artificial errors, and observe how it uses its internal loop to resolve issues. In our next installment, we’ll explore even more advanced LangGraph patterns!

### From idea to working model to real-time deployment

Big Vision takes computer vision projects through the full journey, not just the easy parts.

![Satya Mallick](https://opencv.org/university/wp-content/uploads/sites/4/2023/04/Dr-Satya.jpg)

**Satya Mallick** Founder - Big Vision & LearnOpenCV

[Talk to our Team](https://bigvision.ai/expert-ai-solution-builders/)

## **References**

- [LangGraph code generation with RAG and self correction blog post](https://langchain-ai.github.io/langgraph/tutorials/code_assistant/langgraph_code_assistant/ "LangGraph code generation with RAG and self correction blog post")
- [Diffusers Documentation](https://huggingface.co/docs/diffusers/index "Diffusers Documentation")

Was This Article Helpful?

## Subscribe & Download Code

If you liked this article and would like to download code (C++ and Python) and example images used in this post, please click here. In our newsletter, we share Computer Vision and AI tutorials and examples written in C++/Python, and Computer Vision and Machine Learning algorithms and news.

Download Example Code

[PrevPreviousInside Sinusoidal Position Embeddings: A Sense of Order](https://learnopencv.com/sinusoidal-position-embeddings/)

[NextObject Detection and Spatial Understanding with VLMs ft. Qwen2.5-VLNext](https://learnopencv.com/object-detection-with-vlms-ft-qwen2-5-vl/)

### [World Cup 2026 Offside Technology: AI, Computer Vision, and the Connected Ball](https://learnopencv.com/world-cup-2026-offside-technology/)

Learn how World Cup 2026 offside technology works with multi-camera tracking, AI pose estimation, digital

### [AI Aced JEE Advanced 2026. Can You Trust It to Teach You?](https://learnopencv.com/ai-aced-jee-advanced-2026-can-you-trust-it-to-teach-you/)

A look inside the multi-agent design that keeps an AI tutor grounded in its textbook

### [How to Fine-Tune YOLO26 for Safety Gear and Sign Language Detection](https://learnopencv.com/how-to-fine-tune-yolo26-for-safety-gear-and-sign-language-detection/)

Learn how to fine-tune YOLO26 on your own data. We build a construction PPE safety

![Satya Mallick](https://opencv.org/university/wp-content/uploads/sites/4/2023/04/Dr-Satya.jpg)

#### Satya Mallick, Ph.D.

Founder - Big Vision & LearnOpenCV

##### Are you struggling with your Computer Vision Product Development?

Helping startups and enterprises build and deploy scalable solutions that work in the real world.

[Schedule a Call](https://bigvision.ai/expert-ai-solution-builders?utm_source=lopcv&utm_medium=post)

#### Table of Contents

1. [Beyond One-Shot Generation](https://learnopencv.com/langgraph-self-correcting-agent-code-generation/#heading-1)

2. [The Self-Correcting Agent’s Blueprint](https://learnopencv.com/langgraph-self-correcting-agent-code-generation/#heading-2)

3. [LangGraph Concepts (Advanced)](https://learnopencv.com/langgraph-self-correcting-agent-code-generation/#heading-3)

4. [Running the Agent](https://learnopencv.com/langgraph-self-correcting-agent-code-generation/#heading-4)

5. [Conclusion](https://learnopencv.com/langgraph-self-correcting-agent-code-generation/#heading-5)

6. [References](https://learnopencv.com/langgraph-self-correcting-agent-code-generation/#heading-6)


Was This Article Helpful?

- [ai agents](https://learnopencv.com/tag/ai-agents/), [AI Development](https://learnopencv.com/tag/ai-development/), [Beginner Guide](https://learnopencv.com/tag/beginner-guide/), [Code Generation](https://learnopencv.com/tag/code-generation/), [diffusers](https://learnopencv.com/tag/diffusers/), [Google Gemini](https://learnopencv.com/tag/google-gemini/), [LangChain](https://learnopencv.com/tag/langchain/), [langgraph](https://learnopencv.com/tag/langgraph/), [LLM](https://learnopencv.com/tag/llm/), [Python](https://learnopencv.com/tag/python/), [RAG](https://learnopencv.com/tag/rag/), [Retrieval Augmented Generation](https://learnopencv.com/tag/retrieval-augmented-generation/), [Self-Correcting AI](https://learnopencv.com/tag/self-correcting-ai/), [Workflow Orchestration](https://learnopencv.com/tag/workflow-orchestration/)

## Read Next

[![How to Unlock 5 Vision Skills with the Moondream Cloud API](https://cdn.learnopencv.com/wp-content/uploads/2026/06/09072651/Moondream_Thumbnail-768x429.jpg)](https://learnopencv.com/moondream-cloud-api-one-image-five-grounded-vision-skills/)

[Computer Vision](https://learnopencv.com/category/computer-vision/)[Vision Language Models](https://learnopencv.com/category/generative-ai/vision-language-models/)

[Satya Mallick](https://learnopencv.com/author/spmallick/)
June 10, 2026

## [How to Unlock 5 Vision Skills with the Moondream Cloud API](https://learnopencv.com/moondream-cloud-api-one-image-five-grounded-vision-skills/)

Learn the Moondream Cloud API by running all five vision skills, caption, query, detect, point, and segment, on a single…

[![How to Master Qwen3-VL Embedding and Reranker for Multimodal Search](https://cdn.learnopencv.com/wp-content/uploads/2026/05/24231235/qwen3vl_thumbnail-768x429.jpg)](https://learnopencv.com/how-to-master-qwen3-vl-embedding-and-reranker-for-multimodal-search/)

[Deep Learning](https://learnopencv.com/category/deep-learning/)[LLMs](https://learnopencv.com/category/llms/)[Multimodal Models](https://learnopencv.com/category/generative-models/multimodal-models/)[Tutorial](https://learnopencv.com/category/tutorial/)[Vision Language Models](https://learnopencv.com/category/generative-ai/vision-language-models/)[VLMs](https://learnopencv.com/category/vlms/)

[Sudip Chakrabarty](https://learnopencv.com/author/sudip/)
May 25, 2026

## [How to Master Qwen3-VL Embedding and Reranker for Multimodal Search](https://learnopencv.com/how-to-master-qwen3-vl-embedding-and-reranker-for-multimodal-search/)

Master Qwen3-VL Embedding and Reranker for multimodal retrieval: text, image, video, mixed-modal queries, and a two-stage pipeline that boosts precision.

[![How to Master YOLOE: Real-Time Open-Vocabulary Detection Made Easy](https://cdn.learnopencv.com/wp-content/uploads/2026/05/08001059/thumbnail_YOLOE-768x429.jpg)](https://learnopencv.com/yoloe-tutorial-real-time-open-vocabulary-detection/)

[Computer Vision](https://learnopencv.com/category/computer-vision/)[Deep Learning](https://learnopencv.com/category/deep-learning/)[Image Processing](https://learnopencv.com/category/image-processing/)[Segmentation](https://learnopencv.com/category/segmentation/)[YOLO](https://learnopencv.com/category/yolo/)

[Sudip Chakrabarty](https://learnopencv.com/author/sudip/)
May 9, 2026

## [How to Master YOLOE: Real-Time Open-Vocabulary Detection Made Easy](https://learnopencv.com/yoloe-tutorial-real-time-open-vocabulary-detection/)

Learn YOLOE for real-time open-vocabulary object detection and instance segmentation in Python with Ultralytics — text, visual, and prompt-free modes.

## Subscribe to our Newsletter

Subscribe to our email newsletter to get the latest posts delivered right to your email.

Name

Email

Send

![](https://learnopencv.com/wp-content/uploads/2021/10/cropped-favicon-512x512-1.png)Click here to download the source code to this post