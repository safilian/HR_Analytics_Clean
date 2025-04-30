import os
import json
import logging
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

# Load environment variables
load_dotenv()
AZURE_TEXT_ANALYTICS_KEY = os.getenv("AZURE_TEXT_ANALYTICS_KEY")
AZURE_TEXT_ANALYTICS_ENDPOINT = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

def authenticate_text_analytics_client():
    """Initialize Azure Text Analytics client."""
    if not AZURE_TEXT_ANALYTICS_KEY or not AZURE_TEXT_ANALYTICS_ENDPOINT:
        raise ValueError("Azure credentials are missing. Please check your .env configuration.")
    credential = AzureKeyCredential(AZURE_TEXT_ANALYTICS_KEY)
    return TextAnalyticsClient(endpoint=AZURE_TEXT_ANALYTICS_ENDPOINT, credential=credential)

def extract_key_phrases_on_json(input_file, output_file):
    """Extract key phrases from comments in a JSON file using Azure Text Analytics."""
    client = authenticate_text_analytics_client()

    try:
        with open(input_file, "r", encoding="utf-8") as infile:
            data = json.load(infile)
    except Exception as e:
        logging.error(f"Failed to load input file '{input_file}': {e}")
        return

    logging.info("🔍 Starting key phrase extraction in batches of 10...")
    updated_data = []

    for i in range(0, len(data), 10):
        batch = data[i:i + 10]
        comments = [entry.get("Comment", "") for entry in batch]

        try:
            results = client.extract_key_phrases(documents=comments)
        except Exception as e:
            logging.error(f"Error processing batch {i // 10 + 1}: {e}")
            for entry in batch:
                entry["KeyPhrases"] = []
                updated_data.append(entry)
            continue

        for entry, result in zip(batch, results):
            if not result.is_error:
                entry["KeyPhrases"] = result.key_phrases
            else:
                logging.warning(f"Key phrase extraction failed for {entry.get('EmployeeID', 'Unknown')}: {result.error}")
                entry["KeyPhrases"] = []
            updated_data.append(entry)

    try:
        with open(output_file, "w", encoding="utf-8") as outfile:
            json.dump(updated_data, outfile, indent=4, ensure_ascii=False)
        logging.info(f"✅ Key phrases saved to '{output_file}'")
    except Exception as e:
        logging.error(f"Failed to save output file '{output_file}': {e}")

def main():
    # Define input and output paths
    input_path = ".\output\hr_survey_responses_with_sentiment_summary.json"
    output_path = ".\output\hr_survey_responses_with_sentiment_summary_keyphrases.json"

    # Start the extraction process
    extract_key_phrases_on_json(input_path, output_path)

if __name__ == "__main__":
    main()
