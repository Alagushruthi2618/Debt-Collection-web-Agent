import json

# Load test results
with open('tests/test_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('=== WORKFLOW SUMMARY ===')
for workflow in data:
    if isinstance(data[workflow], dict) and 'total' in data[workflow]:
        passed = data[workflow]['passed']
        total = data[workflow]['total']
        pass_rate = (passed / total) * 100
        print(f'{workflow}: {passed}/{total} ({pass_rate:.1f}%)')

# Calculate overall totals
total_passed = sum(data[w]['passed'] for w in data if isinstance(data[w], dict) and 'passed' in data[w])
total_tests = sum(data[w]['total'] for w in data if isinstance(data[w], dict) and 'total' in data[w])
overall_pass_rate = (total_passed / total_tests) * 100

print(f'\n=== OVERALL ===')
print(f'Total: {total_passed}/{total_tests} ({overall_pass_rate:.1f}%)')
