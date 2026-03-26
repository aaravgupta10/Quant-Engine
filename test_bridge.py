import ollama

print("Sending query to local Llama 3.1...")

response = ollama.chat(model='llama3.1', messages=[
  {
    'role': 'user',
    'content': 'What are the top 3 sectors in the Indian stock market by market capitalization? Answer in one sentence.'
  }
])

print("\nResponse from Agent:")
print(response['message']['content'])