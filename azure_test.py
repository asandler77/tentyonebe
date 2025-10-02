#!/usr/bin/env python3
"""
Azure OpenAI connection test
Checks configuration correctness and service availability
"""

import os
from openai import AzureOpenAI
from dotenv import load_dotenv

def test_azure_openai_connection():
    """Tests Azure OpenAI connection"""
    
    # Load environment variables
    load_dotenv()
    
    # Check for required variables
    required_vars = {
        "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY"),
        "AZURE_OPENAI_MODEL_NAME": os.getenv("AZURE_OPENAI_MODEL_NAME", "gpt-4")
    }
    
    print("=== Environment Variables Check ===")
    missing_vars = []
    for var_name, var_value in required_vars.items():
        if var_value:
            # Hide API key for security
            if "API_KEY" in var_name:
                display_value = f"{var_value[:8]}...{var_value[-4:]}" if len(var_value) > 12 else "***"
            else:
                display_value = var_value
            print(f"✅ {var_name}: {display_value}")
        else:
            print(f"❌ {var_name}: NOT SET")
            missing_vars.append(var_name)
    
    if missing_vars:
        print(f"\n❌ ERROR: Missing environment variables: {', '.join(missing_vars)}")
        print("\nCreate .env file with the following variables:")
        print("AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/")
        print("AZURE_OPENAI_API_KEY=your-api-key")
        print("AZURE_OPENAI_MODEL_NAME=gpt-4")
        return False
    
    print("\n=== Testing Azure OpenAI Connection ===")
    
    try:
        # Create client
        client = AzureOpenAI(
            azure_endpoint=required_vars["AZURE_OPENAI_ENDPOINT"],
            api_key=required_vars["AZURE_OPENAI_API_KEY"],
            api_version="2024-02-15-preview"
        )
        
        print(f"🔗 Connecting to: {required_vars['AZURE_OPENAI_ENDPOINT']}")
        print(f"🤖 Model: {required_vars['AZURE_OPENAI_MODEL_NAME']}")
        
        # Test request
        print("\n📤 Sending test request...")
        
        response = client.chat.completions.create(
            model=required_vars["AZURE_OPENAI_MODEL_NAME"],
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant for testing Azure OpenAI. Answer briefly."
                },
                {
                    "role": "user",
                    "content": "Hello! This is a connection test. Answer with one word: working?"
                }
            ],
            max_tokens=10,
            temperature=0.3
        )
        
        answer = response.choices[0].message.content.strip()
        
        print(f"📥 Received response: '{answer}'")
        print(f"💰 Tokens used: {response.usage.total_tokens}")
        
        print("\n✅ SUCCESS! Azure OpenAI is working correctly!")
        
        # Additional test for "21 questions" game
        print("\n=== Game Functions Test ===")
        
        # Word generation test
        print("🎲 Testing random word generation...")
        word_response = client.chat.completions.create(
            model=required_vars["AZURE_OPENAI_MODEL_NAME"],
            messages=[
                {
                    "role": "system",
                    "content": "You are a word generator for the '21 questions' game. Generate one random word."
                },
                {
                    "role": "user",
                    "content": "Think of one random word for the '21 questions' game. Answer with ONLY the word."
                }
            ],
            max_tokens=10,
            temperature=1.0
        )
        
        secret_word = word_response.choices[0].message.content.strip()
        print(f"🎯 Generated word: '{secret_word}'")
        
        # Referee test
        print("⚖️ Testing referee function...")
        referee_response = client.chat.completions.create(
            model=required_vars["AZURE_OPENAI_MODEL_NAME"],
            messages=[
                {
                    "role": "system",
                    "content": f"""You are a strict referee in the "21 questions" game.
The secret word is: '{secret_word}'.
Answer ONLY with one word:
- "yes" if the secret word IS or BELONGS TO that category,
- "no" if it clearly is not,
- "unclear" if you cannot decide."""
                },
                {
                    "role": "user",
                    "content": "Is it a living thing?"
                }
            ],
            max_tokens=5,
            temperature=0.0
        )
        
        referee_answer = referee_response.choices[0].message.content.strip().lower()
        print(f"⚖️ Referee answer to 'Is it a living thing?': '{referee_answer}'")
        
        print("\n🎉 ALL TESTS PASSED SUCCESSFULLY!")
        print("Your application is ready to work with Azure OpenAI!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR connecting to Azure OpenAI:")
        print(f"   {type(e).__name__}: {str(e)}")
        
        # Additional diagnostics
        if "401" in str(e) or "Unauthorized" in str(e):
            print("\n💡 Possible causes:")
            print("   - Invalid API key")
            print("   - API key expired")
            print("   - Incorrect access permissions")
        elif "404" in str(e) or "NotFound" in str(e):
            print("\n💡 Possible causes:")
            print("   - Invalid endpoint URL")
            print("   - Model not deployed")
            print("   - Incorrect model name")
        elif "429" in str(e) or "RateLimited" in str(e):
            print("\n💡 Possible causes:")
            print("   - Request limit exceeded")
            print("   - Insufficient quota")
        
        return False


if __name__ == "__main__":
    print("🧪 Testing Azure OpenAI for '21 Questions' game")
    print("=" * 60)
    
    success = test_azure_openai_connection()
    
    if success:
        print("\n🚀 You can run the application with:")
        print("   python main_azure.py")
    else:
        print("\n🔧 Fix the errors and run the test again")
        
    print("\n" + "=" * 60)
