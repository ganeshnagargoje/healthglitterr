# Analysis Computation Tools Tests

This directory contains tests for the analysis computation tools used in the medical health review system.

## Test Files

### test_mismatch_detection_tool.py

Comprehensive test suite for the mismatch detection tool that validates lab parameter values against reference ranges.

#### Test Coverage

1. **TestDetectMismatch** - Core mismatch detection functionality
   - Values above reference range
   - Values below reference range
   - Values within reference range
   - Values at boundaries (edge cases)
   - Missing reference ranges
   - Partial reference ranges (only min or only max)

2. **TestSeverityCalculation** - Severity classification
   - Mild severity (< 10% deviation)
   - Moderate severity (10-25% deviation)
   - Severe severity (>= 25% deviation)
   - Zero deviation handling

3. **TestDeviationPercentage** - Deviation calculation accuracy
   - Above range deviation calculation
   - Below range deviation calculation
   - Percentage accuracy validation

4. **TestBatchDetection** - Batch processing
   - All values within range
   - All values with mismatches
   - Mixed results
   - Empty list handling

5. **TestEdgeCases** - Edge case handling
   - Extremely high values
   - Extremely low values
   - Zero values
   - Negative values

6. **TestRealWorldScenarios** - Medical scenarios
   - Prediabetic glucose levels
   - High cholesterol
   - Low hemoglobin (anemia)

### test_trend_computation_tool.py

Comprehensive test suite for the trend computation tool that analyzes temporal patterns in lab parameters.

#### Test Coverage

1. **TestComputeTrend** - Core trend detection functionality
   - Increasing trend detection
   - Decreasing trend detection
   - Stable trend detection
   - Insufficient data handling (< 2 points)
   - Minimum data points (exactly 2)
   - Unsorted timestamp handling
   - Multiple timestamp formats

2. **TestConfidenceScore** - Confidence calculation
   - High confidence with consistent trends
   - Low confidence with erratic values
   - Confidence scaling with data point count

3. **TestTimeSpan** - Time span calculation
   - Multi-day measurements
   - Same-day measurements
   - Time span accuracy

4. **TestBatchTrendComputation** - Batch processing
   - Multiple parameters
   - Mixed sufficient/insufficient data
   - Empty batch handling

5. **TestEdgeCases** - Edge case handling
   - Zero initial values
   - Negative values
   - Identical values
   - Very large values

6. **TestSlopeCalculation** - Linear regression slope
   - Positive slope
   - Negative slope
   - Zero slope

7. **TestStandardDeviation** - Statistical calculations
   - Standard deviation accuracy
   - Identical values (zero std dev)
   - Single value handling

8. **TestRealWorldScenarios** - Medical scenarios
   - Diabetes progression
   - Cholesterol improvement
   - Stable well-controlled parameters

9. **TestPercentageChange** - Percentage calculations
   - Positive changes
   - Negative changes
   - Small changes (stable threshold)

10. **TestTimestampFormats** - Format parsing
    - ISO format with timezone
    - Date-only format

## Running Tests

### Run all analysis computation tools tests:
```bash
pytest agentic-medical-health-review/tests/tools/analysis_computation_tools/ -v
```

### Run specific test file:
```bash
pytest agentic-medical-health-review/tests/tools/analysis_computation_tools/test_mismatch_detection_tool.py -v
pytest agentic-medical-health-review/tests/tools/analysis_computation_tools/test_trend_computation_tool.py -v
```

### Run specific test class:
```bash
pytest agentic-medical-health-review/tests/tools/analysis_computation_tools/test_mismatch_detection_tool.py::TestDetectMismatch -v
pytest agentic-medical-health-review/tests/tools/analysis_computation_tools/test_trend_computation_tool.py::TestComputeTrend -v
```

### Run specific test:
```bash
pytest agentic-medical-health-review/tests/tools/analysis_computation_tools/test_mismatch_detection_tool.py::TestDetectMismatch::test_value_above_range -v
```

### Run with coverage:
```bash
pytest agentic-medical-health-review/tests/tools/analysis_computation_tools/ --cov=tools.src.analysis_computation_tools --cov-report=html
```

## Test Data

### Mismatch Detection Tests
Tests use `NormalizedParameter` objects with various configurations to simulate different medical scenarios:
- Normal glucose levels (3.9-6.1 mmol/L)
- Prediabetic glucose levels (6.1-7.0 mmol/L)
- High cholesterol (> 5.2 mmol/L)
- Low hemoglobin (< 12.0 g/dL)

### Trend Computation Tests
Tests use time-series data points with datetime timestamps to simulate:
- Diabetes progression over months
- Cholesterol improvement with treatment
- Stable well-controlled parameters
- Various edge cases and data quality scenarios

## Dependencies

- pytest
- pydantic (for model validation)
- Python 3.8+

## Notes

- Tests are independent and can run in any order
- No database connection required (uses in-memory objects)
- All test data is self-contained within the test files
- Total: 61 tests (27 mismatch + 34 trend)
