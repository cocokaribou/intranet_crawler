import os

def chunk(size: int, original_list: list):
    chunk_size = len(original_list) // size + (len(original_list) % size > 0)
    return [original_list[i:i + chunk_size] for i in range(0, len(original_list), chunk_size)]

def text_to_list(text):
    data_val = text.replace('<', '').replace('>', '').replace('\n', '*').replace('. ', '*')
    txt_arr = data_val.split('*')
    txt_arr = [l.strip() for l in txt_arr]
    txt_arr = [v for v in txt_arr if v]
    return txt_arr

def save_file(file_name: str, content: str, directory: str):
    file_path = os.path.join(directory, file_name)

    with open(file_path, "w") as file:
        file.write(content)
