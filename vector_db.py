import os

import chromadb
from chromadb.api.models import Collection
from chromadb.utils import embedding_functions
from transformers import AutoTokenizer, AutoModel
import torch

import crawler

chroma_client = chromadb.PersistentClient("./db_client")

sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="paraphrase-multilingual-MiniLM-L12-v2",
    normalize_embeddings=True)


def get_collection(collection_name) -> Collection:
    return chroma_client.get_or_create_collection(
        collection_name,
        embedding_function=sentence_transformer_ef,
        metadata={"hnsw:space": "cosine"}
    )


def add_list_to_documents(collection: Collection, files: list[str]):
    collection.upsert(
        documents=files,
        ids=[str(i) for i, data in enumerate(files)]
    )


def get_documents_count(collection: Collection):
    return collection.count()


def get_every_document(collection: Collection):
    return collection.get()


def query_document(collection: Collection, query: str, top: int = 1):
    return collection.query(
        query_texts=query,
        n_results=top,
        include=["documents", "distances"]
    )


def get_3_similar_document(collection, query) -> str:
    result = query_document(collection, query, top=3)
    return " ".join(result["documents"][0])


def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    pooled_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1),
                                                                                           min=1e-9)
    return pooled_embeddings.tolist()


def update_document_embeddings(collection: Collection, files: list):
    tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
    model = AutoModel.from_pretrained('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

    for i, data in enumerate(files):
        encoded_input = tokenizer(data, padding=True, truncation=True, return_tensors='pt')

        with torch.no_grad():
            model_output = model(**encoded_input)
            result_vector = mean_pooling(model_output, encoded_input['attention_mask'])

        print(len(result_vector[0]))

        collection.upsert(
            ids=[str(i)],
            embeddings=result_vector
        )

def get_text_list_from_files(dir_path: str):
    result_list = []

    if not os.path.exists(dir_path):
        print("directory does not exist!")
        return result_list

    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            result_list.append(content)

    return [str(i) for i in result_list]


if __name__ == "__main__":
    collection = get_collection("pionworld_data")
    # files = get_text_list_from_files("crawling_result")
    # add_list_to_documents(collection, files)

    query = "파이언넷 교통편 알려줘"
    result = query_document(collection, query, 3)
    print(result['documents'])
