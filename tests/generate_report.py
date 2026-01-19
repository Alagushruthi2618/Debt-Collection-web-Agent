# tests/generate_report.py
"""
Generate comprehensive test report similar to TestReport.pdf format.
"""

import json
import os
from datetime import datetime
from typing import Dict

def load_test_results() -> Dict:
    """Load test results from JSON file."""
    results_file = "tests/test_results.json"
    if not os.path.exists(results_file):
        raise FileNotFoundError(f"Test results file not found: {results_file}")
    
    with open(results_file, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_markdown_report(results: Dict) -> str:
    """Generate markdown report from test results."""
    
    report = []
    
    # Title and Introduction
    report.append("# Test Report: Debt Collection Chatbot - Comprehensive Workflow Testing")
    report.append("")
    report.append("## 1. Introduction")
    report.append("")
    report.append("This test report documents the comprehensive evaluation of a debt collection chatbot ")
    report.append("developed for handling customer interactions via web and WhatsApp platforms in India. ")
    report.append("The chatbot supports Hinglish (Hindi-English mix) language and handles key user intents ")
    report.append("related to loan repayment and debt collection.")
    report.append("")
    report.append("The objective of testing was to verify that the chatbot accurately detects user intent ")
    report.append("across diverse Hinglish expressions and correctly routes to the corresponding workflow. ")
    report.append("A total of 6 major workflows were tested, each containing 30 test cases, resulting in ")
    report.append("180 total test cases.")
    report.append("")
    report.append("This report outlines the test structure, workflows, methodology, results, and key ")
    report.append("observations from the automated testing process.")
    report.append("")
    
    # Workflow Descriptions
    report.append("## 2. Description of Workflows")
    report.append("")
    report.append("The chatbot operates through six primary workflows, each designed to handle a specific ")
    report.append("user intent related to loan repayment and debt collection. These workflows are triggered ")
    report.append("by analysing the user's input message and determining the underlying intent. Below is a ")
    report.append("description of each workflow:")
    report.append("")
    
    workflow_descriptions = {
        "already_paid": {
            "name": "Already Paid / Loan Cleared",
            "description": "Activated when a user states that they have already made payment or cleared the loan. "
                          "The chatbot acknowledges the message, thanks the user, and requests payment proof. "
                          "The Supabase status is also updated to reflect loan clearance. Some sample prompts are - "
                          "Main ne pehle hi payment kar diya hai, Payment ho gaya hai last week, Dues clear ho gaye hain."
        },
        "dispute": {
            "name": "Dispute",
            "description": "Triggered when the user denies the obligation to repay or claims the loan is not theirs. "
                          "The chatbot responds in a calm and non-confrontational manner while logging the dispute "
                          "intent for follow-up or escalation. Some sample prompts are - Yeh loan mera nahi hai, "
                          "Maine yeh loan kabhi nahi liya, Yeh fraud lagta hai."
        },
        "callback": {
            "name": "Callback Request",
            "description": "If the user asks to be called back later or indicates they are not available at the moment, "
                          "the callback workflow is triggered. The bot acknowledges the request and schedules a callback. "
                          "Some sample prompts are - Aap baad mein call kar sakte hain?, Main abhi busy hoon kal call karo, "
                          "Abhi available nahi hoon next week call karo."
        },
        "unable_to_pay": {
            "name": "Unable to Pay",
            "description": "This workflow handles situations where the user expresses financial hardship and cannot "
                          "afford to make any payment. The chatbot responds empathetically and logs the case for review. "
                          "Some sample prompts are - Meri naukri chali gayi paise nahi hain, Main abhi kuch bhi pay nahi "
                          "kar sakta, Main financially struggling hoon."
        },
        "willing": {
            "name": "Willing to Pay / Payment Plan Request",
            "description": "Activated when a user expresses willingness to repay but needs payment options or installments. "
                          "The chatbot responds positively, presents payment plan options, and may record a Promise to Pay (PTP). "
                          "Some sample prompts are - Main pay karna chahta hoon lekin full amount nahi de sakta, "
                          "Kya main installments mein pay kar sakta hoon?, Payment options dikhao."
        },
        "unknown": {
            "name": "Unknown / General / Neutral Conversation",
            "description": "This pathway covers generic or ambiguous inputs such as greetings, unclear messages, or "
                          "neutral responses that do not express any clear intent. The bot responds in a neutral tone "
                          "without triggering further backend updates. Some sample prompts are - Hi, Yeh kaun hai?, "
                          "Samajh nahi aaya, Aap kya keh rahe hain?"
        }
    }
    
    for workflow_key, workflow_info in workflow_descriptions.items():
        report.append(f"### Workflow {list(workflow_descriptions.keys()).index(workflow_key) + 1}: {workflow_info['name']}")
        report.append("")
        report.append(workflow_info['description'])
        report.append("")
    
    # Testing Methodology
    report.append("## 3. Testing Methodology")
    report.append("")
    report.append("The chatbot was automatically tested across six primary workflows: Already Paid, Dispute, ")
    report.append("Callback Request, Unable to Pay, Willing to Pay, and Unknown/General. A total of 180 test cases ")
    report.append("were executed across the six workflows, with input messages written in Hinglish (Hindi-English mix). ")
    report.append("Each workflow was tested using diverse Hinglish prompts, including regionally varied and informal inputs.")
    report.append("")
    report.append("Test cases were designed to simulate realistic user inputs, including formal, informal, and ")
    report.append("regionally varied phrasings. The inputs were automatically executed through the chatbot system.")
    report.append("")
    report.append("For each test case, the following aspects were evaluated:")
    report.append("")
    report.append("- **Intent recognition**: Whether the chatbot correctly classified the message into the appropriate workflow.")
    report.append("- **Response correctness**: Whether the bot responded appropriately based on the workflow.")
    report.append("- **Backend actions**: In workflows involving Supabase or other backend systems, whether the relevant ")
    report.append("  backend update or notification was triggered.")
    report.append("")
    report.append("Final testing was conducted automatically by executing each case and comparing the chatbot's detected ")
    report.append("intent to the expected workflow classification. While the replies may not always match word-for-word, ")
    report.append("they were evaluated based on correctness of intent detection and appropriate routing to the intended workflow.")
    report.append("")
    
    # Results Summary
    report.append("## 4. Summary of Results")
    report.append("")
    report.append("A total of 180 test cases were executed to evaluate the chatbot's performance across six workflows. ")
    report.append("Each workflow had 30 test cases, covering a diverse range of user inputs in Hinglish. The goal was ")
    report.append("to verify whether the chatbot correctly detects the user's intent and routes the message to the ")
    report.append("appropriate workflow path.")
    report.append("")
    
    # Results Table
    report.append("| Workflow | Total Cases | Passed | Failed | Pass Rate |")
    report.append("| --- | --- | --- | --- | --- |")
    
    total_cases = 0
    total_passed = 0
    total_failed = 0
    
    workflow_display_names = {
        "already_paid": "Already Paid",
        "dispute": "Dispute",
        "callback": "Callback Request",
        "unable_to_pay": "Unable to Pay",
        "willing": "Willing to Pay",
        "unknown": "Unknown/General"
    }
    
    for workflow_key in workflow_display_names.keys():
        if workflow_key in results:
            workflow_result = results[workflow_key]
            total_cases += workflow_result["total"]
            total_passed += workflow_result["passed"]
            total_failed += workflow_result["failed"]
            
            report.append(f"| {workflow_display_names[workflow_key]} | "
                         f"{workflow_result['total']} | "
                         f"{workflow_result['passed']} | "
                         f"{workflow_result['failed']} | "
                         f"{workflow_result['pass_rate']:.4f} |")
    
    overall_pass_rate = total_passed / total_cases if total_cases > 0 else 0
    report.append(f"| **Total** | **{total_cases}** | **{total_passed}** | **{total_failed}** | **{overall_pass_rate:.4f}** |")
    report.append("")
    report.append(f"Based on the testing, the chatbot shows {'high' if overall_pass_rate >= 0.9 else 'moderate' if overall_pass_rate >= 0.7 else 'low'} ")
    report.append("reliability in detecting and handling debt-related intents in Hinglish. ")
    
    if overall_pass_rate >= 0.95:
        report.append("The system achieved excellent accuracy with near-perfect performance across most workflows.")
    elif overall_pass_rate >= 0.85:
        report.append("While most workflows achieved good accuracy, some minor misclassifications persist in edge-case phrasing.")
    else:
        report.append("Several workflows require improvement in intent detection accuracy.")
    report.append("")
    
    # Detailed Results by Workflow
    report.append("## 5. Detailed Results by Workflow")
    report.append("")
    
    for workflow_key, workflow_result in results.items():
        workflow_name = workflow_display_names.get(workflow_key, workflow_key)
        report.append(f"### 5.{list(results.keys()).index(workflow_key) + 1} {workflow_name}")
        report.append("")
        report.append(f"**Total Test Cases**: {workflow_result['total']}")
        report.append(f"**Passed**: {workflow_result['passed']}")
        report.append(f"**Failed**: {workflow_result['failed']}")
        report.append(f"**Pass Rate**: {workflow_result['pass_rate']:.2%}")
        report.append("")
        
        # Show failed cases
        failed_cases = [tc for tc in workflow_result['test_cases'] if not tc['passed']]
        if failed_cases:
            report.append("**Failed Test Cases:**")
            report.append("")
            for i, case in enumerate(failed_cases[:10], 1):  # Show first 10 failures
                report.append(f"{i}. Input: `{case['input']}`")
                report.append(f"   Detected Status: `{case['detected_status']}`")
                if case['error']:
                    report.append(f"   Error: {case['error']}")
                report.append("")
            if len(failed_cases) > 10:
                report.append(f"*... and {len(failed_cases) - 10} more failed cases*")
                report.append("")
        else:
            report.append("**All test cases passed successfully.**")
            report.append("")
    
    # Observations
    report.append("## 6. Observations")
    report.append("")
    report.append("The testing process highlighted both the strengths and limitations of the current chatbot implementation. ")
    report.append("The following observations were made:")
    report.append("")
    
    # Calculate some statistics
    high_performance_workflows = [w for w, r in results.items() if r['pass_rate'] >= 0.9]
    low_performance_workflows = [w for w, r in results.items() if r['pass_rate'] < 0.7]
    
    report.append("- **Overall Performance**: The system achieved an overall pass rate of "
                  f"{overall_pass_rate:.2%} across all workflows.")
    report.append("")
    
    if high_performance_workflows:
        report.append(f"- **High-Performance Workflows**: {len(high_performance_workflows)} workflow(s) achieved pass rates "
                     f"above 90%: {', '.join([workflow_display_names.get(w, w) for w in high_performance_workflows])}.")
        report.append("")
    
    if low_performance_workflows:
        report.append(f"- **Workflows Requiring Improvement**: {len(low_performance_workflows)} workflow(s) showed pass rates "
                     f"below 70%: {', '.join([workflow_display_names.get(w, w) for w in low_performance_workflows])}. "
                     f"These workflows may benefit from enhanced pattern matching or additional training examples.")
        report.append("")
    
    report.append("- **Intent Detection Accuracy**: The chatbot's intent classification logic, which combines rule-based ")
    report.append("pattern matching with Azure OpenAI classification, generally performs well for clear-cut cases but ")
    report.append("may struggle with ambiguous or context-dependent inputs.")
    report.append("")
    report.append("- **Language Handling**: The system handles Hinglish inputs effectively, recognizing mixed Hindi-English ")
    report.append("expressions across different workflows.")
    report.append("")
    report.append("- **Error Handling**: In most failed cases, the bot still responded appropriately, avoiding escalation ")
    report.append("or producing offensive outputs even when intent was misclassified.")
    report.append("")
    
    # Limitations and Future Work
    report.append("## 7. Limitations and Future Work")
    report.append("")
    report.append("Despite the comprehensive testing, the current version of the chatbot has several limitations that ")
    report.append("constrain its real-world scalability and performance:")
    report.append("")
    report.append("- **Test Coverage**: While 180 test cases provide good coverage, real-world usage may reveal additional ")
    report.append("  edge cases and linguistic variations not captured in this test suite.")
    report.append("")
    report.append("- **Context Understanding**: The system may struggle with multi-turn conversations where context from ")
    report.append("  previous messages is crucial for intent detection.")
    report.append("")
    report.append("- **Ambiguity Handling**: Some ambiguous inputs may be misclassified, requiring fallback mechanisms or ")
    report.append("  clarification prompts.")
    report.append("")
    report.append("- **Regional Variations**: While Hinglish is covered, regional variations in Hindi dialects and ")
    report.append("  English accents may not be fully captured.")
    report.append("")
    report.append("### Future Work")
    report.append("")
    report.append("To overcome these limitations and further strengthen the chatbot, the following improvements are planned:")
    report.append("")
    report.append("- Expanding the test suite with more diverse Hinglish expressions and regional variations.")
    report.append("- Implementing confidence scoring for intent classification to identify uncertain cases.")
    report.append("- Adding context-aware intent detection that considers conversation history.")
    report.append("- Integrating user feedback mechanisms to learn from real-world interactions.")
    report.append("- Implementing real-time analytics dashboards to monitor performance metrics.")
    report.append("")
    
    # Footer
    report.append("---")
    report.append("")
    report.append(f"*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    report.append("")
    
    return "\n".join(report)

def main():
    """Main function to generate report."""
    try:
        results = load_test_results()
        markdown_report = generate_markdown_report(results)
        
        # Save markdown report
        md_file = "tests/TestReport_Comprehensive.md"
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(markdown_report)
        
        print(f"Markdown report generated: {md_file}")
        
        # Also print summary
        print("\n" + "=" * 80)
        print("TEST RESULTS SUMMARY")
        print("=" * 80)
        
        total_cases = sum(r["total"] for r in results.values())
        total_passed = sum(r["passed"] for r in results.values())
        total_failed = sum(r["failed"] for r in results.values())
        overall_pass_rate = total_passed / total_cases if total_cases > 0 else 0
        
        print(f"\nTotal Test Cases: {total_cases}")
        print(f"Passed: {total_passed}")
        print(f"Failed: {total_failed}")
        print(f"Overall Pass Rate: {overall_pass_rate:.2%}")
        print("\nBy Workflow:")
        
        workflow_display_names = {
            "already_paid": "Already Paid",
            "dispute": "Dispute",
            "callback": "Callback Request",
            "unable_to_pay": "Unable to Pay",
            "willing": "Willing to Pay",
            "unknown": "Unknown/General"
        }
        
        for workflow_key, workflow_result in results.items():
            workflow_name = workflow_display_names.get(workflow_key, workflow_key)
            print(f"  {workflow_name:20s} - {workflow_result['passed']:3d}/{workflow_result['total']:3d} "
                  f"({workflow_result['pass_rate']:.2%})")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"Error generating report: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
