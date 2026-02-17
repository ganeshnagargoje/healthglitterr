# Environment Setup Guide (.env file)

This guide shows you how to set up your API keys using a `.env` file for secure and convenient configuration.

---

## Why Use .env File?

**Benefits:**
- ✅ Keep API keys secure (not in code)
- ✅ Easy to manage multiple keys
- ✅ Works across different environments
- ✅ Automatically loaded by the application
- ✅ Never accidentally commit keys to git

---

## Quick Setup (3 steps)

### Step 1: Install python-dotenv

```bash
pip install python-dotenv
```

### Step 2: Create .env File

Create a file named `.env` in your project root directory:

**Project root (recommended):**
```
healthglitterr/
├── .env  ← Create here
├── .env.example
├── .gitignore
├── agentic-medical-health-review/
│   └── ...
```

**Or in the test directory:**
```
agentic-medical-health-review/
└── tests/
    └── tools/
        └── document_data_extraction_tools/
            ├── .env  ← Or create here
            └── test_real_file.py
```

### Step 3: Add Your API Key

Open `.env` and add:

```bash
# OpenAI API Key
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional: Specify default model
LLM_MODEL=gpt-4o-mini
```

**That's it!** The application will automatically load these variables.

---

## Getting Your OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-proj-` or `sk-`)
5. Paste it in your `.env` file

**Important:** Never share your API key or commit it to git!

---

## Complete .env Template

Copy this template to your `.env` file:

```bash
# ============================================
# OpenAI Configuration
# ============================================
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your-openai-api-key-here

# Optional: Organization ID (if you have one)
# OPENAI_ORGANIZATION=org-xxxxxxxxxxxxx

# Optional: Default model for extraction
# LLM_MODEL=gpt-4o-mini

# ============================================
# Alternative LLM Providers (Optional)
# ============================================

# Anthropic (Claude)
# Get key from: https://console.anthropic.com/
# ANTHROPIC_API_KEY=your-anthropic-key-here

# Cohere
# COHERE_API_KEY=your-cohere-key-here

# Hugging Face
# HUGGINGFACE_API_KEY=your-huggingface-key-here

# ============================================
# Other Configuration (Optional)
# ============================================

# Enable debug logging
# DEBUG=true

# Set temperature for LLM (0 = deterministic)
# LLM_TEMPERATURE=0
```

---

## Usage Examples

### Example 1: Basic Usage

Once `.env` is set up, just run your code normally:

```bash
python test_real_file.py ../../test_data/sample_reports/lab_report1_page_1.pdf 
```

The API key is automatically loaded from `.env`!

### Example 2: Python Code

```python
# No need to manually load .env - it's automatic!
from lab_report_parser import extract_structured_lab_data

# This will use the API key from .env
result = extract_structured_lab_data("report.pdf", use_llm=True)
```

---

## Security Best Practices

### ✅ DO:
- Keep `.env` file in your project root
- Add `.env` to `.gitignore` (already done)
- Use different `.env` files for dev/prod
- Rotate API keys regularly
- Use environment-specific files (`.env.local`, `.env.production`)

### ❌ DON'T:
- Commit `.env` to git
- Share `.env` file with others
- Hardcode API keys in code
- Use production keys in development
- Store `.env` in public locations

---

## Multiple Environments

### Development
Create `.env.local`:
```bash
OPENAI_API_KEY=sk-proj-dev-key-here
LLM_MODEL=gpt-4o-mini
DEBUG=true
```

### Production
Create `.env.production`:
```bash
OPENAI_API_KEY=sk-proj-prod-key-here
LLM_MODEL=gpt-4
DEBUG=false
```

Load specific environment:
```python
from dotenv import load_dotenv

# Load production environment
load_dotenv('.env.production')
```

---

## Troubleshooting

### Issue 1: "No module named 'dotenv'"

**Solution:**
```bash
pip install python-dotenv
```

### Issue 2: API key not found

**Symptoms:**
```
Error: OpenAI API key not found
```

**Solutions:**

1. **Check .env file location:**
   ```bash
   # Should be in project root or test directory
   ls -la .env  # Linux/Mac
   dir .env     # Windows
   ```

2. **Check .env file content:**
   ```bash
   cat .env  # Linux/Mac
   type .env # Windows
   ```
   
   Should contain:
   ```
   OPENAI_API_KEY=sk-proj-xxxxx
   ```

3. **Verify python-dotenv is installed:**
   ```bash
   pip show python-dotenv
   ```

4. **Manually load .env:**
   ```python
   from dotenv import load_dotenv
   load_dotenv()  # Explicitly load
   
   import os
   print(os.getenv("OPENAI_API_KEY"))  # Should print your key
   ```

### Issue 3: .env file not loading

**Solution:**
```python
from dotenv import load_dotenv
import os

# Try loading from specific path
load_dotenv('.env')  # Current directory
# or
load_dotenv('../.env')  # Parent directory
# or
load_dotenv('/full/path/to/.env')  # Absolute path

# Verify it loaded
print("API Key loaded:", bool(os.getenv("OPENAI_API_KEY")))
```


## Verification Script

Create `test_env.py` to verify your setup:

```python
#!/usr/bin/env python3
"""Test .env configuration"""

from dotenv import load_dotenv
import os

# Load .env
load_dotenv()

# Check API key
api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    print("✅ .env file loaded successfully!")
    print(f"✅ API key found: {api_key[:10]}...{api_key[-4:]}")
    print(f"✅ Key length: {len(api_key)} characters")
    
    # Check model
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    print(f"✅ Model: {model}")
else:
    print("❌ API key not found!")
    print("\nTroubleshooting:")
    print("1. Create .env file in project root")
    print("2. Add: OPENAI_API_KEY=your-key-here")
    print("3. Install: pip install python-dotenv")
```

Run it:
```bash
python test_env.py
```

---

