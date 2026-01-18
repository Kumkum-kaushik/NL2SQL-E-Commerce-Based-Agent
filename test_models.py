#!/usr/bin/env python3
"""
Test script to check available Gemini models
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

def test_available_models():
    """Test what Gemini models are available"""
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ GOOGLE_API_KEY not found in environment")
            return
        
        genai.configure(api_key=api_key)
        
        print("📋 Available Gemini models:")
        models = genai.list_models()
        
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                print(f"✅ {model.name} - {model.display_name}")
                
    except Exception as e:
        print(f"❌ Error listing models: {str(e)}")

if __name__ == "__main__":
    test_available_models()