
# instruction.md

## Phidata – Vector Databases (SQL + Pinecone) & Agent Teams (Gemini)

---

## GLOBAL CONSTRAINTS (STRICT)

* Python **3.10+**
* Framework: **phidata**
* LLM Provider: **Google Gemini ONLY**
* Embeddings: **GeminiEmbedder ONLY**
* Vector DBs allowed:

  * **PgVector (Postgres)**
  * **SQLite Vector DB**
  * **Pinecone**
* Always valid, executable Python
* Explicit imports and parameters
* No OpenAI imports
* No LangChain chains
* No pseudocode
* No architectural commentary

---

## REQUIRED ENVIRONMENT VARIABLES

```bash
export GOOGLE_API_KEY="..."
export PINECONE_API_KEY="..."
```

Optional:

```bash
export PHI_DEBUG=true
export PHI_MONITORING=true
```

---

## REQUIRED DEPENDENCIES

```bash
pip install -U phidata google-generativeai sqlalchemy psycopg[binary] pgvector pinecone-client
```

SQLite only:

```bash
pip install -U phidata sqlalchemy
```

---

## GEMINI MODEL (MANDATORY)

```python
from phi.model.google import Gemini

model = Gemini(
    id="gemini-1.5-flash",
)
```

---

## GEMINI EMBEDDER (MANDATORY)

```python
from phi.embedder.google import GeminiEmbedder

embedder = GeminiEmbedder(
    model="models/text-embedding-004",
)
```

---

## VECTOR DATABASE OPTIONS

---

# OPTION 1: PGVECTOR (POSTGRES)

### DATABASE URL

```python
DB_URL = "postgresql+psycopg://ai:ai@localhost:5532/ai"
```

### VECTOR DB

```python
from phi.vectordb.pgvector import PgVector

vector_db = PgVector(
    db_url=DB_URL,
    table_name="documents",
    embedder=embedder,
)
```

---

# OPTION 2: SQLITE VECTOR DB

```python
from phi.vectordb.sqlite import SqliteVectorDb

vector_db = SqliteVectorDb(
    db_file="tmp/vectors.db",
    table_name="vectors",
    embedder=embedder,
)
```

---

# OPTION 3: PINECONE VECTOR DB (MANDATORY SYNTAX)

### INITIALIZE PINECONE DB

```python
from phi.vectordb.pineconedb import PineconeDB

vector_db = PineconeDB(
    name="phidata-index",
    dimension=768,
    metric="cosine",
    api_key=None,
    spec={
        "serverless": {
            "cloud": "aws",
            "region": "us-east-1",
        }
    },
    embedder=embedder,
    use_hybrid_search=False,
)
```

---

## KNOWLEDGE BASE (VECTOR DB REQUIRED)

### TEXT KNOWLEDGE

```python
from phi.knowledge.text import TextKnowledgeBase

knowledge_base = TextKnowledgeBase(
    texts=[
        "Agent teams coordinate work.",
        "Vector databases enable semantic search.",
    ],
    vector_db=vector_db,
)

knowledge_base.load(upsert=True)
```

---

### PDF URL KNOWLEDGE

```python
from phi.knowledge.pdf import PDFUrlKnowledgeBase

knowledge_base = PDFUrlKnowledgeBase(
    urls=["https://example.com/doc.pdf"],
    vector_db=vector_db,
)

knowledge_base.load(upsert=True)
```

---

## AGENT WITH VECTOR KNOWLEDGE (AGENTIC RAG)

```python
from phi.agent import Agent

agent = Agent(
    model=model,
    knowledge=knowledge_base,
    search_knowledge=True,
    read_chat_history=True,
    markdown=True,
    show_tool_calls=True,
)

agent.print_response("Query the vector database")
```

---

## AGENT STORAGE (OPTIONAL BUT ALLOWED)

### SQLITE STORAGE

```python
from phi.storage.agent.sqlite import SqlAgentStorage

storage = SqlAgentStorage(
    table_name="agent_sessions",
    db_file="tmp/agents.db",
)
```

### POSTGRES STORAGE

```python
from phi.storage.agent.postgres import PgAgentStorage

storage = PgAgentStorage(
    table_name="agent_sessions",
    db_url=DB_URL,
)
```

---

## AGENT WITH STORAGE + VECTOR DB

```python
agent = Agent(
    model=model,
    knowledge=knowledge_base,
    search_knowledge=True,
    storage=storage,
    add_history_to_messages=True,
    markdown=True,
)
```

---

## AGENT TEAMS (REQUIRED PATTERN)

---

### TEAM MEMBER AGENTS

```python
research_agent = Agent(
    name="VectorResearcher",
    role="Search vector database",
    model=model,
    knowledge=knowledge_base,
    search_knowledge=True,
)

analysis_agent = Agent(
    name="Analyzer",
    role="Analyze retrieved content",
    model=model,
)
```

---

### TEAM LEADER

```python
team_lead = Agent(
    name="TeamLead",
    model=model,
    team=[research_agent, analysis_agent],
    instructions=[
        "Delegate retrieval to VectorResearcher",
        "Delegate analysis to Analyzer",
        "Return a combined result",
    ],
    markdown=True,
    show_tool_calls=True,
)
```

---

### RUN TEAM

```python
team_lead.print_response(
    "Explain semantic search using vector databases",
    stream=True,
)
```

---

## TEAM + PINECONE (CANONICAL PATTERN)

```python
pinecone_researcher = Agent(
    name="PineconeResearcher",
    role="Query Pinecone vector database",
    model=model,
    knowledge=knowledge_base,
    search_knowledge=True,
)

writer = Agent(
    name="Writer",
    role="Write final response",
    model=model,
)

pinecone_team = Agent(
    name="PineconeTeam",
    model=model,
    team=[pinecone_researcher, writer],
    instructions=[
        "Search Pinecone for relevant documents",
        "Summarize results clearly",
    ],
    markdown=True,
)
```

---

## COPILOT ENFORCEMENT RULES

* Always use `Gemini` for `model`
* Always use `GeminiEmbedder` for embeddings
* Always explicitly select **one** vector DB
* Always call `.load(upsert=True)` on knowledge bases
* Pinecone must specify `dimension=768`
* Team members must include `name` and `role`
* Team leader must define `team=[...]`
* No OpenAI
* No mixed providers
* No implicit defaults

---

## DO NOT GENERATE

* Explanations
* Comments describing behavior
* Architecture sections
* Pseudocode
* LangChain chains
* OpenAI or Azure imports

---

## END OF INSTRUCTION
