import os
from dotenv import load_dotenv
import google.generativeai as genai
import time

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv('GOOGLE_API_KEY')
print(f"API key loaded: {'Yes' if api_key else 'No'}")

try:
    # Configure Gemini with safety settings
    genai.configure(api_key=api_key)
    print("API configured successfully")

    # Add delay to respect rate limits
    time.sleep(1)  # Wait 1 second between requests
    
    # Test the API with retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content('Say hello!')
            print(f"Response: {response.text}")
            print("Test completed successfully!")
            break
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2  # Exponential backoff
                print(f"Rate limit hit, waiting {wait_time} seconds...")
                time.sleep(wait_time)
                continue
            raise e

except Exception as e:
    print(f"Error occurred: {str(e)}") 