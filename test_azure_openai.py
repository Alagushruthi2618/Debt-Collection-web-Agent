#!/usr/bin/env python3
"""
Quick test script to verify Azure OpenAI API is working.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_azure_openai():
    """Test if Azure OpenAI API is configured and working."""
    
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://llm-3rdparty.cognitiveservices.azure.com/")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1-mini")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
    
    if not api_key:
        print("[ERROR] AZURE_OPENAI_API_KEY not found in environment variables")
        print("\nPlease create a .env file in the project root with:")
        print("AZURE_OPENAI_API_KEY=your_api_key_here")
        print("AZURE_OPENAI_ENDPOINT=https://llm-3rdparty.cognitiveservices.azure.com/")
        print("AZURE_OPENAI_DEPLOYMENT=gpt-4.1-mini")
        print("AZURE_OPENAI_API_VERSION=2024-12-01-preview")
        return False
    
    print(f"[OK] AZURE_OPENAI_API_KEY found: {api_key[:10]}...{api_key[-4:]}")
    print(f"[OK] Endpoint: {endpoint}")
    print(f"[OK] Deployment: {deployment}")
    print(f"[OK] API Version: {api_version}")
    
    try:
        from openai import AzureOpenAI
        print("[OK] openai package installed")
    except ImportError:
        print("[ERROR] openai package not installed")
        print("Run: pip install openai")
        return False
    
    try:
        client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint
        )
        
        print("[OK] Testing Azure OpenAI API call...")
        response = client.chat.completions.create(
            model=deployment,
            messages=[{"role": "user", "content": "Say 'Hello' in one word."}],
            max_tokens=5
        )
        
        if response and response.choices and len(response.choices) > 0:
            content = response.choices[0].message.content
            if content:
                print(f"[OK] Azure OpenAI API working! Response: {content.strip()}")
                return True
            else:
                print("[ERROR] No content in response from Azure OpenAI API")
                return False
        else:
            print("[ERROR] No response from Azure OpenAI API")
            return False
            
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Azure OpenAI API Configuration Test")
    print("=" * 50)
    print()
    
    success = test_azure_openai()
    
    print()
    print("=" * 50)
    if success:
        print("[SUCCESS] All checks passed! Your Azure OpenAI API is configured correctly.")
        print("\nMake sure your backend server is restarted to use the new code.")
    else:
        print("[FAILED] Configuration issues found. Please fix them above.")
    print("=" * 50)

