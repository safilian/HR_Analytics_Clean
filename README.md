# **Overal Description**
This repository contains a modular pipeline for processing HR survey data — including synthetic survey generation, sentiment analysis, summarization, key phrase extraction, and PDF content parsing — all built using OpenAI and Azure AI services.

Each major functionality is encapsulated in its own .py file, while a unified app.py provides API endpoints for simplified testing. The project is secured using a basic API key mechanism and structured to support scalable automation or integration

# ✅ Environment Setup

**1. Clone the repository**

git clone https://github.com/yourusername/HR-Analytics-Clean.git

cd HR-Analytics-Clean

**2. Create .env file**

**.env Format**

OPENAI_API_KEY=your_openai_key

FLASK_API_KEY=your_custom_key

AZURE_TEXT_ANALYTICS_KEY=your_azure_lang_key

AZURE_TEXT_ANALYTICS_ENDPOINT=https://your-language.cognitiveservices.azure.com/

AZURE_DOCUMENT_INTELLIGENCE_KEY=your_azure_doc_key

AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-docai.cognitiveservices.azure.com/

**3. Install dependencies**

pip install -r requirements.txt

**4. Run the API**

python app.py


# 📁 **Project Structure**

HR-Analytics-Clean/

│

├── app.py                              # Unified Flask API with 5 endpoints

├── generate_survey.py                 # Generates synthetic HR surveys using OpenAI

├── Sentiment_AzureLang.py            # Performs sentiment analysis using Azure AI

├── CommentSummurization.py           # Summarizes comments using OpenAI

├── KeyPhrasesExtraction.py           # Extracts key phrases using Azure AI

├── PDFContentExtraction.py           # Extracts structured data from survey PDFs

│

├── requirements.txt                   # Python dependencies

├── .env                               # Environment variables (API keys, endpoints)

│

├── data/

│   ├── hr_survey_responses2.csv       # Sample synthetic CSV survey data

│   ├── hr_survey_responses2.json      # Sample synthetic JSON survey data

│   └── SurveyPDF.pdf                  # Sample PDF for extraction

│

├── output/

│   ├── hr_survey_responses2.json      # Sample synthetic JSON survey data

│   ├── hr_survey_responses_with_sentiment.json

│   ├── hr_survey_responses_with_sentiment_summary.json

│   ├── hr_survey_responses_with_sentiment_summary_keyphrases.json

│   └── PDFsurvey_extracted.json

# 🌐 **API Access — app.py**
All five tasks are also exposed as API endpoints through a single Flask application. The endpoints require an API key via the x-api-key header.

🔐 **Endpoints:**

Task	Method	URL	Input Type

Generate Survey	POST	/generate-surveys	JSON count

Sentiment Analysis	POST	/analyze-sentiment	JSON file

Comment Summarization	POST	/summarize-comments	JSON file

Key Phrase Extraction	POST	/extract-keyphrases	JSON file

PDF Survey Extraction	POST	/extract-surveys	PDF file

🔍 **Sample API Usage (Postman)**

Example: /summarize-comments

Method: POST

Headers:

x-api-key: your_custom_key

Body: form-data

Key: file (type: File)

Value: Upload hr_survey_responses_with_sentiment.json

## 🔧 File Descriptions

### `generate_survey.py`
Generates up to 30 fictional HR survey responses using OpenAI's GPT-4o model. The output includes:
- `EmployeeID`
- `Department`
- `SatisfactionRating`
- `Comment`

**Outputs**:
- `hr_survey_responses2.json`
- `hr_survey_responses2.csv`

---

### `Sentiment_AzureLang.py`
Receives the output from `generate_survey.py` and uses **Azure AI Language** to detect:
- Sentiment (`positive`, `neutral`, `negative`)
- Confidence scores

**Output**:
- `hr_survey_responses_with_sentiment.json`

---

### `CommentSummurization.py`
Receives the output from `Sentiment_AzureLang.py` and processes the sentiment-enriched data and generates a 1–2 sentence **HR-friendly summary** of each comment using OpenAI.

**Output**:
- `hr_survey_responses_with_sentiment_summary.json`

---

### `KeyPhrasesExtraction.py`
Receives the output from `CommentSummurization.py` and uses Azure AI to extract **key phrases** from each survey comment, helping to identify common topics or themes.

**Output**:
- `hr_survey_responses_with_sentiment_summary_keyphrases.json`

---

### `PDFContentExtraction.py`
Extracts structured HR survey responses from a PDF using Azure **Document Intelligence** with the `prebuilt-read` model.

**Output**:
- `PDFsurvey_extracted.json`

---
