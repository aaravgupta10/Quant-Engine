import os
from dotenv import load_dotenv
from google import genai

load_dotenv(override=True)
client = genai.Client()

print("Sending query to Gemini 2.5 Flash...")

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents='What are the top 3 sectors in the Indian stock market by market capitalization? Answer in one sentence.'
)

print("\nResponse from Agent:")
print(response.text)