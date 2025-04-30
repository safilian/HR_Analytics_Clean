import os
import json
import logging
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient

# Load environment variables
load_dotenv()
AZURE_DOCUMENT_INTELLIGENCE_KEY = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

def authenticate_document_client():
    """Initialize Azure Document Intelligence client."""
    if not AZURE_DOCUMENT_INTELLIGENCE_KEY or not AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT:
        raise ValueError("Missing Azure Document Intelligence credentials. Please check your .env file.")
    return DocumentAnalysisClient(
        endpoint=AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT,
        credential=AzureKeyCredential(AZURE_DOCUMENT_INTELLIGENCE_KEY)
    )

def extract_surveys_from_pdf(pdf_path, output_path):
    """Extract survey responses from a structured PDF using Azure's prebuilt-read model."""
    client = authenticate_document_client()

    try:
        with open(pdf_path, "rb") as f:
            poller = client.begin_analyze_document("prebuilt-read", document=f)
            result = poller.result()
    except Exception as e:
        logging.error(f"Failed to analyze PDF '{pdf_path}': {e}")
        return

    # Aggregate all lines of text
    all_text = ""
    for page in result.pages:
        for line in page.lines:
            all_text += line.content.strip() + "\n"

    # Parse individual surveys
    blocks = all_text.split("Survey ")[1:]  # Skip any content before the first survey
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

    # Save structured survey data to JSON
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(surveys, f, indent=4, ensure_ascii=False)
        logging.info(f"✅ Extracted {len(surveys)} surveys and saved to '{output_path}'")
    except Exception as e:
        logging.error(f"Failed to save extracted surveys to '{output_path}': {e}")

def main():
    # Define PDF input and JSON output paths
    input_pdf = ".\data\SurveyPDF.pdf"
    output_json = ".\output\PDFsurvey_extracted.json"

    # Run extraction process
    extract_surveys_from_pdf(input_pdf, output_json)

if __name__ == "__main__":
    main()
