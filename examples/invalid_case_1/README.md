# Invalid Case 1: Missing Required Location Fields

## Test Case Details
This invalid case has incomplete location information:
- Canton field is empty
- District field is empty

## Expected Behavior
Should **fail validation** at the Pydantic model level with clear error messages about missing required fields.

## Purpose
Tests that the system properly validates input data and rejects incomplete reports before processing. This ensures:
1. Data quality standards are maintained
2. Users get immediate feedback about missing information
3. Agents don't waste processing time on incomplete data

## Error Messages Expected
- "Canton and district cannot be empty"

## Notes
This is a critical test to ensure the validation layer works correctly. In production, this would prompt the user to complete the form before submission.
