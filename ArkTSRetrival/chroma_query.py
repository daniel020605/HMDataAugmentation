import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI
import json
from tqdm import tqdm
import os

chroma_client = chromadb.PersistentClient(path="./chroma_db")

BAAI_ef = embedding_function=embedding_functions.OpenAIEmbeddingFunction(
                                                api_base="https://api.siliconflow.cn/v1/",
                                                api_key="sk-cjvcxzatusoigdfrvbrdlkflncunldopmrfvkdhhbhynzlpw",
                                                model_name="BAAI/bge-m3",
                                             )

name_collection = chroma_client.get_collection(name="HM_data_function_name", 
                                             embedding_function= BAAI_ef,)

code_collection = chroma_client.get_collection(name="HM_data_code", 
                                             embedding_function= BAAI_ef,)

full_code_collection = chroma_client.get_collection(name="HM_data_full_code",
                                             embedding_function= BAAI_ef,)

def query_by_function_name(function_name, top_k=5):
    function_vec = BAAI_ef(function_name)
    results = name_collection.query(
        query_embeddings=function_vec,
        n_results=top_k
    )
    return results

def query_by_code(code, top_k=5):
    code_vec = BAAI_ef(code)
    results = code_collection.query(
        query_embeddings=code_vec,
        n_results=top_k
    )
    return results

def query_by_full_code(code, top_k=5):
    code_vec = BAAI_ef(code)
    results = full_code_collection.query(
        query_embeddings=code_vec,
        n_results=top_k
    )
    return results

def load_existing_results(output_file):
    """Load existing results from the output file."""
    if not os.path.exists(output_file):
        return {}
    with open(output_file, 'r', encoding='utf-8') as file:
        try:
            return {item['query']: item for item in json.load(file)}
        except json.JSONDecodeError:
            return {}

def pipe():
    input_file = 'data/IC_dataset_functions_0401.json'
    output_file = 'output/IC_dataset_functions_0401_query_fullcode.json'

    # Load existing results
    existing_results = load_existing_results(output_file)

    # Ensure the output file exists
    if not os.path.exists(output_file):
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump([], file)

    with open(input_file, 'r', encoding='utf-8') as file:
        datas = json.load(file)

    for data in tqdm(datas):
        query_id = data.get("query")
        if query_id in existing_results:
            continue  # Skip if the data is already processed

        if data.get("imports"):
            for code in data.get("imports"):
                func_name_retrival = query_by_function_name(code)
                code_retrival = query_by_code(code)
                full_code_retrival = query_by_full_code(code)
                result = {
                    "query": data.get("query"),
                    "code": data.get("imports"),
                    "variables": data.get("variables"),
                    "solution": data.get("solution"),
                    "function_name_retrival": func_name_retrival,
                    "code_retrival": code_retrival,
                    "full_code_retrival": full_code_retrival
                }

                # Append the result to the output file dynamically
                with open(output_file, 'r+', encoding='utf-8') as file:
                    try:
                        current_data = json.load(file)
                    except json.JSONDecodeError:
                        current_data = []
                    current_data.append(result)
                    file.seek(0)
                    json.dump(current_data, file, indent=4, ensure_ascii=False)
                    file.truncate()

pipe()