import os
import fitz  # PyMuPDF
import json
import requests

# Configuration
#Your master directory
base_folder = "" 
contact_base_url = "https://www.mpsv.cz/api/api-gateway/rest/adresy/spojeni"
pdf_base_url = "https://www.mpsv.cz/api/agportal-server/rest/documents/"
search_url = "https://www.mpsv.cz/api/api-gateway/rest/registr-poskytovatelu/hledani"
version_param = "v=73246d599443799b0de33398482e44f4"
support_folder = os.path.join(base_folder, "Support")
response_data_path = os.path.join(base_folder, "masterdataset.json")

#Type of service / Druh socialni sluzby
service_type_id = 3847 #Domov pro seniory

#number of downloaded facilites for response_data.json
number_of_facilities = 600  # Fetch up to  600 results

#Pagination settings
chunk_size = 10

#number of created folders
created_folders = 600 # Limit to first 3 services for brevity, up to  600 folders



# Headers for requests
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0.1 Safari/605.1.15',
}

#

# Support data URLs
support_urls = {
    "typ_kapacity_data.json": "https://www.mpsv.cz/api/ciselniky/rest/ciselniky/TypKapacitySocialniSluzby/polozky?jazyk=cs&v=73246d599443799b0de33398482e44f4",
    "forma_pravni_data.json": "https://www.mpsv.cz/api/ciselniky/rest/ciselniky/FormaPravniSubjektivity/polozky?jazyk=cs&v=73246d599443799b0de33398482e44f4",
    "den_v_tydnu_data.json": "https://www.mpsv.cz/api/ciselniky/rest/ciselniky/DenVTydnu/polozky?jazyk=cs&v=73246d599443799b0de33398482e44f4",
    "typ_spojeni_data.json": "https://www.mpsv.cz/api/ciselniky/rest/ciselniky/TypSpojeni/polozky?jazyk=cs&v=73246d599443799b0de33398482e44f4",
    "forma_soc_sluzby_data.json": "https://www.mpsv.cz/api/ciselniky/rest/ciselniky/FormaSocSluzby/polozky?jazyk=cs&v=73246d599443799b0de33398482e44f4",
    "cilova_skupina_osoby_data.json": "https://www.mpsv.cz/api/ciselniky/rest/ciselniky/CilovaSkupinaOsoby/polozky?jazyk=cs&v=73246d599443799b0de33398482e44f4",
    "vekova_skupina_osoby_data.json": "https://www.mpsv.cz/api/ciselniky/rest/ciselniky/VekovaSkupinaOsoby/polozky?jazyk=cs&v=73246d599443799b0de33398482e44f4",
    "druh_socialni_sluzby_data.json": "https://www.mpsv.cz/api/ciselniky/rest/ciselniky/DruhSocialniSluzby/polozky?jazyk=cs&v=73246d599443799b0de33398482e44f4",
    "kraje_data.json": "https://www.mpsv.cz/api/adresy/rest/kraje?v=73246d599443799b0de33398482e44f4"
}

# Create necessary directories
os.makedirs(support_folder, exist_ok=True)
os.makedirs(base_folder, exist_ok=True)

