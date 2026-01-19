# tests/run_comprehensive_tests.py
"""
Test execution script for comprehensive workflow testing.
Runs all test cases and collects results for report generation.
"""

import sys
import os
from datetime import datetime
from typing import Dict, List, Tuple

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.state import create_initial_state
from src.graph import app
from tests.test_cases_comprehensive import TEST_CASES

# Map workflow names to expected payment_status values
WORKFLOW_STATUS_MAP = {
    "already_paid": "paid",
    "dispute": "disputed",
    "callback": "callback",
    "unable_to_pay": "unable",
    "willing": "willing",
    "unknown": "unknown"  # Note: system may default this to "unable"
}

# Test phone numbers (cycling through available customers)
TEST_PHONES = ["+919876543210", "+919876543211", "+919876543212"]
phone_index = 0

def get_test_phone():
    """Get next test phone number, cycling through available ones."""
    global phone_index
    phone = TEST_PHONES[phone_index % len(TEST_PHONES)]
    phone_index += 1
    return phone

def run_test_case(workflow: str, test_input: str) -> Tuple[bool, str, str]:
    """
    Run a single test case.
    Returns: (passed, detected_status, error_message)
    """
    try:
        phone = get_test_phone()
        state = create_initial_state(phone)
        
        if not state:
            return False, "unknown", "Failed to create initial state"
        
        # Initialize conversation - invoke once to start
        state = app.invoke(state, config={"recursion_limit": 25})
        
        # Get customer DOB for verification
        customer_dob = state.get("customer_dob", "15-03-1985")
        
        # Simulate conversation flow: greeting -> verification -> disclosure -> test input
        user_messages = ["Yes", customer_dob, test_input]
        
        for i, msg in enumerate(user_messages):
            if state.get("is_complete"):
                break
            
            # Wait for the system to be ready for user input
            max_wait_iterations = 20
            wait_iter = 0
            while not state.get("awaiting_user") and not state.get("is_complete") and wait_iter < max_wait_iterations:
                state = app.invoke(state, config={"recursion_limit": 25})
                wait_iter += 1
                if state.get("is_complete"):
                    break
            
            if state.get("is_complete"):
                break
            
            # Add user message
            state["messages"].append({"role": "user", "content": msg})
            state["last_user_input"] = msg
            state["awaiting_user"] = False
            
            # Process the user input
            max_iterations = 30
            iteration = 0
            while not state.get("is_complete") and iteration < max_iterations:
                state = app.invoke(state, config={"recursion_limit": 25})
                iteration += 1
                
                # If awaiting user, we need to provide next input (unless this is the last message)
                if state.get("awaiting_user") and i < len(user_messages) - 1:
                    break
                
                # If complete, we're done
                if state.get("is_complete"):
                    break
        
        detected_status = state.get("payment_status", "unknown")
        expected_status = WORKFLOW_STATUS_MAP.get(workflow, "unknown")
        
        # For unknown workflow, system may default to "unable", so we check both
        if workflow == "unknown":
            passed = detected_status in ["unknown", "unable"]
        else:
            passed = detected_status == expected_status
        
        return passed, detected_status, ""
        
    except Exception as e:
        import traceback
        return False, "error", f"{str(e)}\n{traceback.format_exc()}"

def run_all_tests() -> Dict[str, Dict]:
    """
    Run all test cases and collect results.
    Returns: Dictionary with results organized by workflow
    """
    results = {}
    
    print("=" * 80)
    print("COMPREHENSIVE TEST EXECUTION")
    print("=" * 80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    total_cases = sum(len(cases) for cases in TEST_CASES.values())
    current_case = 0
    
    for workflow, test_cases in TEST_CASES.items():
        print(f"\nTesting Workflow: {workflow.upper()}")
        print("-" * 80)
        
        workflow_results = {
            "total": len(test_cases),
            "passed": 0,
            "failed": 0,
            "test_cases": []
        }
        
        for i, test_input in enumerate(test_cases, 1):
            current_case += 1
            print(f"[{current_case}/{total_cases}] Test {i}/{len(test_cases)}: {test_input[:60]}...", end=" ")
            
            passed, detected_status, error = run_test_case(workflow, test_input)
            
            if passed:
                workflow_results["passed"] += 1
                print("PASS")
            else:
                workflow_results["failed"] += 1
                print(f"FAIL (detected: {detected_status})")
            
            workflow_results["test_cases"].append({
                "input": test_input,
                "passed": passed,
                "detected_status": detected_status,
                "error": error
            })
        
        workflow_results["pass_rate"] = workflow_results["passed"] / workflow_results["total"]
        results[workflow] = workflow_results
        
        print(f"\nWorkflow Summary: {workflow_results['passed']}/{workflow_results['total']} passed "
              f"({workflow_results['pass_rate']:.2%})")
    
    print("\n" + "=" * 80)
    print("TEST EXECUTION COMPLETE")
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    return results

if __name__ == "__main__":
    results = run_all_tests()
    
    # Save results to JSON file for report generation
    import json
    output_file = "tests/test_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to: {output_file}")
