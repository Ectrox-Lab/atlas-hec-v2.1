# E1 Audit Failure Cases

Generated: 2026-03-13T01:45:17.848875

Total failures: 24 / 120

## Failure Breakdown

| Test ID | Task Type | Selected | Expected | Rollback Success |
|---------|-----------|----------|----------|------------------|
| test_008 | documentation | general_coder | general_coder | True |
| test_012 | performance_optimization | sre | performance_engineer | True |
| test_014 | code_review | general_coder | general_coder | False |
| test_020 | code_review | general_coder | general_coder | True |
| test_021 | code_review | general_coder | security_expert | True |
| test_025 | documentation | general_coder | general_coder | False |
| test_031 | code_review | general_coder | general_coder | True |
| test_036 | documentation | general_coder | general_coder | True |
| test_044 | bug_fix | general_coder | domain_expert | True |
| test_049 | code_review | general_coder | general_coder | True |
| test_063 | bug_fix | general_coder | domain_expert | True |
| test_064 | code_review | general_coder | general_coder | True |
| test_069 | code_review | general_coder | general_coder | True |
| test_071 | code_review | general_coder | general_coder | True |
| test_073 | code_review | general_coder | general_coder | True |
| test_074 | code_review | general_coder | general_coder | True |
| test_076 | bug_fix | general_coder | domain_expert | True |
| test_080 | performance_optimization | sre | sre | True |
| test_086 | bug_fix | general_coder | domain_expert | True |
| test_095 | code_review | general_coder | general_coder | True |
| test_096 | code_review | general_coder | general_coder | True |
| test_107 | documentation | general_coder | general_coder | True |
| test_112 | code_review | general_coder | general_coder | True |
| test_113 | performance_optimization | sre | sre | True |

## Root Cause Analysis

1. **Wrong specialist selected**: 6 cases
   - Executive made incorrect delegation decision

2. **Correct selection but audit flagged**: 18 cases
   - Selection logic differs from audit criteria

## Rollback Performance

- Rollbacks triggered: 24
- Rollback successes: 22
- Rollback rate: 91.7%
