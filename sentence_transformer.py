"""
    Sentence Transformer 연결하여 문장 별로 비교하고 결과물 도출.
"""
import os

from sentence_transformers import SentenceTransformer
from scikit-learn.metrics.pairwise import cosine_similarity
import torch

def text_to_list(text):
    data_val = text.replace('<', '').replace('>', '').replace('\n', '*').replace('. ', '*')
    txt_arr = data_val.split('*')
    txt_arr = [l.strip() for l in txt_arr]
    txt_arr = [v for v in txt_arr if v]
    return txt_arr

def get_bulk_text_embeddings():
    embeddings_dict = {}

    directory_path = "crawling_result"
    model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            # Split file data into a list of strings
            content_list = text_to_list(content)
            # Encode each string separately and concatenate the embeddings
            embeddings = []
            for text in content_list:
                embeddings.append(torch.tensor(model.encode([text])[0]))  # Convert to PyTorch tensor
            final_embedding = torch.mean(torch.stack(embeddings), dim=0)
            embeddings_dict[filename] = final_embedding

    return embeddings_dict

def get_most_similar_vectors(query, result_data):
    # Initialize SentenceTransformer model
    model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

    # Encode query string into embedding vector
    query_embedding = model.encode([query])[0]

    # Calculate cosine similarity between query vector and each vector in result_data
    similarities = {}
    for filename, embedding in result_data.items():
        similarity = cosine_similarity([query_embedding], [embedding])[0][0]
        similarities[filename] = similarity

    # Sort similarities dictionary by values in descending order
    sorted_similarities = sorted(similarities.items(), key=lambda x: x[1], reverse=True)

    # Get the top 3 most similar filenames and their embeddings
    top_3_filenames = [filename for filename, _ in sorted_similarities[:3]]
    top_3_embeddings = [result_data[filename] for filename in top_3_filenames]

    return top_3_filenames, top_3_embeddings


if __name__ == "__main__":
    # Example usage
    # 1. Get the result_data dictionary containing filename-embedding pairs
    result_data = get_bulk_text_embeddings()

    # 2. Input your query string
    query_string = "회사 얼마나 오래됐어?"

    # 3. Get the most similar vector from the result_data
    most_similar_filename, most_similar_embedding = get_most_similar_vectors(query_string, result_data)

    print("Most similar filename:", most_similar_filename)
