import json
import random
from transformers import AutoModelForCausalLM, AutoTokenizer

class FAQChatbot:
    def __init__(self, model_name='distilgpt2', faq_file='data/campus_faq.jsonl'):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.faq_data = self.load_faq_data(faq_file)

    def load_faq_data(self, faq_file):
        with open(faq_file, 'r') as file:
            return [json.loads(line) for line in file]

    def get_answer(self, question):
        # Select a random FAQ entry to provide context
        faq_entry = random.choice(self.faq_data)
        context = faq_entry['question'] + " " + faq_entry['answer']
        
        # Encode the input
        input_text = f"Question: {question}\nContext: {context}\nAnswer:"
        input_ids = self.tokenizer.encode(input_text, return_tensors='pt')

        # Generate a response
        output = self.model.generate(input_ids, max_length=150, num_return_sequences=1)
        answer = self.tokenizer.decode(output[0], skip_special_tokens=True)

        # Extract the answer from the generated text
        return answer.split("Answer:")[-1].strip()

if __name__ == "__main__":
    chatbot = FAQChatbot()
    print("Welcome to the FAQ Chatbot! Type 'exit' to quit.")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        response = chatbot.get_answer(user_input)
        print(f"Chatbot: {response}")