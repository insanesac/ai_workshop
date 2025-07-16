def load_model(model_name):
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    return tokenizer, model

def generate_text(tokenizer, model, prompt, max_length=50):
    inputs = tokenizer.encode(prompt, return_tensors='pt')
    outputs = model.generate(inputs, max_length=max_length, num_return_sequences=1)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

def save_model(model, tokenizer, save_directory):
    model.save_pretrained(save_directory)
    tokenizer.save_pretrained(save_directory)

def load_saved_model(save_directory):
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(save_directory)
    model = AutoModelForCausalLM.from_pretrained(save_directory)

    return tokenizer, model

def evaluate_model(model, tokenizer, test_data):
    # Placeholder for evaluation logic
    results = []
    for prompt in test_data:
        generated_text = generate_text(tokenizer, model, prompt)
        results.append((prompt, generated_text))
    return results