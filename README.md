**Overal Description**
This repository contains a modular pipeline for processing HR survey data — including synthetic survey generation, sentiment analysis, summarization, key phrase extraction, and PDF content parsing — all built using OpenAI and Azure AI services.

Each major functionality is encapsulated in its own .py file, while a unified app.py provides API endpoints for simplified testing. The project is secured using a basic API key mechanism and structured to support scalable automation or integration

✅ Environment Setup

**1. Clone the repository**

git clone https://github.com/yourusername/HR-Analytics-Pipeline.git

cd HR-Analytics-Pipeline

**2. Create .env file**

# .env

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


📁 **Project Structure**

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

🌐 API Access — app.py
All five tasks are also exposed as API endpoints through a single Flask application. The endpoints require an API key via the x-api-key header.

🔐 Endpoints:

Task	Method	URL	Input Type
Generate Survey	POST	/generate-surveys	JSON count
Sentiment Analysis	POST	/analyze-sentiment	JSON file
Comment Summarization	POST	/summarize-comments	JSON file
Key Phrase Extraction	POST	/extract-keyphrases	JSON file
PDF Survey Extraction	POST	/extract-surveys	PDF file

