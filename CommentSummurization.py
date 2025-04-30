import os
import json
import time
import logging
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

def summarize_comment(comment, retries=3):
    """Use OpenAI to summarize a single comment into 1–2 professional HR sentences."""
    prompt = (
        "You are an HR assistant. Summarize the following employee feedback "
        "into 1–2 professional, HR-friendly sentences:\n\n"
        f"\"{comment}\"\n\nSummary:"
    )
    for attempt in range(retries):
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that writes professional HR summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.5,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.warning(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2)

    logging.error("Failed to get summary after multiple attempts.")
    return "Summary unavailable due to API error."

def summarize_comments_file(input_file, output_file):
    """Process a JSON file of survey data and summarize each comment using OpenAI."""
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        logging.error(f"Failed to load input file '{input_file}': {e}")
        return

    logging.info(f"Starting comment summarization for {len(data)} records...")

    for i, entry in enumerate(data, 1):
        comment = entry.get("Comment", "")
        summary = summarize_comment(comment)
        entry["CommentSummary"] = summary
        logging.info(f"✅ Summary {i}/{len(data)} added.")

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logging.info(f"✅ Summaries saved to '{output_file}'")
    except Exception as e:
        logging.error(f"Failed to save output file '{output_file}': {e}")

def main():
    # Set input/output paths here
    input_path = ".\output\hr_survey_responses_with_sentiment.json"
    output_path = ".\output\hr_survey_responses_with_sentiment_summary.json"

    # Start the summarization process
    summarize_comments_file(input_path, output_path)

if __name__ == "__main__":
    main()
