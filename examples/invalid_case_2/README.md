# Invalid Case 2: Too Many Images and Invalid Province

## Test Case Details
This invalid case has multiple violations:
1. **Too many images**: 6 images when max is 5
2. **Invalid province**: "Madrid" is not a Costa Rica province

## Expected Behavior
Should **fail validation** with multiple error messages explaining both issues.

## Purpose
Tests that the system can:
1. Enforce multiple validation rules simultaneously
2. Provide clear error messages for each violation
3. Handle compound validation failures gracefully
4. Ensure geographic data is valid for Costa Rica

## Error Messages Expected
- "Maximum 5 images allowed"
- "Province must be one of: San José, Alajuela, Cartago, Heredia, Guanacaste, Puntarenas, Limón"

## Notes
This tests the robustness of the validation layer with multiple simultaneous failures. In production, the UI should prevent these errors, but backend validation is still essential.
