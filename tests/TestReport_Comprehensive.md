# Test Report: Debt Collection Chatbot - Comprehensive Workflow Testing

## 1. Introduction

This test report documents the comprehensive evaluation of a debt collection chatbot 
developed for handling customer interactions via web and WhatsApp platforms in India. 
The chatbot supports Hinglish (Hindi-English mix) language and handles key user intents 
related to loan repayment and debt collection.

The objective of testing was to verify that the chatbot accurately detects user intent 
across diverse Hinglish expressions and correctly routes to the corresponding workflow. 
A total of 6 major workflows were tested, each containing 30 test cases, resulting in 
180 total test cases.

This report outlines the test structure, workflows, methodology, results, and key 
observations from the automated testing process.

## 2. Description of Workflows

The chatbot operates through six primary workflows, each designed to handle a specific 
user intent related to loan repayment and debt collection. These workflows are triggered 
by analysing the user's input message and determining the underlying intent. Below is a 
description of each workflow:

### Workflow 1: Already Paid / Loan Cleared

Activated when a user states that they have already made payment or cleared the loan. The chatbot acknowledges the message, thanks the user, and requests payment proof. The Supabase status is also updated to reflect loan clearance. Some sample prompts are - Main ne pehle hi payment kar diya hai, Payment ho gaya hai last week, Dues clear ho gaye hain.

### Workflow 2: Dispute

Triggered when the user denies the obligation to repay or claims the loan is not theirs. The chatbot responds in a calm and non-confrontational manner while logging the dispute intent for follow-up or escalation. Some sample prompts are - Yeh loan mera nahi hai, Maine yeh loan kabhi nahi liya, Yeh fraud lagta hai.

### Workflow 3: Callback Request

If the user asks to be called back later or indicates they are not available at the moment, the callback workflow is triggered. The bot acknowledges the request and schedules a callback. Some sample prompts are - Aap baad mein call kar sakte hain?, Main abhi busy hoon kal call karo, Abhi available nahi hoon next week call karo.

### Workflow 4: Unable to Pay

This workflow handles situations where the user expresses financial hardship and cannot afford to make any payment. The chatbot responds empathetically and logs the case for review. Some sample prompts are - Meri naukri chali gayi paise nahi hain, Main abhi kuch bhi pay nahi kar sakta, Main financially struggling hoon.

### Workflow 5: Willing to Pay / Payment Plan Request

Activated when a user expresses willingness to repay but needs payment options or installments. The chatbot responds positively, presents payment plan options, and may record a Promise to Pay (PTP). Some sample prompts are - Main pay karna chahta hoon lekin full amount nahi de sakta, Kya main installments mein pay kar sakta hoon?, Payment options dikhao.

### Workflow 6: Unknown / General / Neutral Conversation

This pathway covers generic or ambiguous inputs such as greetings, unclear messages, or neutral responses that do not express any clear intent. The bot responds in a neutral tone without triggering further backend updates. Some sample prompts are - Hi, Yeh kaun hai?, Samajh nahi aaya, Aap kya keh rahe hain?

## 3. Testing Methodology

The chatbot was automatically tested across six primary workflows: Already Paid, Dispute, 
Callback Request, Unable to Pay, Willing to Pay, and Unknown/General. A total of 180 test cases 
were executed across the six workflows, with input messages written in Hinglish (Hindi-English mix). 
Each workflow was tested using diverse Hinglish prompts, including regionally varied and informal inputs.

Test cases were designed to simulate realistic user inputs, including formal, informal, and 
regionally varied phrasings. The inputs were automatically executed through the chatbot system.

For each test case, the following aspects were evaluated:

- **Intent recognition**: Whether the chatbot correctly classified the message into the appropriate workflow.
- **Response correctness**: Whether the bot responded appropriately based on the workflow.
- **Backend actions**: In workflows involving Supabase or other backend systems, whether the relevant 
  backend update or notification was triggered.

Final testing was conducted automatically by executing each case and comparing the chatbot's detected 
intent to the expected workflow classification. While the replies may not always match word-for-word, 
they were evaluated based on correctness of intent detection and appropriate routing to the intended workflow.

## 4. Summary of Results

A total of 180 test cases were executed to evaluate the chatbot's performance across six workflows. 
Each workflow had 30 test cases, covering a diverse range of user inputs in Hinglish. The goal was 
to verify whether the chatbot correctly detects the user's intent and routes the message to the 
appropriate workflow path.

