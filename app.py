import os
import json
import time
import logging
from random import randint, choice
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import openai
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from azure.ai.formrecognizer import DocumentAnalysisClient

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
FLASK_API_KEY = os.getenv("FLASK_API_KEY")  # Add your API key in .env
AZURE_TEXT_ANALYTICS_KEY = os.getenv("AZURE_TEXT_ANALYTICS_KEY")
AZURE_TEXT_ANALYTICS_ENDPOINT = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")
AZURE_DOCUMENT_INTELLIGENCE_KEY = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

# Initialize Flask app
app = Flask(__name__)

##################################################
# Systetic Coment Generation by OpenAI 4o

# Predefined department list
departments = [
    "Engineering", "Marketing", "Sales", "Customer Support",
    "HR", "Finance", "IT", "Operations", "Legal", "Product"
]

# Generate GPT prompt
def generate_prompt(employee_id, department, satisfaction_rating):
    return f"""
Generate a fictional HR survey comment for the following employee:

EmployeeID: {employee_id}
Department: {department}
SatisfactionRating: {satisfaction_rating}

Write a realistic comment (no more than 200 words) that reflects the satisfaction level given. 
If the satisfaction rating is low (e.g., 1 or 2), the comment should reflect dissatisfaction.
If it's high (e.g., 4 or 5), the comment should express a positive experience.

Only return the comment text. Do not include any other information or formatting.
"""

# Call OpenAI API with retry logic
def call_openai(prompt, retries=3):
    for attempt in range(retries):
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an assistant generating HR survey comments. Only output the comment."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=300,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.warning(f"OpenAI call failed (attempt {attempt + 1}): {e}")
            time.sleep(2)
    raise Exception("OpenAI API call failed after retries.")

# Flask API route to generate surveys
@app.route("/generate-surveys", methods=["POST"])
def generate_surveys():
    # API Key check
    api_key = request.headers.get("x-api-key")
    if api_key != FLASK_API_KEY:
        return jsonify({"error": "Unauthorized: Invalid API key"}), 401

    try:
        num_surveys = int(request.json.get("count", 30))
        responses = []

        for i in range(1, num_surveys + 1):
            employee_id = f"EMP{i:03d}"
            department = choice(departments)
            satisfaction = randint(1, 5)

            logging.info(f"Generating comment for {employee_id} (Rating: {satisfaction})")
            prompt = generate_prompt(employee_id, department, satisfaction)
            comment = call_openai(prompt)

            responses.append({
                "EmployeeID": employee_id,
                "Department": department,
                "SatisfactionRating": satisfaction,
                "Comment": comment
            })

        return jsonify(responses)

    except Exception as e:
        logging.exception("Error during survey generation")
        return jsonify({"error": "Internal Server Error"}), 500

##################################################
# Senetiment Analysis by Azure Languague

# Authenticate with Azure Text Analytics
def authenticate_text_analytics_client():
    if not AZURE_TEXT_ANALYTICS_KEY or not AZURE_TEXT_ANALYTICS_ENDPOINT:
        raise ValueError("Missing Azure credentials.")
    credential = AzureKeyCredential(AZURE_TEXT_ANALYTICS_KEY)
    return TextAnalyticsClient(endpoint=AZURE_TEXT_ANALYTICS_ENDPOINT, credential=credential)

# Perform sentiment analysis on uploaded JSON
def analyze_sentiment(data):
    client = authenticate_text_analytics_client()
    enriched_data = []

    for i in range(0, len(data), 10):  # Max 10 per batch
        batch = data[i:i + 10]
        comments = [entry.get("Comment", "") for entry in batch]

        try:
            results = client.analyze_sentiment(documents=comments)
        except Exception as e:
            logging.error(f"Error analyzing batch {i // 10 + 1}: {e}")
            for entry in batch:
                entry["Sentiment"] = "error"
                entry["SentimentScore"] = 0.0
                enriched_data.append(entry)
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
                logging.warning(f"Sentiment error for entry: {result.error}")
                entry["Sentiment"] = "error"
                entry["SentimentScore"] = 0.0
            enriched_data.append(entry)

    return enriched_data

@app.route("/analyze-sentiment", methods=["POST"])
def analyze_sentiment_api():
    # Check API key
    api_key = request.headers.get("x-api-key")
    if api_key != FLASK_API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    # Check if file is provided
    if "file" not in request.files:
        return jsonify({"error": "Missing file"}), 400

    file = request.files["file"]

    try:
        data = json.load(file)
        if not isinstance(data, list):
            return jsonify({"error": "JSON must be an array of records."}), 400

        logging.info(f"Analyzing {len(data)} records for sentiment...")
        result = analyze_sentiment(data)
        return jsonify(result), 200

    except Exception as e:
        logging.exception("Failed to analyze sentiment")
        return jsonify({"error": "Processing failed", "details": str(e)}), 500

