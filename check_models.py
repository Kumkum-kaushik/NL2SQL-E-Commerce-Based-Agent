import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found in environment.")
else:
    genai.configure(api_key=api_key)
    
    print("Listing available models...")
    try:
        found_flash = False
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
                if "flash" in m.name.lower():
                    found_flash = True
        
        if not found_flash:
            print("\nWARNING: No 'flash' model found in the list.")
            
    except Exception as e:
        print(f"Error listing models: {e}")
