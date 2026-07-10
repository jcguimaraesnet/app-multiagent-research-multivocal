[Sitemap](https://medium.com/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40rubenszimbres%2Fcode-generation-using-retrieval-augmented-generation-langchain-861e3c1a1a53&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

[Medium Logo](https://medium.com/?source=post_page---top_nav_layout_nav-----------------------------------------)

Get app

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav------------------)

[Search](https://medium.com/search?source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40rubenszimbres%2Fcode-generation-using-retrieval-augmented-generation-langchain-861e3c1a1a53&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

![Unknown user](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

Langchain

Google Cloud Platform

Vertex AI

Code Generation

LLM

# Code Generation using Retrieval Augmented Generation + LangChain

[![Rubens Zimbres](https://miro.medium.com/v2/resize:fill:32:32/1*4g5XVksp8-oEHxR6Yc5mZQ.png)](https://medium.com/@rubenszimbres?source=post_page---byline--861e3c1a1a53---------------------------------------)

[Rubens Zimbres](https://medium.com/@rubenszimbres?source=post_page---byline--861e3c1a1a53---------------------------------------)

Follow

11 min read

·

Nov 15, 2023

259

1

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D861e3c1a1a53&operation=register&redirect=https%3A%2F%2Fmedium.com%2F%40rubenszimbres%2Fcode-generation-using-retrieval-augmented-generation-langchain-861e3c1a1a53&source=---header_actions--861e3c1a1a53---------------------post_audio_button------------------)

Share

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*65bzKvBX8gLUzyf63-L7bw.png)

In the article [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401), authors combine pre-trained parametric (implicit knowledge base pre-trained on a seq2seq model) and non-parametric memory (a dense vector index of Wikipedia) for language generation. This dense vector, embeddings, is accessed via a neural retriever, providing complimentary information for the trained seq2seq neural net.

The idea is simple: the pre-trained model was subject to backpropagation to learn the weights regarding its own knowledge base. If fine-tuned, it was trained on a specific domain knowledge. RAG provides additional information via retrieval to this pre-trained/fine-tuned model as a collection of embeddings (of a document) from where one retrieves the top K best options according to the user prompt to serve as a context for the LLM to answer the prompt.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*YvEfYAyAMW_NFd4p9QYfLA.png)

Source: [https://arxiv.org/abs/2005.11401](https://arxiv.org/abs/2005.11401)

The algorithm is composed by a retriever pη( _z_ \| _x_), select documents _z_ with parameters η that returns a top-K distributions of texts given a query _x_ and a generator that will return _y_ given the prompt, documents (context) and the previous 1:i−1 tokens:

![](https://miro.medium.com/v2/resize:fit:131/1*WvEcWmYLn2-MpoU27_poPw.png)

The retriever is given by generating embeddings for the user prompt ( _x_), and also for the documents ( _z_). This way, the top-K best matches in terms of proximity will be retrieved.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*16w6DYEth2Hsfuzur93N5g.png)

So, the probability of the output ( _y_), given the user prompt ( _x_), equals the sum of probabilities of documents given the prompt, times the product of probabilities of the output given the prompt, the documents retrieved, and the previous output sequence:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*N3HiQWYxTkjGqG8M4TZ48A.png)

If you already used BERT to generate embeddings, used Google Cloud Matching Engine with SCaNN for information retrieval and used Vertex AI _text@bison001_ to generate text, question answering, you already used all the tools necessary for Retrieval Augmented Generation (RAG). Also, you can use open source models for code generation and additional context embeddings.

You can develop this solution without LangChain, from scratch once you have the pieces (models/APIs and services), but LangChain provides a framework to simplify your work, and it also provides the memory feature to remember past prompts, in case you are building a notebook with generated blocks of code.

Ok, let’s start. Here are the tasks we will perform:

- List the python files (.py and .ipynb) in a given GitHub repo
- Extract code and markdown from these files
- Create chunks of code and generate embeddings for each code string
- Initialize the vector store ( [FAISS](https://arxiv.org/abs/1702.08734))
- Get different prompts to test
- Test RAG Chain and compare results

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*gySUsUi3MmJeIfBjWN6g2w.png)

In this article I will present two ways of generating code: first, submit the question straight to LangChain, that will use code-bison pretrained model + instructions to give a response, and second, RAG, that provides additional context, by generating embeddings of additional code and creates an index for retrieval. The top-K most similar embeddings to question embeddings will be used by LangChain + code-bison + instructions to generate a better response.

**RUNNING THE CODE**

First, we will install the necessary libraries:

```
pip install google-cloud-aiplatform==1.36.2 langchain==0.0.332  faiss-cpu==1.7.4 nbformat
```

Now, we will import LangChain, Vertex AI and Google Cloud libraries:

```
# LangChain
from langchain.llms import VertexAI
from langchain.embeddings import VertexAIEmbeddings

from langchain.schema import HumanMessage, SystemMessage
from langchain.schema.document import Document

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.text_splitter import Language

from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

import time
from typing import List
from pydantic import BaseModel

# Vertex AI
from google.cloud import aiplatform
import vertexai
from vertexai.language_models import CodeGenerationModel
```

Now, in order to use the Vertex AI LLM, we will define _locally_ the environment variables and the GitHub repo. If your notebook is in a Vertex AI instance or in Cloud Run, _os.environ_ is not necessary, _as long as_ the correspondent service account has the proper permissions.

```
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/home/user/key.json"

vertexai.init(project='your-project', location='us-central1')

GITHUB_TOKEN = "github_token_here" # @param {type:"string"}
GITHUB_REPO = "GoogleCloudPlatform/generative-ai" # @param {type:"string"}
```

Next, we will define the LLM to generate code, that was already pretrained in blocks of code. We use low temperature to reduce hallucinations.

```
#Code Generation

code_llm = VertexAI(
    model_name="code-bison@latest",
    max_output_tokens=2048,
    temperature=0.1,
    verbose=False,
    )
```

The next step is to create an index that will store the embeddings of all the code present in the files listed in the GitHub repo. Note that you will need a GitHub token for this step. Go to GitHub / Settings / Developer settings / Personal access tokens and generate your token:

```
import requests, time

#Crawls a GitHub repository and returns a list of all ipynb files in the repository
def crawl_github_repo(url,is_sub_dir,access_token = f"{GITHUB_TOKEN}"):

    ignore_list = ['__init__.py']

    if not is_sub_dir:
        api_url = f"https://api.github.com/repos/{url}/contents"
    else:
        api_url = url

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {access_token}"
                   }

    response = requests.get(api_url, headers=headers)
    response.raise_for_status()  # Check for any request errors

    files = []

    contents = response.json()

    for item in contents:
        if item['type'] == 'file' and item['name'] not in ignore_list and (item['name'].endswith('.py') or item['name'].endswith('.ipynb')):
            files.append(item['html_url'])
        elif item['type'] == 'dir' and not item['name'].startswith("."):
            sub_files = crawl_github_repo(item['url'],True)
            time.sleep(.1)
            files.extend(sub_files)

    return files
```

You will get a list of files that will be saved in a text file:

```
code_files_urls = crawl_github_repo(GITHUB_REPO,False,GITHUB_TOKEN)

# Write list to a file so you do not have to download each time
with open('/home/user/code_files_urls.txt', 'w') as f:
    for item in code_files_urls:
        f.write(item + '\n')
```

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*tlpmjCkjSSIavYQlBx3DDA.png)

Now, let’s extract the code contained in all of these URLs and save the formatted code in the text file:

```
import requests
import nbformat
import json

# Extracts the python code from an .ipynb file from github
def extract_python_code_from_ipynb(github_url,cell_type = "code"):
    raw_url = github_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")

    response = requests.get(raw_url)
    response.raise_for_status()  # Check for any request errors

    notebook_content = response.text

    notebook = nbformat.reads(notebook_content, as_version=nbformat.NO_CONVERT)

    python_code = None

    for cell in notebook.cells:
        if cell.cell_type == cell_type:
          if not python_code:
            python_code = cell.source
          else:
            python_code += "\n" + cell.source

    return python_code

# Extracts the python code from an .py file from github
def extract_python_code_from_py(github_url):
    raw_url = github_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")

    response = requests.get(raw_url)
    response.raise_for_status()  # Check for any request errors

    python_code = response.text

    return python_code

with open('/home/user/code_files_urls.txt') as f:
    code_files_urls = f.read().splitlines()
```

```
code_strings = []

for i in range(0, len (code_files_urls)):
    if code_files_urls[i].endswith(".ipynb"):
        content = extract_python_code_from_ipynb(code_files_urls[i],"code")
        doc = Document(page_content=content, metadata= {"url": code_files_urls[i], "file_index":i})
        code_strings.append(doc)
code_strings[0]
```

You will get a list of code strings:

```
Document(page_content='%pip install --upgrade google-cloud-discoveryengine humanize\n\nimport sys\n\nif "google.colab" in sys.modules:\n    from google.auth import default\n    from google.colab import auth\n\n    auth.authenticate_user()\n    creds, _ = default()\nelse:\n    # Otherwise, attempt to discover local credentials as described on https://cloud.google.com/docs/authentication/application-default-credentials\n    pass\n\nimport humanize\nimport time\nimport re\nfrom typing import List, Optional\n\nfrom google.api_core.client_options import ClientOptions\nfrom google.cloud import discoveryengine_v1beta as discoveryengine\n\n\ndef _call_list_documents(\n    project_id: str, location: str, datastore_id: str, page_token: Optional[str] = None\n) -> discoveryengine.ListDocumentsResponse:\n    """Build the List Docs Request payload."""\n    client_options = (\n        ClientOptions(\n            api_endpoint=f"{location}-discoveryengine.googleapis.com")\n        if location != "global"\n        else None\n    )\n    client = discoveryengine.DocumentServiceClient(\n        client_options=client_options)\n\n    request = discoveryengine.ListDocumentsRequest(\n        parent=client.branch_path(\n            project_id, location, datastore_id, "default_branch"\n        ),\n        page_size=1000,\n        page_token=page_token,\n    )\n\n    return client.list_documents(request=request)\n\n\ndef list_documents(\n    project_id: str, location: str, datastore_id: str, rate_limit: int = 1\n) -> List[discoveryengine.Document]:\n    """Gets a list of docs in a datastore."""\n\n    res = _call_list_documents(project_id, location, datastore_id)\n\n    # setup the list with the first batch of docs\n    docs = res.documents\n\n    while res.next_page_token:\n        # implement a rate_limit to prevent quota exhaustion\n        time.sleep(rate_limit)\n\n        res = _call_list_documents(\n            project_id, location, datastore_id, res.next_page_token\n        )\n        docs.extend(res.documents)\n\n    return docs\n\n\ndef list_indexed_urls(\n    docs: Optional[List[discoveryengine.Document]] = None,\n    project_id: str = None,\n    location: str = None,\n    datastore_id: str = None,\n) -> List[str]:\n    """Get the list of docs in data store, then parse to only urls."""\n    if not docs:\n        docs = list_documents(project_id, location, datastore_id)\n    urls = [doc.content.uri for doc in docs]\n\n    return urls\n\n\ndef search_url(urls: List[str], url: str) -> None:\n    """Searches a url in a list of urls."""\n    for item in urls:\n        if url in item:\n            print(item)\n\n\ndef search_doc_id(\n    doc_id: str,\n    docs: Optional[List[discoveryengine.Document]] = None,\n    project_id: str = None,\n    location: str = None,\n    datastore_id: str = None,\n) -> None:\n    """Searches a doc_id in a list of docs."""\n    if not docs:\n        docs = list_documents(project_id, location, datastore_id)\n\n    doc_found = False\n    for doc in docs:\n        if doc.parent_document_id == doc_id:\n            doc_found = True\n            print(doc)\n\n    if not doc_found:\n        print(f"Document not found for provided Doc ID: `{doc_id}`")\n\n\ndef estimate_data_store_size(\n    urls: Optional[List[str]] = None,\n    docs: Optional[List[discoveryengine.Document]] = None,\n    project_id: str = None,\n    location: str = None,\n    datastore_id: str = None,\n) -> None:\n    """For Advanced Website Indexing data stores only."""\n    if not urls:\n        if not docs:\n            docs = list_documents(project_id, location, datastore_id)\n        urls = list_indexed_urls(docs=docs)\n\n    # Filter to only include website urls.\n    urls = list(filter(lambda x: re.search(r"https?://", x), urls))\n\n    if not urls:\n        print(\n            "No urls found. Make sure this data store is for websites with advanced indexing."\n        )\n        return\n\n    # For website indexing, each page is calculated as 500KB.\n    size = len(urls) * 500_000\n    print(f"Estimated data store size: {humanize.naturalsize(size)}")\n\n\nPENDING_MESSAGE = """\nNo docs found.\\n\\nIt\\\'s likely one of the following issues: \\n  [1] Your data store is not finished indexing. \\n  [2] Your data store failed indexing. \\n  [3] Your data store is for website data without advanced indexing.\\n\\n\nIf you just added your data store, it can take up to 4 hours before it will become available.\n"""\n\nproject_id = "YOUR_PROJECT_ID"\nlocation = "global"  # Options: "global", "us", "eu"\ndatastore_id = "YOUR_DATA_STORE_ID"\n\ndocs = list_documents(project_id, location, datastore_id)\n\nif len(docs) == 0:\n    print(PENDING_MESSAGE)\nelse:\n    SUCCESS_MESSAGE = f"""\n  Success! 🎉\\n\n  Your indexing is complete.\\n\n  Your index contains {len(docs)} documents.\n  """\n    print(SUCCESS_MESSAGE)\n\ndocs = list_documents(project_id, location, datastore_id)\ndocs[0]\n\ndocument_id = "000a98558b6fe9aef7992c9023fb7fdb"\n\nsearch_doc_id(document_id, docs=docs)\n\nurls = list_indexed_urls(docs=docs)\nurls[0]\n\nsearch_url(urls, "https://cloud.google.com/docs/terraform/samples")\n\nsearch_url(urls, "terraform")\n\nestimate_data_store_size(urls=urls)\n', metadata={'url': 'https://github.com/GoogleCloudPlatform/generative-ai/blob/main/conversation/data-store-status-checker/data_store_checker.ipynb', 'file_index': 0})
```

Then, we will chunk code strings. Note that there is a chunk overlap:

```
# Chunk code strings
text_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,chunk_size=2000, chunk_overlap=200
)
texts = text_splitter.split_documents(code_strings)
```

Now we initialize the Embedding API:

```
EMBEDDING_QPM = 100
EMBEDDING_NUM_BATCH = 5
embeddings = VertexAIEmbeddings(
    requests_per_minute=EMBEDDING_QPM,
    num_instances_per_batch=EMBEDDING_NUM_BATCH,
    model_name = "textembedding-gecko@latest"
)
```

Now that we have the embeddings ready, we will take this list of embedding vectors and create an Index locally, the same way we do with SCaNN in Matching Engine, using FAISS ( [https://github.com/facebookresearch/faiss](https://github.com/facebookresearch/faiss)):

```
# Create Index from embedded code chunks
db = FAISS.from_documents(texts, embeddings)
```

Note that there are other ways to create this vector store, like Matching Engine, AlloyDB and PostgreSQL using [pgvector](https://github.com/pgvector/pgvector) extension.

## Get Rubens Zimbres’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Remember me for faster sign in

Now we initialize the retriever to follow similarity of embeddings and return top-5 embeddings:

```
# Init your retriever.
retriever = db.as_retriever(
    search_type="similarity",  # Also test "similarity", "mmr"
    search_kwargs={"k": 5},)
```

Let’s run it:

User prompt:

```
user_question = "Create a python function that takes text input and returns embeddings using VertexAI textembedding-gecko model."
```

Let’s try it two ways: Zero Shot Prompt and RAG prompt:

Zero-shot prompt template: here the LLM will only consider your question and the existing knowledge the LLM was trained with:

```
# Zero Shot prompt template
prompt_zero_shot = """
    You are a proficient python developer. Respond with the syntactically correct & concise code for to the question below.

    Question:
    {question}

    Output Code :
    """

prompt_prompt_zero_shot = PromptTemplate(
input_variables=["question"],
template=prompt_zero_shot,
)
```

RAG template: here the LLM will consider your question, the existing knowledge the LLM was trained with and the context, that will be given by the RAG that checks the top-5 most similar embeddings in the Index ( _retriever_ variable) with the prompt:

```
# RAG template
prompt_RAG = """
    You are a proficient python developer. Respond with the syntactically correct code for to the question below. Make sure you follow these rules:
    1. Use context to understand the APIs and how to use it & apply.
    2. Do not add license information to the output code.
    3. Do not include colab code in the output.
    4. Ensure all the requirements in the question are met.

    Question:
    {question}

    Context:
    {context}

    Helpful Response :
    """

prompt_RAG_tempate = PromptTemplate(
    template=prompt_RAG, input_variables=["context", "question"]
)

qa_chain = RetrievalQA.from_llm(
    llm=code_llm, prompt=prompt_RAG_tempate, retriever=retriever, return_source_documents=True
)
```

Zero-shot prompt prediction:

```
response = code_llm.predict(text=user_question, max_output_tokens=2048, temperature=0.1)
print(response)
```

Generated code of zero-shot prompt: it’s possible to notice we have a useless _import os_:

```
import os
from google.cloud import aiplatform

# TODO: Replace the following with your own project ID.
PROJECT_ID = "YOUR_PROJECT_ID"

# TODO: Replace the following with your own model ID.
MODEL_ID = "YOUR_MODEL_ID"

# Create the AI Platform client.
aiplatform.init(project=PROJECT_ID)

# Get the model.
model = aiplatform.models.TextEmbeddingModel(model_id=MODEL_ID)

# Create the text input.
text_input = "This is a sample text."

# Get the embeddings.
embeddings = model.predict(text_input)

# Print the embeddings.
print(embeddings)
```

RAG prompt:

```
results = qa_chain({"query": user_question})
print(results["result"])
```

Generated code for RAG prompt:

```
def get_embeddings_vertexai(texts):
    """Gets embeddings for a list of texts using Vertex AI textembedding-gecko model.

    Args:
    texts: A list of strings.

    Returns:
    A list of lists of floats, where each inner list is the embedding for the
    corresponding text.
    """

    # Initialize the Vertex AI textembedding-gecko model.
    model = TextEmbeddingModel.from_pretrained("textembedding-gecko@latest")

    # Get the embeddings for the texts.
    embeddings = model.get_embeddings(texts)

    # Return the embeddings.
    return embeddings
```

Now, let’s test the knowledge base in which **code-bison** was trained. I will ask to generate the code of a function that sums two variables, something that is not contained in the .ipynb files of the GitHub we used for RAG:

```
user_question = "Create a python function that sums two variables a and b."

response = code_llm.predict(text=user_question, max_output_tokens=2048, temperature=0.1)
print(response)
```

```
def sum_two_variables(a, b):
  """
  This function sums two variables.

  Args:
    a: The first variable.
    b: The second variable.

  Returns:
    The sum of the two variables.
  """

  return a + b
```

It works ! Now, let’s generate the code for the sum and run this code with two variable values:

```
user_question = "Create a python function that sums two variables a and b. Then, run this function with a=2 and b=7"

response = code_llm.predict(text=user_question, max_output_tokens=2048, temperature=0.1)
print(response)
```

```
def sum_two_variables(a, b):
  """Sums two variables.

  Args:
    a: The first variable.
    b: The second variable.

  Returns:
    The sum of the two variables.
  """

  return a + b

if __name__ == "__main__":
  a = 2
  b = 7
  print(sum_two_variables(a, b))

... 9
```

Even better! These outputs prove that **code-bison** was pretrained in a dataset of codes, and we don’t need RAG to answer this prompt.

Besides, you can split the two requests (Python code for sum, add 2 and 7) into different prompts, using LangChain memory, what is super simple:

```
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

# Create a memory object
memory = ConversationBufferMemory()

# Create a conversation chain
chain = ConversationChain(llm=code_llm, memory=memory)

# Respond to the user
chain.predict(input='Create a python function that sums two variables a and b.')
chain.predict(input='Now, run this function with a=2 and b=7 and give me only the result')

' 9'
```

This means that you can develop your own ChatGPT — Duet AI code companion. For instance, if you are developing a PyTorch notebook, you can RAG the PyTorch GitHub repo to get a code companion specifically for your needs.

There are many possibilities for improvement and model tuning in RAG:

- change the VertexAI model type (code-bison, code-gecko or codechat-bison)
- change the VertexAI model temperature and max\_output\_tokens
- change the size and quality of the context documents
- change the chunk\_size in TextSplitter
- change chunk\_overlap in TextSplitter
- change the type of model for embeddings generation
- do user prompt engineering
- change model directions syntax
- change K in the top-K most similar documents for context

As you can see, it’s a beautiful solution whose hyperparameters should be set according to the specificity of the problem being approached.

For more notebooks about Generative AI, access [Google Cloud Generative AI Github](https://github.com/googleCloudPlatform/generative-ai).

**REFERENCES:**

**Announcing ScaNN: Efficient Vector Similarity Search** [https://blog.research.google/2020/07/announcing-scann-efficient-vector.html?m=1](https://blog.research.google/2020/07/announcing-scann-efficient-vector.html?m=1)

**FAISS: Billion-scale similarity search with gpus**. Jeff Johnson, Matthijs Douze, and Hervé Jégou. arXiv preprint arXiv:1702.08734, 2017. URL [https://arxiv.org/abs/1702.08734](https://arxiv.org/abs/1702.08734)

**Kaggle notebook: Two Towers Recommender in Tensorflow/Keras — Training and Deployment.** [https://www.rubenszimbres.phd/kaggle-sprint](https://www.rubenszimbres.phd/kaggle-sprint)

**Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks**. Lewis et al. arXiv preprint arXiv:2005.1140, 2020. URL [https://arxiv.org/abs/2005.11401](https://arxiv.org/abs/2005.11401)

**Train and Deploy Google Cloud’s Two Towers Recommender** [https://medium.com/p/3ae5c29891af](https://medium.com/p/3ae5c29891af)

**\*Google ML Developer Programs team supported this work by providing Google Cloud Credit**

[Langchain](https://medium.com/tag/langchain?source=post_page---footer_tags--861e3c1a1a53---------------------------------------)

[Google Cloud Platform](https://medium.com/tag/google-cloud-platform?source=post_page---footer_tags--861e3c1a1a53---------------------------------------)

[Vertex AI](https://medium.com/tag/vertex-ai?source=post_page---footer_tags--861e3c1a1a53---------------------------------------)

[Code Generation](https://medium.com/tag/code-generation?source=post_page---footer_tags--861e3c1a1a53---------------------------------------)

[LLM](https://medium.com/tag/llm?source=post_page---footer_tags--861e3c1a1a53---------------------------------------)

[![Rubens Zimbres](https://miro.medium.com/v2/resize:fill:48:48/1*4g5XVksp8-oEHxR6Yc5mZQ.png)](https://medium.com/@rubenszimbres?source=post_page---post_author_info--861e3c1a1a53---------------------------------------)

[![Rubens Zimbres](https://miro.medium.com/v2/resize:fill:64:64/1*4g5XVksp8-oEHxR6Yc5mZQ.png)](https://medium.com/@rubenszimbres?source=post_page---post_author_info--861e3c1a1a53---------------------------------------)

Follow

[**Written by Rubens Zimbres**](https://medium.com/@rubenszimbres?source=post_page---post_author_info--861e3c1a1a53---------------------------------------)

[1.5K followers](https://medium.com/@rubenszimbres/followers?source=post_page---post_author_info--861e3c1a1a53---------------------------------------)

· [83 following](https://medium.com/@rubenszimbres/following?source=post_page---post_author_info--861e3c1a1a53---------------------------------------)

I’m an ML Engineer and Google Developer Expert in ML and GCP. I love studying NLP algos, LLMs and Cloud Infra. CompTIA Security +. PhD. [www.rubenszimbres.phd](http://www.rubenszimbres.phd/)

Follow

[Help](https://help.medium.com/hc/en-us?source=post_page-----861e3c1a1a53---------------------------------------)

[Status](https://status.medium.com/?source=post_page-----861e3c1a1a53---------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----861e3c1a1a53---------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----861e3c1a1a53---------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----861e3c1a1a53---------------------------------------)

[Store](https://medium.com/store)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----861e3c1a1a53---------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----861e3c1a1a53---------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----861e3c1a1a53---------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----861e3c1a1a53---------------------------------------)

reCAPTCHA

Recaptcha requires verification.

protected by **reCAPTCHA**