# hello_world_gpt2.py

import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

def generate_hello_world():
    # Load pre-trained model and tokenizer
    model_name = 'gpt2'
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    model = GPT2LMHeadModel.from_pretrained(model_name)

    # Encode input text
    input_text = "Hello, World!"
    input_ids = tokenizer.encode(input_text, return_tensors='pt')

    # Generate output
    with torch.no_grad():
        output = model.generate(input_ids, max_length=50, num_return_sequences=1)

    # Decode and print the output
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
    print(generated_text)

if __name__ == "__main__":
    generate_hello_world()