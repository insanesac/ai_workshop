def load_jsonl(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            data.append(json.loads(line))
    return data

def load_text(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def load_image(image_path):
    return Image.open(image_path)

def load_dataset(dataset_type, file_path):
    if dataset_type == 'jsonl':
        return load_jsonl(file_path)
    elif dataset_type == 'text':
        return load_text(file_path)
    elif dataset_type == 'image':
        return load_image(file_path)
    else:
        raise ValueError("Unsupported dataset type. Use 'jsonl', 'text', or 'image'.")