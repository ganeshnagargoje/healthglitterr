"""
LLM-Based Structured Lab Data Extractor

Uses an LLM to extract structured lab test data from OCR text.
Much more robust than regex patterns for handling varied formats.
"""

import json
import os
from typing import Dict, List, Optional, Any

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file from current directory or parent directories
except ImportError:
    # python-dotenv not installed, will use system environment variables
    pass


class LLMStructuredExtractor:
    """Extract structured lab data using an LLM."""
    
    def __init__(self, llm=None, model_name: str = "gpt-4o-mini"):
        """
        Initialize the LLM extractor.
        
        Args:
            llm: Optional pre-configured LLM instance (LangChain compatible)
            model_name: Model name to use if llm is not provided
        """
        self.llm = llm
        self.model_name = model_name
        
        if self.llm is None:
            self._initialize_default_llm()
    
    def _initialize_default_llm(self):
        """Initialize a default LLM if none provided."""
        try:
            # Use OpenAI directly (avoids PyTorch dependency issues with LangChain)
            import openai
            self.llm = "openai_direct"  # Flag to use direct OpenAI API
            self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        except ImportError:
            try:
                # Fallback to LangChain if OpenAI package not available
                from langchain_openai import ChatOpenAI
                self.llm = ChatOpenAI(
                    model=self.model_name,
                    temperature=0  # Deterministic for data extraction
                )
            except ImportError:
                # Fallback: user needs to provide their own LLM
                self.llm = None
    
    def extract_structured_data(
        self, 
        raw_text: str, 
        file_path: str = ""
    ) -> Dict[str, Any]:
        """
        Extract structured lab test data from raw OCR text using LLM.
        
        Args:
            raw_text: Raw text extracted from lab report
            file_path: Optional file path for metadata
            
        Returns:
            dict: Structured lab data with format:
            {
                "raw_text": str,
                "tests": [
                    {
                        "test_name": str,
                        "test_value": str,
                        "unit": str,
                        "reference_range": str
                    }
                ],
                "metadata": {
                    "file_path": str,
                    "extraction_status": str,
                    "total_tests_found": int,
                    "extraction_method": "llm"
                }
            }
        """
        if not self.llm:
            return {
                "raw_text": raw_text,
                "tests": [],
                "metadata": {
                    "file_path": file_path,
                    "extraction_status": "error",
                    "error_message": "LLM not initialized. Please configure OPENAI_API_KEY in .env file.",
                    "total_tests_found": 0,
                    "extraction_method": "llm"
                }
            }
        
        if not raw_text or not raw_text.strip():
            return {
                "raw_text": raw_text,
                "tests": [],
                "metadata": {
                    "file_path": file_path,
                    "extraction_status": "no_text",
                    "total_tests_found": 0,
                    "extraction_method": "llm"
                }
            }
        
        try:
            # Create extraction prompt
            prompt = self._create_extraction_prompt(raw_text)
            
            # Call LLM based on type
            if self.llm == "openai_direct":
                # Use OpenAI API directly
                response = self.openai_client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0
                )
                response_content = response.choices[0].message.content
            else:
                # Use LangChain LLM
                response = self.llm.invoke(prompt)
                response_content = response.content
            
            # Parse response
            tests = self._parse_llm_response(response_content)
            
            return {
                "raw_text": raw_text,
                "tests": tests,
                "metadata": {
                    "file_path": file_path,
                    "extraction_status": "success" if tests else "no_tests_found",
                    "total_tests_found": len(tests),
                    "extraction_method": "llm",
                    "model": self.model_name
                }
            }
            
        except Exception as e:
            return {
                "raw_text": raw_text,
                "tests": [],
                "metadata": {
                    "file_path": file_path,
                    "extraction_status": "error",
                    "error_message": str(e),
                    "total_tests_found": 0,
                    "extraction_method": "llm"
                }
            }
    
    def _create_extraction_prompt(self, raw_text: str) -> str:
        """
        Create the extraction prompt for the LLM by loading from template file.
        
        Args:
            raw_text: The OCR text to extract from
            
        Returns:
            str: The complete prompt with OCR text inserted
        """
        try:
            # Try to load prompt from file
            from pathlib import Path
            
            # Get the path to the prompt file
            # Try multiple possible locations
            possible_paths = [
                # Relative to this file
                Path(__file__).parent.parent.parent.parent / "prompts" / "tool_medical_report_extraction_prompt.md",
                # Relative to current directory
                Path("agentic-medical-health-review/prompts/tool_medical_report_extraction_prompt.md"),
                Path("prompts/tool_medical_report_extraction_prompt.md"),
            ]
            
            prompt_template = None
            for prompt_path in possible_paths:
                if prompt_path.exists():
                    with open(prompt_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    # Extract PRIMARY_PROMPT section
                    prompt_template = self._extract_section(content, "PRIMARY_PROMPT")
                    break
            
            if prompt_template:
                # Replace the placeholder with actual OCR text
                return prompt_template.replace("{ocr_text}", raw_text)
            else:
                # Fallback to inline prompt if file not found
                return self._get_fallback_prompt(raw_text)
                
        except Exception as e:
            # If any error occurs, use fallback prompt
            return self._get_fallback_prompt(raw_text)
    
    def _extract_section(self, content: str, section_name: str) -> str:
        """
        Extract a specific section from the prompt file.
        
        Args:
            content: Full content of the prompt file
            section_name: Name of the section to extract (e.g., "PRIMARY_PROMPT")
            
        Returns:
            str: The extracted section content, or empty string if not found
        """
        import re
        
        # Pattern to match section: ## [SECTION_NAME] ... (until next ## [ or end)
        pattern = rf'## \[{section_name}\](.*?)(?=## \[|$)'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            # Get the section content and clean it up
            section_content = match.group(1).strip()
            # Remove the "---" separator if present at the end
            section_content = re.sub(r'\n---\s*$', '', section_content)
            return section_content
        
        return ""
    
    def _get_fallback_prompt(self, raw_text: str) -> str:
        """
        Fallback prompt if template file cannot be loaded.
        Tries to load from FALLBACK_PROMPT section first, then ULTIMATE_FALLBACK, then uses inline.
        
        Args:
            raw_text: The OCR text to extract from
            
        Returns:
            str: The complete prompt
        """
        try:
            # Try to load fallback from file
            from pathlib import Path
            
            possible_paths = [
                Path(__file__).parent.parent.parent.parent / "prompts" / "tool_medical_report_extraction_prompt.md",
                Path("agentic-medical-health-review/prompts/tool_medical_report_extraction_prompt.md"),
                Path("prompts/tool_medical_report_extraction_prompt.md"),
            ]
            
            for prompt_path in possible_paths:
                if prompt_path.exists():
                    with open(prompt_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Try FALLBACK_PROMPT first
                    fallback_template = self._extract_section(content, "FALLBACK_PROMPT")
                    if fallback_template:
                        return fallback_template.replace("{ocr_text}", raw_text)
                    
                    # Try ULTIMATE_FALLBACK if FALLBACK_PROMPT not found
                    ultimate_template = self._extract_section(content, "ULTIMATE_FALLBACK")
                    if ultimate_template:
                        return ultimate_template.replace("{ocr_text}", raw_text)
        except:
            pass
        
        # Ultimate fallback: inline prompt (only if file completely inaccessible)
        return f"""You are a medical lab report data extraction assistant. Extract all lab test results from the following OCR text.

For each test found, extract:
- test_name: The name of the lab test
- test_value: The measured value (numeric)
- unit: The unit of measurement
- reference_range: The normal reference range

Return ONLY a valid JSON array of test objects. Do not include any explanation or markdown formatting.

Example format:
[
  {{
    "test_name": "Glucose",
    "test_value": "95",
    "unit": "mg/dL",
    "reference_range": "70-100"
  }},
  {{
    "test_name": "Hemoglobin",
    "test_value": "14.5",
    "unit": "g/dL",
    "reference_range": "13.5-17.5"
  }}
]

OCR Text:
{raw_text}

Extract all lab tests as JSON array:"""
    
    def _parse_llm_response(self, response: str) -> List[Dict[str, str]]:
        """Parse the LLM response into structured test data."""
        try:
            # Remove markdown code blocks if present
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            # Parse JSON
            tests = json.loads(response)
            
            # Validate structure
            if not isinstance(tests, list):
                return []
            
            # Ensure all required fields are present
            validated_tests = []
            for test in tests:
                if all(key in test for key in ["test_name", "test_value", "unit", "reference_range"]):
                    validated_tests.append({
                        "test_name": str(test["test_name"]),
                        "test_value": str(test["test_value"]),
                        "unit": str(test["unit"]),
                        "reference_range": str(test["reference_range"])
                    })
            
            return validated_tests
            
        except json.JSONDecodeError:
            # If JSON parsing fails, return empty list
            return []

# Convenience function
def extract_with_llm(raw_text: str, file_path: str = "", llm=None, model_name: str = "gpt-4o-mini") -> Dict[str, Any]:
    """
    Convenience function to extract structured data using LLM.
    
    Args:
        raw_text: Raw OCR text from lab report
        file_path: Optional file path for metadata
        llm: Optional pre-configured LLM instance
        model_name: Model name to use if llm is not provided
        
    Returns:
        dict: Structured lab data
    """
    extractor = LLMStructuredExtractor(llm=llm, model_name=model_name)
    return extractor.extract_structured_data(raw_text, file_path)
