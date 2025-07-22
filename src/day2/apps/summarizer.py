from transformers import pipeline

def summarize_text(text):
    summarizer = pipeline("summarization")
    summary = summarizer(text, max_length=130, min_length=30, do_sample=False)
    return summary[0]['summary_text']

if __name__ == "__main__":
    input_text = """
    Your input text goes here. This can be a long paragraph or multiple paragraphs that you want to summarize.
    """
    summary = summarize_text(input_text)
    print("Summary:")
    print(summary)