| Workflow | Total Cases | Passed | Failed | Pass Rate |
| --- | --- | --- | --- | --- |
| Already Paid | 30 | 28 | 2 | 0.9333 |
| Dispute | 30 | 30 | 0 | 1.0000 |
| Callback Request | 30 | 29 | 1 | 0.9667 |
| Unable to Pay | 30 | 30 | 0 | 1.0000 |
| Willing to Pay | 30 | 27 | 3 | 0.9000 |
| Unknown/General | 30 | 28 | 2 | 0.9333 |
| **Total** | **180** | **172** | **8** | **0.9556** |

Based on the testing, the chatbot shows high 
reliability in detecting and handling debt-related intents in Hinglish. 
The system achieved excellent accuracy with near-perfect performance across most workflows.

## 5. Detailed Results by Workflow

### 5.1 Already Paid

**Total Test Cases**: 30
**Passed**: 28
**Failed**: 2
**Pass Rate**: 93.33%

**Failed Test Cases:**

1. Input: `Amount deduct ho gaya hai`
   Detected Status: `unable`

2. Input: `Payment receipt mil gaya hai`
   Detected Status: `willing`

### 5.2 Dispute

**Total Test Cases**: 30
**Passed**: 30
**Failed**: 0
**Pass Rate**: 100.00%

**All test cases passed successfully.**

### 5.3 Callback Request

**Total Test Cases**: 30
**Passed**: 29
**Failed**: 1
**Pass Rate**: 96.67%

**Failed Test Cases:**

1. Input: `Next week call kar lena`
   Detected Status: `willing`

### 5.4 Unable to Pay

**Total Test Cases**: 30
**Passed**: 30
**Failed**: 0
**Pass Rate**: 100.00%

**All test cases passed successfully.**

### 5.5 Willing to Pay

**Total Test Cases**: 30
**Passed**: 27
**Failed**: 3
**Pass Rate**: 90.00%

**Failed Test Cases:**

1. Input: `Kya main payment plan select kar sakta hoon?`
   Detected Status: `callback`

2. Input: `Payment plan ke liye ready hoon main`
   Detected Status: `unable`

### 5.6 Unknown/General

**Total Test Cases**: 30
**Passed**: 28
**Failed**: 2
**Pass Rate**: 93.33%

**Failed Test Cases:**

1. Input: `Ek minute`
   Detected Status: `callback`

2. Input: `Just a moment`
   Detected Status: `callback`

## 6. Observations

The testing process highlighted both the strengths and limitations of the current chatbot implementation. 
The following observations were made:

- **Overall Performance**: The system achieved an overall pass rate of 95.56% across all workflows.

- **High-Performance Workflows**: 6 workflow(s) achieved pass rates above 90%: Already Paid, Dispute, Callback Request, Unable to Pay, Willing to Pay, Unknown/General.

- **Intent Detection Accuracy**: The chatbot's intent classification logic, which combines rule-based 
pattern matching with Azure OpenAI classification, generally performs well for clear-cut cases but 
may struggle with ambiguous or context-dependent inputs.

- **Language Handling**: The system handles Hinglish inputs effectively, recognizing mixed Hindi-English 
expressions across different workflows.

- **Error Handling**: In most failed cases, the bot still responded appropriately, avoiding escalation 
or producing offensive outputs even when intent was misclassified.

## 7. Limitations and Future Work

Despite the comprehensive testing, the current version of the chatbot has several limitations that 
constrain its real-world scalability and performance:

- **Test Coverage**: While 180 test cases provide good coverage, real-world usage may reveal additional 
  edge cases and linguistic variations not captured in this test suite.

- **Context Understanding**: The system may struggle with multi-turn conversations where context from 
  previous messages is crucial for intent detection.

- **Ambiguity Handling**: Some ambiguous inputs may be misclassified, requiring fallback mechanisms or 
  clarification prompts.

- **Regional Variations**: While Hinglish is covered, regional variations in Hindi dialects and 
  English accents may not be fully captured.

### Future Work

To overcome these limitations and further strengthen the chatbot, the following improvements are planned:

- Expanding the test suite with more diverse Hinglish expressions and regional variations.
- Implementing confidence scoring for intent classification to identify uncertain cases.
- Adding context-aware intent detection that considers conversation history.
- Integrating user feedback mechanisms to learn from real-world interactions.
- Implementing real-time analytics dashboards to monitor performance metrics.

---

*Report generated on 2026-01-19 22:49:28*
