# Prompt Management Guide

This guide explains how to manage multiple prompts in a single file using section markers.

---

## File Structure

Prompts are organized using section markers in markdown files:

```markdown
## [SECTION_NAME]

Your prompt content here...

---

## [ANOTHER_SECTION]

Another prompt here...
```

---

## Section Naming Convention

Use descriptive, uppercase names with underscores:

- `[PRIMARY_PROMPT]` - Main prompt used in production
- `[FALLBACK_PROMPT]` - Simplified backup prompt
- `[EXPERIMENTAL_PROMPT]` - Testing new approaches
- `[VERBOSE_PROMPT]` - Detailed version with more instructions
- `[CONCISE_PROMPT]` - Minimal version for cost optimization

---

## Example: tool_medical_report_extraction_prompt.md

```markdown
# Medical Lab Report Data Extraction Prompts

## [PRIMARY_PROMPT]

You are a medical lab report data extraction assistant...

{ocr_text}

---

## [FALLBACK_PROMPT]

Simplified version of the prompt...

{ocr_text}

---

## [EXPERIMENTAL_PROMPT]

Testing a new approach...

{ocr_text}
```

---

## Using Placeholders

Use `{variable_name}` for dynamic content:

```markdown
## [MY_PROMPT]

Extract data from this text:

{input_text}

Additional context: {context}
```

In code:
```python
prompt = template.replace("{input_text}", actual_text)
prompt = prompt.replace("{context}", context_info)
```

---

## Code Integration

### Loading a Specific Section

```python
def _extract_section(self, content: str, section_name: str) -> str:
    """Extract a specific section from the prompt file."""
    import re
    
    # Pattern: ## [SECTION_NAME] ... (until next ## [ or end)
    pattern = rf'## \[{section_name}\](.*?)(?=## \[|$)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    return ""
```

### Using in Your Code

```python
# Load file
with open('prompts/my_prompts.md', 'r') as f:
    content = f.read()

# Extract specific section
primary = self._extract_section(content, "PRIMARY_PROMPT")
fallback = self._extract_section(content, "FALLBACK_PROMPT")

# Replace placeholders
prompt = primary.replace("{ocr_text}", actual_text)
```

---

## Best Practices

### 1. Always Include a Fallback

```markdown
## [PRIMARY_PROMPT]
Detailed prompt with all features...

## [FALLBACK_PROMPT]
Simplified version that always works...
```

### 2. Document Each Section

```markdown
## [PRIMARY_PROMPT]
<!-- Used in production. Optimized for accuracy. -->

Your prompt here...

## [EXPERIMENTAL_PROMPT]
<!-- Testing new approach. Not for production. -->

Experimental prompt...
```

### 3. Use Consistent Placeholders

```markdown
## [PROMPT_V1]
Extract from: {input_text}

## [PROMPT_V2]
Extract from: {input_text}  <!-- Same placeholder name -->
```

### 4. Version Your Prompts

```markdown
## [EXTRACTION_V1]
Original version...

## [EXTRACTION_V2]
Improved version with better instructions...

## [EXTRACTION_V3]
Latest version with examples...
```

---

## Advanced Patterns

### A/B Testing

```markdown
## [VARIANT_A]
Approach A: Step-by-step instructions...

## [VARIANT_B]
Approach B: Example-driven instructions...
```

In code:
```python
import random

# Randomly select variant for A/B testing
variant = random.choice(["VARIANT_A", "VARIANT_B"])
prompt = self._extract_section(content, variant)
```

### Conditional Prompts

```markdown
## [SIMPLE_EXTRACTION]
For simple reports with standard format...

## [COMPLEX_EXTRACTION]
For complex reports with multiple formats...
```

In code:
```python
# Choose based on complexity
section = "COMPLEX_EXTRACTION" if is_complex else "SIMPLE_EXTRACTION"
prompt = self._extract_section(content, section)
```

### Language-Specific Prompts

```markdown
## [PROMPT_EN]
English instructions...

## [PROMPT_ES]
Instrucciones en español...

## [PROMPT_FR]
Instructions en français...
```

---

## Migration Guide

### From Inline Prompts

**Before:**
```python
def get_prompt(self, text):
    return f"""Extract data from: {text}"""
```

**After:**
```python
def get_prompt(self, text):
    content = self._load_prompt_file()
    template = self._extract_section(content, "PRIMARY_PROMPT")
    return template.replace("{text}", text)
```

### From Separate Files

**Before:**
```
prompts/
├── primary_prompt.txt
├── fallback_prompt.txt
└── experimental_prompt.txt
```

**After:**
```
prompts/
└── all_prompts.md  # Contains [PRIMARY_PROMPT], [FALLBACK_PROMPT], [EXPERIMENTAL_PROMPT]
```

---

## Testing Your Prompts

### Test Script

```python
def test_prompt_sections():
    """Test that all sections can be loaded."""
    with open('prompts/my_prompts.md', 'r') as f:
        content = f.read()
    
    sections = ["PRIMARY_PROMPT", "FALLBACK_PROMPT"]
    
    for section in sections:
        prompt = extract_section(content, section)
        assert prompt, f"Section {section} not found"
        assert "{ocr_text}" in prompt, f"Placeholder missing in {section}"
        print(f"✓ {section} loaded successfully")
```

---

## Common Issues

### Issue 1: Section Not Found

**Problem:** `_extract_section()` returns empty string

**Solutions:**
- Check section name spelling: `[PRIMARY_PROMPT]` not `[Primary_Prompt]`
- Ensure section marker format: `## [NAME]` with space after `##`
- Verify file encoding is UTF-8

### Issue 2: Placeholder Not Replaced

**Problem:** `{ocr_text}` appears in final prompt

**Solution:**
```python
# Make sure to replace ALL placeholders
prompt = template.replace("{ocr_text}", text)
prompt = prompt.replace("{context}", context)
```

### Issue 3: Extra Whitespace

**Problem:** Prompt has extra newlines or spaces

**Solution:**
```python
section_content = match.group(1).strip()
# Remove trailing separator
section_content = re.sub(r'\n---\s*$', '', section_content)
```

---

## Examples

See these files for working examples:
- `tool_medical_report_extraction_prompt.md` - Multiple prompts in one file
- `llm_structured_extractor.py` - Code that loads sections

---

## Summary

**Benefits of Section-Based Prompts:**
- ✅ Single file for related prompts
- ✅ Easy to compare versions
- ✅ Better version control
- ✅ Reduced file clutter
- ✅ Consistent formatting

**When to Use:**
- Multiple versions of same prompt
- A/B testing variants
- Primary + fallback prompts
- Language variations
- Experimental prompts
