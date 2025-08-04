import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import logging

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableMap
from langsmith import Client

# --- API KEYS ---
# Set your environment variables for OpenAI, LangChain tracing, and LangSmith
os.environ["OPENAI_API_KEY"] = ""   # <-- insert your OpenAI API key
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "" # <-- insert your LangChain API key
os.environ["LANGSMITH_PROJECT"] = "" # <-- insert your LangSmith project ID

# Models configuration
LLM_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-small"

# --- Logging ---
# Configure root logger to show INFO messages
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Embeddings & Vector DB ---
# Initialize OpenAI embeddings
embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
# Initialize Chroma vector DB with a persistent directory
chroma_db = Chroma(
    persist_directory="./db/chroma_db_with_metadata",
    embedding_function=embeddings,
)
#Create a retriever to fetch top k=3 similar documents for queries
retriever = chroma_db.as_retriever(search_kwargs={"k": 3})

# --- Prompt template ---
# Custom template guiding the assistant to focus on social service recommendations
custom_prompt_template = """
# Cíl
Chovej se jako asistent pro výběr nejvhodnější sociální služby. Pokud už znáš věk osoby, její potřeby, zájmy a lokaci, odpověz rovnou; pokud něco chybí, zeptej se na to.

# Známá fakta:
{facts}

# Kontext (vyhledané dokumenty):
{context}

# Direktivy
- Bav se výhradně o tématu sociálních služeb a souvisejícím kontextu.
- **VŽDY** u každého doporučení **uveď kontaktní informace** (adresa, telefon, e-mail nebo web).
- Pokud dokumenty explicitně neuvádějí kontakt, doporuč, jak kontakt doplnit (např. „Kontaktujte recepci na +420 XXX XXX XXX“).
- Piš jako **markdown**, aby šlo výstup hezky vykreslit v JavaScriptovém okně.

# Historie a dotaz uživatele:
{question}
"""
# Create a PromptTemplate object with input variables
prompt = PromptTemplate(
    input_variables=["facts", "context", "question"],
    template=custom_prompt_template,
)

# --- RAG chain setup ---
# Initialize the Chat LLM with low temperature for consistency
llm = ChatOpenAI(model=LLM_MODEL, temperature=0.2)
# Compose a RunnableMap to fetch context, pass facts and question into the prompt, then call the LLM
rag_chain = (
    RunnableMap({
        # Fetch context: join page_content of top retrieved docs
        "context": lambda x: "\n".join(d.page_content for d in retriever.get_relevant_documents(x["query"])),
        "facts": lambda x: x["facts"],# pass facts string
        "question": lambda x: x["question"], # pass question string
    })
    | prompt # feed into prompt template
    | llm # invoke LLM
)

# --- Slot-filling schema for user facts ---
# Define a JSON schema to extract structured facts about the senior user
fact_schema = {
    "title": "SeniorInfoExtraction",
    "description": (
        "Extrahuj klíčová fakta o seniorovi: věk, bydliště, zájmy, potřeby, zdravotní stav a omezení. "
        "Pokud si nejsi jistý, vrať null."
    ),
    "type": "object",
    "properties": {
        "age": {"type": "integer"},
        "place_of_residence": {"type": "string"},
        "hobbies": {"type": "string", "description": "Koníčky, např. hudba."},
        "social_service_interest": {"type": "string"},
        "health_status": {"type": "string"},
        "medical_diagnosis": {"type": "string"},
        "life_limitations": {"type": "string"},
    },
}
# Wrap the LLM to produce structured output per the schema
structured_llm = llm.with_structured_output(schema=fact_schema)

# In-memory store for extracted user facts
user_facts = {k: None for k in fact_schema["properties"].keys()}
# Helper to create a concise facts string for prompts
def summarize_facts(facts: dict) -> str:
    parts = []
    if facts.get("age"):
        parts.append(f"{facts['age']} let")
    if facts.get("place_of_residence"):
        parts.append(f"bydlí v {facts['place_of_residence']}")
    if facts.get("hobbies"):
        parts.append(f"zájmy: {facts['hobbies']}")
    return ", ".join(parts) or "zatím žádné podrobnosti"
# Extract structured facts from user message
def extract_facts(text: str) -> dict:
    try:
        response = structured_llm.invoke(text)
        logger.info("Extracted facts: %s", response)
        return response or {}
    except Exception as e:
        logger.error("Extraction error: %s", e)
        return {}

# --- FastAPI setup ---
app = FastAPI()
# Enable CORS for all origins (adjust for production)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
#Serve static files from 'static' directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=FileResponse)
async def home():
    return FileResponse("static/index.html")

# Define request schema for chat endpoint
class ChatRequest(BaseModel):
    message: str
    history: list[str] = [] # prior messages for context

@app.post("/chat")
async def chat(req: ChatRequest):
    """
    Handle chat requests: extract facts, update memory, invoke RAG chain,
    and return a markdown-formatted recommendation.
    """
    global user_facts
    # 1) Extract and update new facts
    new = extract_facts(req.message)
    for k, v in new.items():
        if v is not None:
            user_facts[k] = v
    logger.info("User facts now: %s", user_facts)

    # 2) Build combined question with known facts and history
    facts_str = summarize_facts(user_facts)
    full_q = f"Známá fakta: {facts_str}\n" + "\n".join(req.history + [req.message])

    # 3) Invoke RAG chain with query, facts, and context
    result = rag_chain.invoke({
        "query": full_q,
        "facts": facts_str,
        "context": "",    # už je v RunnableMap
        "question": full_q,
    })

    # 4) Return the raw text response
    text = result.content if hasattr(result, "content") else str(result)
    return {"response": text}

@app.post("/reset")
async def reset():
    """Clear stored user facts."""
    for k in user_facts:
        user_facts[k] = None
    logger.info("Facts reset")
    return {"status": "facts reset"}

if __name__ == "__main__":
    # Run the FastAPI app with live reload on localhost:8000
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)