#################################################
# Comment Summurizatio with OpenAI 4o

def summarize_comment(comment, retries=3):
    """Generate an HR-friendly summary from a single comment using OpenAI."""
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

    logging.error("Failed to summarize comment after retries.")
    return "Summary unavailable due to API error."

def summarize_comments(data):
    """Apply summarization to each record in the data."""
    summarized = []
    for i, entry in enumerate(data, 1):
        comment = entry.get("Comment", "")
        summary = summarize_comment(comment)
        entry["CommentSummary"] = summary
        logging.info(f"✅ Summary {i}/{len(data)} added.")
        summarized.append(entry)
    return summarized

@app.route("/summarize-comments", methods=["POST"])
def summarize_api():
    # Authenticate with x-api-key
    api_key = request.headers.get("x-api-key")
    if api_key != FLASK_API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    # Ensure file is included
    if "file" not in request.files:
        return jsonify({"error": "Missing file"}), 400

    file = request.files["file"]

    try:
        data = json.load(file)
        if not isinstance(data, list):
            return jsonify({"error": "JSON must be an array of records"}), 400

        logging.info(f"Starting summarization for {len(data)} records...")
        summarized_data = summarize_comments(data)
        return jsonify(summarized_data)

    except Exception as e:
        logging.exception("Failed to process summarization request")
        return jsonify({"error": "Processing failed", "details": str(e)}), 500

#################################################
#key-Phrase Extraction with Azure AI language



def extract_key_phrases(data):
    """Apply Azure Key Phrase Extraction on a list of records."""
    client = authenticate_text_analytics_client()
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
                logging.warning(f"Key phrase extraction failed for entry: {result.error}")
                entry["KeyPhrases"] = []
            updated_data.append(entry)

    return updated_data

@app.route("/extract-keyphrases", methods=["POST"])
def extract_keyphrases_api():
    # API key validation
    api_key = request.headers.get("x-api-key")
    if api_key != FLASK_API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    if "file" not in request.files:
        return jsonify({"error": "Missing file"}), 400

    file = request.files["file"]

    try:
        data = json.load(file)
        if not isinstance(data, list):
            return jsonify({"error": "JSON must be an array of records."}), 400

        logging.info(f"Starting key phrase extraction for {len(data)} records...")
        result = extract_key_phrases(data)
        return jsonify(result)

    except Exception as e:
        logging.exception("Processing failed")
        return jsonify({"error": "Processing failed", "details": str(e)}), 500

#################################################
#PDF survey Content Extraction with Azure Document Intelligence


def authenticate_document_client():
    """Initialize Azure Document Intelligence client."""
    if not AZURE_DOCUMENT_INTELLIGENCE_KEY or not AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT:
        raise ValueError("Missing Azure Document Intelligence credentials.")
    return DocumentAnalysisClient(
        endpoint=AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT,
        credential=AzureKeyCredential(AZURE_DOCUMENT_INTELLIGENCE_KEY)
    )

def extract_surveys_from_pdf_file(file_stream):
    """Extract survey responses from a PDF file-like object."""
    client = authenticate_document_client()

    try:
        poller = client.begin_analyze_document("prebuilt-read", document=file_stream)
        result = poller.result()
    except Exception as e:
        logging.error(f"Failed to analyze PDF: {e}")
        raise

    all_text = ""
    for page in result.pages:
        for line in page.lines:
            all_text += line.content.strip() + "\n"

    blocks = all_text.split("Survey ")[1:]
    surveys = []

    for block in blocks:
        survey = {}
        lines = block.strip().split("\n")
        comment_lines = []
        parsing_comment = False

        for line in lines:
            if "EmployeeID" in line:
                survey["EmployeeID"] = line.split(":")[-1].strip()
            elif "Department" in line:
                survey["Department"] = line.split(":")[-1].strip()
            elif "SatisfactionRating" in line:
                survey["SatisfactionRating"] = line.split(":")[-1].strip()
            elif "Comment" in line:
                parsing_comment = True
                comment_lines.append(line.split(":", 1)[-1].strip())
            elif parsing_comment:
                comment_lines.append(line.strip())

        if comment_lines:
            survey["Comment"] = " ".join(comment_lines).strip()

        if survey:
            surveys.append(survey)

    return surveys

@app.route("/extract-surveys", methods=["POST"])
def extract_surveys_api():
    # Validate API key
    api_key = request.headers.get("x-api-key")
    if api_key != FLASK_API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    # Validate file upload
    if "file" not in request.files:
        return jsonify({"error": "Missing PDF file"}), 400

    file = request.files["file"]

    try:
        surveys = extract_surveys_from_pdf_file(file)
        return jsonify(surveys)
    except Exception as e:
        logging.exception("Error processing PDF")
        return jsonify({"error": "Processing failed", "details": str(e)}), 500


#################################################
# Run app
if __name__ == "__main__":
    app.run(debug=False)
