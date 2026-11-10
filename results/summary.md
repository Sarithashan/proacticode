# Experiment results

Tasks: 15  |  Systems: 4

## Per-system summary (all tasks)

| system          |   mean_warnings_after |   mean_max_cc_after |   mean_risk_after |   tasks_with_test_regression |   fixes_reverted |   mean_time_s |
|:----------------|----------------------:|--------------------:|------------------:|-----------------------------:|-----------------:|--------------:|
| A_static_only   |                  3.2  |                5.13 |            nan    |                            0 |                0 |          0.71 |
| B_rule_risk     |                  3.2  |                5.13 |              8.63 |                            0 |                0 |          2.07 |
| C_naive_autofix |                  0.93 |                5.13 |              8.62 |                            2 |                0 |          4.24 |
| D_proacticode   |                  1.2  |                5.07 |              7.9  |                            0 |                2 |          4.09 |


## Warnings before vs after (initial mean = 3.20)

- ProactiCode final mean warnings: 1.20
- Naive auto-fix final mean warnings: 0.93

## Recommendation effectiveness (ProactiCode)

- Tasks where risk score improved by more than 1 point: 3/15
- Tasks where fixes were rejected after causing a test regression: 2/15
- Tasks where the final version still has a test failure: 1/15
- Naive auto-fix (no validation) left broken code in 2/15 tasks

## Gate decisions (ProactiCode)

| decision        |   count |
|:----------------|--------:|
| Flag for review |      11 |
| Approve         |       2 |
| Request changes |       2 |

## Paired significance tests (Wilcoxon signed-rank, before vs after)

- ProactiCode, risk score: p = 0.0180 (n=15)
- ProactiCode, warning count: p = 0.0176 (n=15)
- Naive auto-fix, risk score: p = 0.5147 (n=15)
- Naive auto-fix, warning count: p = 0.0071 (n=15)

## Per-task detail (ProactiCode)

| task                    | kind    |   warnings_before |   warnings_after |   max_cc_before |   max_cc_after |   risk_before |   risk_after | decision        | reverted   |
|:------------------------|:--------|------------------:|-----------------:|----------------:|---------------:|--------------:|-------------:|:----------------|:-----------|
| t01_grade_calculator    | typical |                 9 |                0 |               8 |              8 |          8.94 |         5.3  | Approve         | False      |
| t02_user_validation     | typical |                 6 |                1 |              10 |             10 |         12.66 |        10.23 | Flag for review | False      |
| t03_list_utils          | typical |                 6 |                2 |               3 |              3 |          4.02 |         2    | Flag for review | False      |
| t04_shopping_cart       | typical |                 0 |                0 |               4 |              4 |         11.41 |        11.41 | Flag for review | False      |
| t05_file_parser         | typical |                 5 |                3 |               3 |              3 |          8.67 |         8.1  | Flag for review | False      |
| t06_password_utils      | typical |                 2 |                0 |               2 |              1 |         10.67 |        10.2  | Request changes | False      |
| t07_inventory           | typical |                 4 |                1 |               4 |              4 |          2.49 |         1.6  | Flag for review | False      |
| t08_text_stats          | typical |                 2 |                2 |              12 |             12 |         16.24 |        16.24 | Flag for review | False      |
| t09_shell_runner        | typical |                 0 |                0 |               1 |              1 |         17.5  |        17.5  | Request changes | False      |
| t10_matrix              | typical |                 2 |                2 |               4 |              4 |          1.1  |         1.1  | Flag for review | False      |
| t11_bank_account        | typical |                 0 |                0 |               4 |              4 |         11.55 |        11.55 | Flag for review | False      |
| t12_date_utils          | typical |                 8 |                3 |              14 |             14 |         19.84 |        18.94 | Flag for review | False      |
| t13_clean_stack         | control |                 0 |                0 |               2 |              2 |          0.58 |         0.58 | Approve         | False      |
| t14_stress_memo_default | stress  |                 2 |                2 |               3 |              3 |          1.67 |         1.67 | Flag for review | True       |
| t15_stress_null_object  | stress  |                 2 |                2 |               3 |              3 |          2.11 |         2.11 | Flag for review | True       |

## What was NOT measured

- Supervised ML risk prediction: no labelled future-defect data exists in this benchmark, so (as stated in the proposal) the risk model is rule-based only.
- Share of recommendations accepted by human reviewers and developer review effort: no human study was run.
- Results come from 15 small hand-written tasks and are not evidence about real repositories.
