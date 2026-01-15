import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found in environment.")
else:
    client = genai.Client(api_key=api_key)
    
    print("Listing available models using new SDK...")
    try:
        found_flash = False
        # In the new SDK, models are listed via client.models.list()
        for m in client.models.list():
            # Check for generation support
            # For simplicity, we check if it's a model
            print(f"- {m.name}")
            if "flash" in m.name.lower():
                found_flash = True
        
        if not found_flash:
            print("\nWARNING: No 'flash' model found in the list.")
            
    except Exception as e:
        print(f"Error listing models: {e}")
