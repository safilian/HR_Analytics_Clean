import os
import csv
import json
import time
import openai
import logging
from random import randint, choice
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("survey_generation.log"),
        logging.StreamHandler()
    ]
)

# Predefined department names
departments = [
    "Engineering", "Marketing", "Sales", "Customer Support",
    "HR", "Finance", "IT", "Operations", "Legal", "Product"
]

# Prompt template for generating realistic HR comments
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

# Call the OpenAI Chat Completion API with retries
def call_openai(prompt, retries=3):
    for attempt in range(retries):
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",  # Replace with "gpt-4" if preferred
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
            logging.warning(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2)
    logging.error("All retry attempts failed while calling OpenAI API.")
    raise Exception("OpenAI API call failed after multiple retries.")

# Main process to generate HR survey data
def main():
    csv_filename = ".\data\hr_survey_responses3.csv"
    json_filename = ".\output\hr_survey_responses3.json"
    fieldnames = ["EmployeeID", "Department", "SatisfactionRating", "Comment"]
    all_responses = []

    logging.info("Starting HR survey generation process...")

    try:
        with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for i in range(1, 31):
                employee_id = f"EMP{i:03d}"
                department = choice(departments)
                satisfaction = randint(1, 5)

                logging.info(f"Generating comment for {employee_id} (Rating: {satisfaction})")
                prompt = generate_prompt(employee_id, department, satisfaction)
                comment = call_openai(prompt)

                row = {
                    "EmployeeID": employee_id,
                    "Department": department,
                    "SatisfactionRating": satisfaction,
                    "Comment": comment
                }

                writer.writerow(row)
                all_responses.append(row)

        with open(json_filename, "w", encoding="utf-8") as jsonfile:
            json.dump(all_responses, jsonfile, indent=4, ensure_ascii=False)

        logging.info(f"Survey generation completed successfully.")
        logging.info(f"CSV file saved: {csv_filename}")
        logging.info(f"JSON file saved: {json_filename}")

    except Exception as e:
        logging.exception("An error occurred during survey generation.")

if __name__ == "__main__":
    main()
