import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI
import json
from tqdm import tqdm

file_path = 'data/extracted_harmonyos-references.json'
chroma_client = chromadb.PersistentClient(path="./chroma_db")

BAAI_ef = embedding_function=embedding_functions.OpenAIEmbeddingFunction(
                                                api_base="https://api.siliconflow.cn/v1/",
                                                api_key="sk-cjvcxzatusoigdfrvbrdlkflncunldopmrfvkdhhbhynzlpw",
                                                model_name="BAAI/bge-m3",
                                             )
def create():
    collection_1 = chroma_client.get_or_create_collection(name="HM_data_function_name", 
                                                embedding_function= BAAI_ef,)

    collection_2 = chroma_client.get_or_create_collection(name="HM_data_code", 
                                                embedding_function= BAAI_ef,)

    collection_3 = chroma_client.get_or_create_collection(name="HM_data_full_code",
                                                embedding_function= BAAI_ef,)
    
    return collection_1, collection_2, collection_3

def fullfill():
    collection_1, collection_2, collection_3 = create()
# Load the JSON file
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Process each entry in the JSON file
    for entry in tqdm(data):
        function_name = entry.get('function_name')
        import_info = entry.get('import_module')
        metadata = entry
        if entry.get('type') == "Reference":
            collection_3.add(
                documents=[entry.get('pre')],
                metadatas=[{"function_name": function_name if function_name else "default_function_name",
                            "import_info": import_info if import_info else "default_import_info",
                            "code": entry.get('pre') if entry.get('pre') else "default_code"}],
                ids=[str(entry.get('id', len(data)))]  # Use a unique ID for each entry
            )
        # Add the data to the collection
        # if function_name:
        #     collection_1.add(
        #         documents=[function_name],
        #         metadatas=[{"function_name": function_name if function_name else "default_function_name",
        #                     "import_info": import_info if import_info else "default_import_info",
        #                     "code": entry.get('pre') if entry.get('pre') else "default_code"}],
        #         ids=[str(entry.get('id', len(data)))]  # Use a unique ID for each entry
        #     )
        # if import_info:
        #     collection_2.add(
        #         documents=[import_info],
        #         metadatas=[{"function_name": function_name if function_name else "default_function_name",
        #                     "import_info": import_info if import_info else "default_import_info",
        #                     "code": entry.get('pre') if entry.get('pre') else "default_code"}],
        #         ids=[str(entry.get('id', len(data)))]  # Use a unique ID for each entry
        #     )
            
fullfill()