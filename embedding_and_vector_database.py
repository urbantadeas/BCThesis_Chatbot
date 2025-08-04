from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
import os

# --- API KEYS ---
os.environ["OPENAI_API_KEY"] = ""  # <-- insert your OpenAI key here
os.environ["LANGCHAIN_TRACING_V2"] = "true"

#Paths for input text files and persistent vector DB
txt_path = "./summaries" # Directory containing .txt summaries
db_dir = "./db" # Base directory for database storage. Before creating embedding please delete the inside of the db folde 
persistent_directory = os.path.join(db_dir, "chroma_db_with_metadata") # Path to store Chroma DB

# Display the configured directories
print(f"Input InputDocumentsData directory: {txt_path}")
print(f"Persistent directory: {persistent_directory}")


# ---------------------------------------------
# Load text documents and attach metadata
# ---------------------------------------------


 # List all text files in the directory
source_documents_files = [f for f in os.listdir(txt_path) if f.endswith(".txt")]

# Read the text content from each file and store it with metadata
# Walk through txt_path and find all .txt files
documents = []
for root, dirs, files in os.walk(txt_path):
    for file in files:
        if file.endswith(".txt"):
            file_path = os.path.join(root, file)
            # Use the containing folder name as a tag
            subdirectory_name = os.path.basename(root)
            # Load the file into a LangChain Document
            loader = TextLoader(file_path, encoding='utf-8')
            input_data_docs = loader.load()
            # Add metadata: source filename and tag
            for doc in input_data_docs:
                # Add metadata with TAG (subdirectory name) and source file
                doc.metadata = {
                    "source": file,
                    "tag": subdirectory_name
                }
                documents.append(doc)


  

    docs = documents

    # Display information about the split documents
    print("\n--- Document Chunks Information ---")
    print(f"Number of document chunks: {len(docs)}")

    # ---------------------------------------------
    # Generate embeddings and build vector store
    # ---------------------------------------------

    # Create embeddings
    print("\n--- Creating embeddings ---")
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small" # Specify the embedding model
    )  # Update to a valid embedding model if needed
    print("\n--- Finished creating embeddings ---")

    # Create the vector store and persist it
    print("\n--- Creating and persisting vector store ---")
    # Build Chroma vector store from documents and save to disk
    db = Chroma.from_documents(
        docs, embeddings, persist_directory=persistent_directory)
    print("\n--- Finished creating and persisting vector store ---")
