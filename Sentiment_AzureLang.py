import os
import json
import logging
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

# Load Azure credentials
AZURE_TEXT_ANALYTICS_KEY = os.getenv("AZURE_TEXT_ANALYTICS_KEY")
AZURE_TEXT_ANALYTICS_ENDPOINT = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")


def authenticate_text_analytics_client():
    """Initialize Azure Text Analytics client."""
    if not AZURE_TEXT_ANALYTICS_KEY or not AZURE_TEXT_ANALYTICS_ENDPOINT:
        raise ValueError("Azure Text Analytics credentials are missing. "
                         "Ensure AZURE_TEXT_ANALYTICS_KEY and AZURE_TEXT_ANALYTICS_ENDPOINT are set.")
    credential = AzureKeyCredential(AZURE_TEXT_ANALYTICS_KEY)
    return TextAnalyticsClient(endpoint=AZURE_TEXT_ANALYTICS_ENDPOINT, credential=credential)


def analyze_sentiment_on_json(input_json_path, output_json_path):
    """Perform sentiment analysis on survey comments using Azure Text Analytics."""
    client = authenticate_text_analytics_client()

    try:
        with open(input_json_path, "r", encoding="utf-8") as infile:
            data = json.load(infile)
    except Exception as e:
        logging.error(f"Failed to load input JSON file '{input_json_path}': {e}")
        return

    logging.info("🔍 Starting sentiment analysis in batches of 10...")
    updated_data = []

    for i in range(0, len(data), 10):
        batch = data[i:i + 10]
        comments = [entry.get("Comment", "") for entry in batch]

        try:
            results = client.analyze_sentiment(documents=comments)
        except Exception as e:
            logging.error(f"❗ Azure error analyzing batch {i // 10 + 1}: {e}")
            for entry in batch:
                entry["Sentiment"] = "error"
                entry["SentimentScore"] = 0.0
                updated_data.append(entry)
            continue

        for entry, result in zip(batch, results):
            if not result.is_error:
                scores = result.confidence_scores
                score_map = {
                    "positive": scores.positive,
                    "neutral": scores.neutral,
                    "negative": scores.negative
                }
                best_sentiment = max(score_map, key=score_map.get)
                entry["Sentiment"] = best_sentiment
                entry["SentimentScore"] = round(score_map[best_sentiment], 3)
            else:
                logging.warning(f"Sentiment error for {entry.get('EmployeeID', 'Unknown')}: {result.error}")
                entry["Sentiment"] = "error"
                entry["SentimentScore"] = 0.0
            updated_data.append(entry)

    try:
        with open(output_json_path, "w", encoding="utf-8") as outfile:
            json.dump(updated_data, outfile, indent=4, ensure_ascii=False)
        logging.info(f"✅ Sentiment analysis complete. Output saved to '{output_json_path}'")
    except Exception as e:
        logging.error(f"Failed to save output file '{output_json_path}': {e}")


def main():
    # Define file paths here
    input_path = ".\output\hr_survey_responses2.json"
    output_path = ".\output\hr_survey_responses_with_sentiment.json"
    
    # Start sentiment analysis
    analyze_sentiment_on_json(input_path, output_path)


if __name__ == "__main__":
    main()
