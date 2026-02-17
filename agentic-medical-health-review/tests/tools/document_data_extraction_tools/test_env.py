#!/usr/bin/env python3
"""
Test .env Configuration

Run this script to verify your .env file is set up correctly.
"""

import sys
import os

def test_env_setup():
    """Test if .env file is configured correctly."""
    
    print("="*70)
    print("Environment Configuration Test")
    print("="*70)
    
    # Try to load dotenv
    print("\n1. Checking python-dotenv...")
    try:
        from dotenv import load_dotenv
        print("   ✅ python-dotenv is installed")
        
        # Load .env file
        load_dotenv()
        print("   ✅ .env file loaded")
    except ImportError:
        print("   ❌ python-dotenv not installed")
        print("\n   Install with: pip install python-dotenv")
        return False
    
    # Check for API key
    print("\n2. Checking OpenAI API key...")
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("   ❌ OPENAI_API_KEY not found")
        print("\n   Troubleshooting:")
        print("   1. Create .env file in project root")
        print("   2. Add: OPENAI_API_KEY=your-key-here")
        print("   3. Get key from: https://platform.openai.com/api-keys")
        return False
    
    # Validate API key format
    if not api_key.startswith(('sk-', 'sk-proj-')):
        print(f"   ⚠ Warning: API key format looks unusual")
        print(f"   Key starts with: {api_key[:10]}")
        print("   OpenAI keys usually start with 'sk-' or 'sk-proj-'")
    else:
        print(f"   ✅ API key found: {api_key[:10]}...{api_key[-4:]}")
        print(f"   ✅ Key length: {len(api_key)} characters")
    
    # Check model configuration
    print("\n3. Checking model configuration...")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    print(f"   ✅ Model: {model}")
    
    # Check optional configurations
    print("\n4. Checking optional configurations...")
    
    org_id = os.getenv("OPENAI_ORGANIZATION")
    if org_id:
        print(f"   ✅ Organization ID: {org_id[:10]}...")
    else:
        print("   ℹ Organization ID: Not set (optional)")
    
    debug = os.getenv("DEBUG", "false").lower() == "true"
    print(f"   ℹ Debug mode: {debug}")
    
    # Test LangChain import
    print("\n5. Checking LangChain installation...")
    try:
        from langchain_openai import ChatOpenAI
        print("   ✅ langchain-openai is installed")
        
        # Try to create LLM instance
        try:
            llm = ChatOpenAI(model=model, temperature=0)
            print("   ✅ LLM instance created successfully")
        except Exception as e:
            print(f"   ⚠ Warning: Could not create LLM instance: {e}")
    except ImportError:
        print("   ⚠ langchain-openai not installed (optional)")
        print("   Install with: pip install langchain langchain-openai")
    
    # Summary
    print("\n" + "="*70)
    print("Summary")
    print("="*70)
    print("\n✅ Configuration looks good!")
    print("\nNext steps:")
    print("1. Test extraction: python test_real_file.py report.pdf --llm")
    print("2. See LLM_EXTRACTION_GUIDE.md for usage examples")
    
    return True


if __name__ == "__main__":
    success = test_env_setup()
    sys.exit(0 if success else 1)
