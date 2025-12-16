"""
Test runner for validating all test cases
"""
import json
import sys
import os
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')

from src.models.pet_models import UserInput, Location
from src.main import load_config, setup_agents, process_pet_report

def test_case(case_name: str, case_path: Path):
    """Run a single test case"""
    print(f"\n{'='*80}")
    print(f"TESTING: {case_name}")
    print(f"{'='*80}\n")
    
    # Load test case
    test_file = case_path / "test_case.json"
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return False
    
    with open(test_file, 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    # Check if this is an invalid test case (should fail validation)
    is_invalid_case = "invalid" in case_name
    
    try:
        # Extract user_input from test case
        input_data = test_data.get("user_input", test_data)
        
        # Create UserInput from test case
        user_input = UserInput(
            report_type=input_data["report_type"],
            location=Location(**input_data["location"]),
            description=input_data["description"],
            images=input_data.get("images", [])
        )
        
        # If we got here and it's an invalid case, validation didn't catch it
        if is_invalid_case:
            print(f"\n❌ {case_name} FAILED - Expected validation error but none occurred")
            return False
        
        print(f"✓ Test case validation passed: {case_name}")
        print(f"  Report type: {user_input.report_type}")
        print(f"  Location: {user_input.location.district}, {user_input.location.province}")
        print(f"  Description length: {len(user_input.description)} chars")
        print(f"  Images: {len(user_input.images)}")
        
        # Load config and setup agents
        config = load_config()
        agent1, agent2, agent3 = setup_agents(config)
        
        # Process the report
        result = process_pet_report(user_input, agent1, agent2, agent3)
        
        if result:
            print(f"\n✓ {case_name} PASSED")
            print(f"  Confidence: {result.matches.confidence_level}")
            print(f"  Matches found: {len(result.matches.candidates)}")
            return True
        else:
            print(f"\n❌ {case_name} FAILED - No result returned")
            return False
            
    except Exception as e:
        # If this is an invalid case, validation error is expected
        if is_invalid_case:
            print(f"\n✓ {case_name} PASSED - Validation correctly rejected invalid input")
            print(f"  Error caught: {str(e)[:100]}")
            return True
        else:
            print(f"\n❌ {case_name} FAILED")
            print(f"  Error: {str(e)}")
            return False

def main():
    """Run all test cases"""
    print("\n" + "="*80)
    print("RUNNING ALL TEST CASES")
    print("="*80)
    
    examples_dir = Path("examples")
    test_cases = [
        "valid_case_1",
        "valid_case_2",
        "edge_case_1",
        "invalid_case_1",
        "invalid_case_2"
    ]
    
    results = {}
    for case_name in test_cases:
        case_path = examples_dir / case_name
        if case_path.exists():
            results[case_name] = test_case(case_name, case_path)
        else:
            print(f"\n❌ Test case directory not found: {case_path}")
            results[case_name] = False
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for case_name, passed_test in results.items():
        status = "✓ PASSED" if passed_test else "❌ FAILED"
        print(f"  {case_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*80 + "\n")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
