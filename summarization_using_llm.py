import openai
import os

# Initialize OpenAI client with your API key
client = openai.OpenAI(api_key='')# <-- insert your OpenAI API key here

# Directories for input text files and output summaries
INPUT_FOLDER = "data"
OUTPUT_FOLDER = "summaries"

def summarize_text_file(input_path, output_path):
    """
    Read text from input_path, send it to the OpenAI API for summarization,
    and write the resulting summary to output_path.
    """
    # Load the full text from the file
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()
    #Construct the summarization prompt, limiting output to 1200 characters
    prompt = (
        "Sumarizuj následující text **ne více než 1200 znaků**. "
        "Potřebujeme všechny relevantní informace jako adresa provozovny, nabízené služby, počet lůžek, poskytované terapie,technické vybavení a všechny informace, "
        "které jsou pro uživatele důležité, naopak takéty obecné řeči jsou zbytečné, pouze faktické věci, "
        "na základě kterých si může uživatel danou službu vybrat.\n\n"
        f"{text}"
    )
      # Call the Chat Completions API with GPT-4o-mini model
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1200, # cap the output length
        temperature=0.7 # control randomness/creativity
    )
     # Extract and clean up the summary text
    summary = response.choices[0].message.content.strip()

     # Truncate summary in case it exceeds character limit
    if len(summary) > 1200:
        summary = summary[:1200].rstrip() + "…"

    # Write the summary to the output file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(summary)
    print(f"Summary saved to {output_path}")

def summarize_all_files():
    """
    Process all .txt files in INPUT_FOLDER, summarize each,
    and save results into OUTPUT_FOLDER.
    """
    # Ensure output directory exists
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    # Loop through all .txt files in the input folder
    for filename in os.listdir(INPUT_FOLDER):
        if filename.lower().endswith('.txt'):
            input_path = os.path.join(INPUT_FOLDER, filename)
            output_path = os.path.join(OUTPUT_FOLDER, filename)
             # Summarize each file
            summarize_text_file(input_path, output_path)

# Entry point: run summarization on all files when executed as script
if __name__ == '__main__':
    summarize_all_files()