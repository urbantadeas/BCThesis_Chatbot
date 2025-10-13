# Implementation of a chatbot using the Retrieval Augmented Generation principle to support caregivers of the elderly in the Czech Republic
Czech Technical University in Prague  
Faculty of Nuclear Sciences and Physical Engineering  
Department of Mathematics  
Applied Informatics  
Tadeas Urban

This repository contains the implementation of my bachelor thesis project focused on developing a user-friendly chatbot that helps elderly people, caregivers, and relatives easily find suitable care homes in the Czech Republic. Addressing the complexity of the official MoLSA/MPSV care home registry, the system uses LLMs and Retrieval-Augmented Generation (RAG) to enable natural, semantic search.

Read the bachelor thesis with the reviews [here](https://dspace.cvut.cz/handle/10467/126527?locale-attribute=en).

Results of my testing could be found in the [`/results`](\results) folder. For better understanding, please refer to the thesis.


If you have any questions or feedback, feel free to reach out at urbantad@fjfi.cvut.cz.
<br><br>
<br><br>
> [!IMPORTANT]
> This guide explains how to set up the chatbot project. Please follow the steps below. 

## Install Dependencies
First, install the required Python packages. Run the following command in your terminal:

```pip install -r requirements.txt```

## Running the Existing Project
If you want to use the chatbot with the provided data (`/data_2` and `/summary_2`):
1.  Open the file `main.py`. 
2.  On lines 18 to 21, enter your OpenAI API key, LangChain API key, and the name of your LangSmith project.
3.  Run the `main.py` script.

## Creating a New Project
If you want to create a new project with your own data, follow these steps:
###  1. File Scraper Manager
1.  Open the `file_scraper_manager.py` script.
2.  Set the location of your main (master) folder in the variable `base_folder`. This is where all data will be saved.
3.  If you want to change the number of establishment’s folders created (for storing detailed information and documents), update the variable `created_folders` to the desired number (lines 8 to 26).
4.  Run the file_scraper_manager.py script.

###  2. File Migration Manager
1.  Open the `file_migration_manager.py` script.
2.  Set the location of your master directory (line 7).
3.  Add the location of `sluzba_ids.json` (this file should be in your master directory) on line 8.
4.  Run the `file_migration_manager.py` script.

### 3. Summarization using LLM
1.  Open the `summarization_using_llm.py` script.
2.  Enter your OpenAI API key on line 5.
3.  Run the `summarization_using_llm.py` script.

### 4. Embedding & Creation of Vector Database
1.  Open the `embedding_and_vector_database.py` script.
2.  Insert your OpenAI API key on line 7.
3.  Delete all contents inside the `/db` folder.
4.  Run the `embedding_and_vector_database.py` script.

### 5. Chatbot
1.  Open `main.py` script.
2.  Insert your OpenAI API key, LangChain API key, and the name of your LangSmith project on lines 18 to 21.
3.  Run the `main.py` script.