# Fetch and save support data
for filename, url in support_urls.items():
    try:
        response = requests.get(url, headers=headers, timeout=60)
        response.raise_for_status()
        data = response.json()
        with open(os.path.join(support_folder, filename), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Support data saved: {filename}")
    except Exception as e:
        print(f"Failed to fetch support data {filename}: {e}")

# Full Payload Template
payload_template = {
    "index": ["registr-poskytovatelu"],
    "pagination": {
        "start": 0,
        "count": chunk_size,
        "order": ["-id"]
    },
    "query": {
        "must": [
            {
                "matchAny": {
                    "field": "druhSocialniSluzbyId",
                    "query": [service_type_id]
                }
            },
            {
                "nested": {
                    "path": "_filtr",
                    "filter": {
                        "must": [
                            {
                                "should": [
                                    {
                                        "must": [
                                            {"match": {"field": "poskytovaniSluzbyOd", "query": None}},
                                            {"match": {"field": "poskytovaniSluzbyDo", "query": None}}
                                        ]
                                    },
                                    {
                                        "must": [
                                            {"match": {"field": "poskytovaniSluzbyOd", "query": None}},
                                            {"range": {"field": "poskytovaniSluzbyDo", "gte": "2024-10-21"}}
                                        ]
                                    },
                                    {
                                        "must": [
                                            {"range": {"field": "poskytovaniSluzbyOd", "lte": "2024-10-21"}},
                                            {"match": {"field": "poskytovaniSluzbyDo", "query": None}}
                                        ]
                                    },
                                    {
                                        "must": [
                                            {"range": {"field": "poskytovaniSluzbyOd", "lte": "2024-10-21"}},
                                            {"range": {"field": "poskytovaniSluzbyDo", "gte": "2024-10-21"}}
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        ]
    }
}

# Fetch masterdataset.json
all_data = []
for start in range(0, number_of_facilities, chunk_size):  # Fetch up to  600 results
    payload_template['pagination']['start'] = start
    try:
        response = requests.post(search_url, headers=headers, json=payload_template, timeout=60)
        response.raise_for_status()
        data = response.json()
        if 'list' in data:
            all_data.extend(data['list'])
        else:
            print(f"Unexpected data format: {data}")
            break
    except Exception as e:
        print(f"Failed to fetch data at start={start}: {e}")
        break

# Save response_data.json
with open(response_data_path, 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False, indent=4)
print(f"masterdataset.json saved to {response_data_path}")

# Process services
for service in all_data[:created_folders]:  # Limit to first 3 services for brevity
    service_id = service['sluzba']['id']
    service_folder = os.path.join(base_folder, str(service_id))
    contact_folder = os.path.join(service_folder, "Contact")
    documents_folder = os.path.join(service_folder, "Documents")
    os.makedirs(contact_folder, exist_ok=True)
    os.makedirs(documents_folder, exist_ok=True)

    # Fetch and save contact_info.json
    contact_url = f"{contact_base_url}?subjektId={service_id}&typSubjektu=SocialniSluzba&v={version_param}"
    try:
        contact_response = requests.get(contact_url, headers=headers, timeout=60)
        contact_response.raise_for_status()
        contact_data = contact_response.json()
        with open(os.path.join(contact_folder, "contact_info.json"), 'w', encoding='utf-8') as f:
            json.dump(contact_data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Failed to fetch contact_info.json for service ID {service_id}: {e}")

    # Fetch zarizeni_contact_info.json
    sluzby_v_zarizeni = service['sluzba'].get('sluzbyVZarizeni', [])
    if sluzby_v_zarizeni:
        id_zarizeni = sluzby_v_zarizeni[0].get('idZarizeni')
        if id_zarizeni:
            zarizeni_contact_url = f"{contact_base_url}?subjektId={id_zarizeni}&typSubjektu=ZarizeniSocialniSluzby&v={version_param}"
            try:
                zarizeni_response = requests.get(zarizeni_contact_url, headers=headers, timeout=60)
                zarizeni_response.raise_for_status()
                zarizeni_data = zarizeni_response.json()
                with open(os.path.join(contact_folder, "zarizeni_contact_info.json"), 'w', encoding='utf-8') as f:
                    json.dump(zarizeni_data, f, ensure_ascii=False, indent=4)
            except Exception as e:
                print(f"Failed to fetch zarizeni_contact_info.json for service ID {service_id}: {e}")

    # Fetch poskytovatel_contact_info.json
    poskytovatel = service.get('poskytovatel')
    if poskytovatel:
        poskytovatel_id = poskytovatel['id']
        poskytovatel_url = f"{contact_base_url}?subjektId={poskytovatel_id}&typSubjektu=PoskytovatelSocialniSluzbyFoNeboPo&v={version_param}"
        try:
            poskytovatel_response = requests.get(poskytovatel_url, headers=headers, timeout=60)
            poskytovatel_response.raise_for_status()
            poskytovatel_data = poskytovatel_response.json()
            with open(os.path.join(contact_folder, "poskytovatel_contact_info.json"), 'w', encoding='utf-8') as f:
                json.dump(poskytovatel_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Failed to fetch poskytovatel_contact_info.json for service ID {service_id}: {e}")

    # Download documents and save PDFs
    for attachment_key in ['popisyPersonalnihoZajisteni', 'popisyRealizacePoskytovaniSluzby', 'planyFinancnihoZajisteni']:
        for attachment in service['sluzba'].get(attachment_key, []):
            attachment_id = attachment.get('priloha')
            if attachment_id:
                pdf_url = f"{pdf_base_url}{attachment_id}/content"
                pdf_path = os.path.join(documents_folder, f"{attachment_key}_{attachment_id}.pdf")
                try:
                    pdf_response = requests.get(pdf_url, headers=headers, timeout=60)
                    pdf_response.raise_for_status()
                    with open(pdf_path, 'wb') as f:
                        f.write(pdf_response.content)
                    print(f"PDF saved: {pdf_path}")
                except Exception as e:
                    print(f"Failed to download PDF {attachment_id} for service ID {service_id}: {e}")


# Define the input and output file names
input_file_name = 'masterdataset.json'
output_file_name = 'sluzba_ids.json'

# Read and parse the JSON data from the input file
with open(input_file_name, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Extract the IDs from "sluzba"
sluzba_ids = [entry['sluzba']['id'] for entry in data]

# Save the IDs to a new JSON file
with open(output_file_name, 'w', encoding='utf-8') as output_file:
    json.dump(sluzba_ids, output_file, ensure_ascii=False, indent=4)

print(f"Extracted IDs saved to {output_file_name}")

# Process PDFs and extract text
json_file_path = os.path.join(base_folder, "sluzba_ids.json")
with open(json_file_path, "r") as file:
    sluzba_ids = json.load(file)

for sluzba_id in sluzba_ids:
    documents_folder = os.path.join(base_folder, str(sluzba_id), "Documents")
    if not os.path.exists(documents_folder):
        print(f"Documents folder not found for ID {sluzba_id}")
        continue

    for file_name in os.listdir(documents_folder):
        if file_name.endswith(".pdf"):
            pdf_path = os.path.join(documents_folder, file_name)
            doc = fitz.open(pdf_path)
            extracted_text = ""
            for page_num in range(len(doc)):
                page = doc[page_num]
                extracted_text += page.get_text()

            if extracted_text.strip():
                new_pdf_name = os.path.splitext(file_name)[0] + "_text.pdf"
            else:
                new_pdf_name = os.path.splitext(file_name)[0] + "_scan.pdf"

            new_pdf_path = os.path.join(documents_folder, new_pdf_name)
            os.rename(pdf_path, new_pdf_path)

            if extracted_text.strip():
                text_file_name = os.path.splitext(new_pdf_name)[0] + ".txt"
                text_file_path = os.path.join(documents_folder, text_file_name)
                with open(text_file_path, "w", encoding="utf-8") as text_file:
                    text_file.write(extracted_text)

            print(f"Processed: {new_pdf_path}")
