# sentiment_tool.py

import json
from transformers import pipeline

def load_model():
    """Load the sentiment analysis model."""
    model = pipeline("sentiment-analysis")
    return model

def analyze_sentiment(text):
    """Analyze the sentiment of the given text."""
    model = load_model()
    result = model(text)
    return result

def main():
    """Main function to run the sentiment analysis tool."""
    print("Sentiment Analysis Tool")
    text = input("Enter text for sentiment analysis: ")
    result = analyze_sentiment(text)
    print("Sentiment Analysis Result:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()