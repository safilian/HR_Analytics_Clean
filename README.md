**Overal Description**
This repository contains a modular pipeline for processing HR survey data — including synthetic survey generation, sentiment analysis, summarization, key phrase extraction, and PDF content parsing — all built using OpenAI and Azure AI services.

Each major functionality is encapsulated in its own .py file, while a unified app.py provides API endpoints for simplified testing. The project is secured using a basic API key mechanism and structured to support scalable automation or integration


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

🔧 File Descriptions
generate_survey.py
Generates up to 30 fictional HR survey responses using OpenAI's GPT-4o model. The output includes:

EmployeeID

Department

SatisfactionRating

Comment

Outputs:

hr_survey_responses2.json

hr_survey_responses2.csv

Sentiment_AzureLang.py
Receives the output from generate_survey.py and uses Azure AI Language to detect:

Sentiment (positive, neutral, negative)

Confidence scores

Output:

hr_survey_responses_with_sentiment.json

CommentSummurization.py
Processes the sentiment-enriched data and generates a 1–2 sentence HR-friendly summary of each comment using OpenAI.

Output:

hr_survey_responses_with_sentiment_summary.json

KeyPhrasesExtraction.py
Uses Azure AI to extract key phrases from each survey comment, helping to identify common topics or themes.

Output:

hr_survey_responses_with_sentiment_summary_keyphrases.json

PDFContentExtraction.py
Extracts structured HR survey responses from a PDF using Azure Document Intelligence with the prebuilt-read model.

Output:

PDFsurvey_extracted.json
