# NL2SQL System - Test Results and Evaluation

**Generated:** 2026-01-15 12:01:58

---

## Executive Summary

- **Total Test Queries:** 15
- **Strategies Tested:** 2 (Schema-First, Chain-of-Thought)
- **Total Test Runs:** 30

## Performance Metrics by Strategy

### Strategy 1 (Schema-First)

| Metric | Value |
|--------|-------|
| Total Queries | 15 |
| Successful Executions | 0 |
| Valid Queries | 0 |
| **Success Rate** | **0.0%** |
| Validation Rate | 0.0% |
| Avg Generation Time | 0 ms |
| Avg Execution Time | 0 ms |
| Min Generation Time | 0 ms |
| Max Generation Time | 0 ms |

#### Performance by Difficulty

| Difficulty | Total | Successful | Success Rate |
|------------|-------|------------|-------------|
| Easy | 5 | 0 | 0.0% |
| Medium | 6 | 0 | 0.0% |
| Difficult | 4 | 0 | 0.0% |

### Strategy 2 (Chain-of-Thought)

| Metric | Value |
|--------|-------|
| Total Queries | 15 |
| Successful Executions | 0 |
| Valid Queries | 0 |
| **Success Rate** | **0.0%** |
| Validation Rate | 0.0% |
| Avg Generation Time | 0 ms |
| Avg Execution Time | 0 ms |
| Min Generation Time | 0 ms |
| Max Generation Time | 0 ms |

#### Performance by Difficulty

| Difficulty | Total | Successful | Success Rate |
|------------|-------|------------|-------------|
| Easy | 5 | 0 | 0.0% |
| Medium | 6 | 0 | 0.0% |
| Difficult | 4 | 0 | 0.0% |

## Detailed Test Results

### Strategy 1: Schema-First

#### Test 1: ✗ FAIL

**Question:** Show all customers

**Difficulty:** easy

**Generated SQL:**
```sql
N/A
```

- **Error:** Failed to generate SQL after 3 attempts: Gemini API quota exceeded. This shouldn't happen with rate limiting enabled. Error: 429 You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate-limits. To monitor your current usage, head to: https://ai.dev/rate-limit. 
* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 0, model: gemini-2.0-flash-exp
* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 0, model: gemini-2.0-flash-exp
* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_input_token_count, limit: 0, model: gemini-2.0-flash-exp
Please retry in 5.665517982s. [links {
  description: "Learn more about Gemini API quotas"
  url: "https://ai.google.dev/gemini-api/docs/rate-limits"
}
, violations {
  quota_metric: "generativelanguage.googleapis.com/generate_content_free_tier_requests"
  quota_id: "GenerateRequestsPerDayPerProjectPerModel-FreeTier"
  quota_dimensions {
    key: "model"
    value: "gemini-2.0-flash-exp"
  }
  quota_dimensions {
    key: "location"
    value: "global"
  }
}
violations {
  quota_metric: "generativelanguage.googleapis.com/generate_content_free_tier_requests"
  quota_id: "GenerateRequestsPerMinutePerProjectPerModel-FreeTier"
  quota_dimensions {
    key: "model"
    value: "gemini-2.0-flash-exp"
  }
  quota_dimensions {
    key: "location"
    value: "global"
  }
}
violations {
  quota_metric: "generativelanguage.googleapis.com/generate_content_free_tier_input_token_count"
  quota_id: "GenerateContentInputTokensPerModelPerMinute-FreeTier"
  quota_dimensions {
    key: "model"
    value: "gemini-2.0-flash-exp"
  }
  quota_dimensions {
    key: "location"
    value: "global"
  }
}
, retry_delay {
  seconds: 5
}
]

---

#### Test 2: ✗ FAIL

**Question:** List all products in the Electronics category

**Difficulty:** easy

**Generated SQL:**
```sql
N/A
```

- **Error:** Failed to generate SQL after 3 attempts: Gemini API quota exceeded. This shouldn't happen with rate limiting enabled. Error: 429 You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate-limits. To monitor your current usage, head to: https://ai.dev/rate-limit. 
* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_input_token_count, limit: 0, model: gemini-2.0-flash-exp
* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 0, model: gemini-2.0-flash-exp
* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 0, model: gemini-2.0-flash-exp
Please retry in 4.889135258s. [links {
  description: "Learn more about Gemini API quotas"
  url: "https://ai.google.dev/gemini-api/docs/rate-limits"
}
, violations {
  quota_metric: "generativelanguage.googleapis.com/generate_content_free_tier_input_token_count"
  quota_id: "GenerateContentInputTokensPerModelPerMinute-FreeTier"
  quota_dimensions {
    key: "model"
    value: "gemini-2.0-flash-exp"
  }
  quota_dimensions {
    key: "location"
    value: "global"
  }
}
violations {
  quota_metric: "generativelanguage.googleapis.com/generate_content_free_tier_requests"
  quota_id: "GenerateRequestsPerMinutePerProjectPerModel-FreeTier"
  quota_dimensions {
    key: "model"
    value: "gemini-2.0-flash-exp"
  }
  quota_dimensions {
    key: "location"
    value: "global"
  }
}
violations {
  quota_metric: "generativelanguage.googleapis.com/generate_content_free_tier_requests"
  quota_id: "GenerateRequestsPerDayPerProjectPerModel-FreeTier"
  quota_dimensions {
    key: "model"
    value: "gemini-2.0-flash-exp"
  }
  quota_dimensions {
    key: "location"
    value: "global"
  }
}
, retry_delay {
  seconds: 4
}
]

---

#### Test 3: ✗ FAIL

**Question:** How many orders have been placed?

**Difficulty:** easy

**Generated SQL:**
```sql
N/A
```

- **Error:** Failed to generate SQL after 3 attempts: Gemini API quota exceeded. This shouldn't happen with rate limiting enabled. Error: 429 You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate-limits. To monitor your current usage, head to: https://ai.dev/rate-limit. 
* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_input_token_count, limit: 0, model: gemini-2.0-flash-exp
* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 0, model: gemini-2.0-flash-exp
* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 0, model: gemini-2.0-flash-exp
Please retry in 4.273570919s. [links {
  description: "Learn more about Gemini API quotas"
  url: "https://ai.google.dev/gemini-api/docs/rate-limits"
}
, violations {
  quota_metric: "generativelanguage.googleapis.com/generate_content_free_tier_input_token_count"
  quota_id: "GenerateContentInputTokensPerModelPerMinute-FreeTier"
  quota_dimensions {
    key: "model"
    value: "gemini-2.0-flash-exp"
  }
  quota_dimensions {
    key: "location"
    value: "global"
  }
}
violations {
  quota_metric: "generativelanguage.googleapis.com/generate_content_free_tier_requests"
  quota_id: "GenerateRequestsPerMinutePerProjectPerModel-FreeTier"
  quota_dimensions {
    key: "model"
    value: "gemini-2.0-flash-exp"
  }
  quota_dimensions {
    key: "location"
    value: "global"
  }
}
violations {
  quota_metric: "generativelanguage.googleapis.com/generate_content_free_tier_requests"
  quota_id: "GenerateRequestsPerDayPerProjectPerModel-FreeTier"
  quota_dimensions {
    key: "model"
    value: "gemini-2.0-flash-exp"
  }
  quota_dimensions {
    key: "location"
    value: "global"
  }
}
, retry_delay {
  seconds: 4
}
]

---

#### Test 4: ✗ FAIL

**Question:** What is the total revenue from all payments?

**Difficulty:** easy

**Generated SQL:**
```sql
N/A
```

- **Error:** Failed to generate SQL after 3 attempts: Rate limit exceeded. Please wait 52 seconds. Limits: 10 requests/min, 1500 requests/day

---

#### Test 5: ✗ FAIL

**Question:** Show customers from USA

**Difficulty:** easy

**Generated SQL:**
```sql
N/A
```

- **Error:** Failed to generate SQL after 3 attempts: Rate limit exceeded. Please wait 51 seconds. Limits: 10 requests/min, 1500 requests/day

---

#### Test 6: ✗ FAIL

**Question:** List the top 5 most expensive products

**Difficulty:** medium

**Generated SQL:**
```sql
N/A
```

- **Error:** Failed to generate SQL after 3 attempts: Rate limit exceeded. Please wait 51 seconds. Limits: 10 requests/min, 1500 requests/day

---

#### Test 7: ✗ FAIL

**Question:** Show total sales by category

**Difficulty:** medium

**Generated SQL:**
```sql
N/A
```

- **Error:** Failed to generate SQL after 3 attempts: Rate limit exceeded. Please wait 51 seconds. Limits: 10 requests/min, 1500 requests/day

---

#### Test 8: ✗ FAIL

**Question:** Which customers have placed more than one order?

**Difficulty:** medium

**Generated SQL:**
```sql
N/A
```

- **Error:** Failed to generate SQL after 3 attempts: Rate limit exceeded. Please wait 51 seconds. Limits: 10 requests/min, 1500 requests/day

---

#### Test 9: ✗ FAIL

**Question:** What is the average order value?

**Difficulty:** medium

**Generated SQL:**
```sql
N/A
```

- **Error:** Failed to generate SQL after 3 attempts: Rate limit exceeded. Please wait 51 seconds. Limits: 10 requests/min, 1500 requests/day

---

#### Test 10: ✗ FAIL

**Question:** Show orders with their customer names and total amounts

**Difficulty:** medium

**Generated SQL:**
```sql
N/A
```

- **Error:** Failed to generate SQL after 3 attempts: Rate limit exceeded. Please wait 51 seconds. Limits: 10 requests/min, 1500 requests/day

---

#### Test 11: ✗ FAIL

**Question:** Find the most popular product by quantity sold

**Difficulty:** difficult

**Generated SQL:**
```sql
N/A
```

- **Error:** Failed to generate SQL after 3 attempts: Rate limit exceeded. Please wait 51 seconds. Limits: 10 requests/min, 1500 requests/day

---

#### Test 12: ✗ FAIL

**Question:** Show monthly revenue for 2024

**Difficulty:** difficult

**Generated SQL:**
```sql
N/A
```

- **Error:** Failed to generate SQL after 3 attempts: Rate limit exceeded. Please wait 51 seconds. Limits: 10 requests/min, 1500 requests/day

---

#### Test 13: ✗ FAIL

**Question:** Which payment method is most commonly used?

**Difficulty:** medium

**Generated SQL:**
```sql
N/A
```

- **Error:** Failed to generate SQL after 3 attempts: Rate limit exceeded. Please wait 51 seconds. Limits: 10 requests/min, 1500 requests/day

---

#### Test 14: ✗ FAIL

**Question:** List customers who have never placed an order

**Difficulty:** difficult

**Generated SQL:**
```sql
N/A
```

- **Error:** Failed to generate SQL after 3 attempts: Rate limit exceeded. Please wait 51 seconds. Limits: 10 requests/min, 1500 requests/day

---

#### Test 15: ✗ FAIL

**Question:** Show the top 3 customers by total spending

**Difficulty:** difficult

**Generated SQL:**
```sql
N/A
```

- **Error:** Failed to generate SQL after 3 attempts: Rate limit exceeded. Please wait 51 seconds. Limits: 10 requests/min, 1500 requests/day

---

### Strategy 2: Chain-of-Thought

#### Test 1: ✗ FAIL

**Question:** Show all customers

**Difficulty:** easy

**Generated SQL:**
```sql
N/A
```

- **Error:** Failed to generate SQL after 3 attempts: Rate limit exceeded. Please wait 51 seconds. Limits: 10 requests/min, 1500 requests/day

---

#### Test 2: ✗ FAIL

**Question:** List all products in the Electronics category

**Difficulty:** easy

**Generated SQL:**
```sql
N/A
```

- **Error:** Failed to generate SQL after 3 attempts: Rate limit exceeded. Please wait 51 seconds. Limits: 10 requests/min, 1500 requests/day

---

#### Test 3: ✗ FAIL

**Question:** How many orders have been placed?

**Difficulty:** easy

**Generated SQL:**
```sql
N/A
```

- **Error:** Failed to generate SQL after 3 attempts: Rate limit exceeded. Please wait 51 seconds. Limits: 10 requests/min, 1500 requests/day

---

#### Test 4: ✗ FAIL

**Question:** What is the total revenue from all payments?

**Difficulty:** easy

**Generated SQL:**
```sql
N/A
```

- **Error:** Failed to generate SQL after 3 attempts: Rate limit exceeded. Please wait 51 seconds. Limits: 10 requests/min, 1500 requests/day

---

#### Test 5: ✗ FAIL

**Question:** Show customers from USA

**Difficulty:** easy

**Generated SQL:**
```sql
N/A
```

- **Error:** Failed to generate SQL after 3 attempts: Rate limit exceeded. Please wait 51 seconds. Limits: 10 requests/min, 1500 requests/day

---

#### Test 6: ✗ FAIL

**Question:** List the top 5 most expensive products

**Difficulty:** medium

**Generated SQL:**
```sql
N/A
```

- **Error:** Failed to generate SQL after 3 attempts: Rate limit exceeded. Please wait 51 seconds. Limits: 10 requests/min, 1500 requests/day

---

#### Test 7: ✗ FAIL

**Question:** Show total sales by category

**Difficulty:** medium

**Generated SQL:**
```sql
N/A
```

- **Error:** Failed to generate SQL after 3 attempts: Rate limit exceeded. Please wait 51 seconds. Limits: 10 requests/min, 1500 requests/day

---

#### Test 8: ✗ FAIL

**Question:** Which customers have placed more than one order?

**Difficulty:** medium

**Generated SQL:**
```sql
N/A
```

- **Error:** Failed to generate SQL after 3 attempts: Rate limit exceeded. Please wait 51 seconds. Limits: 10 requests/min, 1500 requests/day

---

#### Test 9: ✗ FAIL

**Question:** What is the average order value?

**Difficulty:** medium

**Generated SQL:**
```sql
N/A
```

- **Error:** Failed to generate SQL after 3 attempts: Rate limit exceeded. Please wait 51 seconds. Limits: 10 requests/min, 1500 requests/day

---

#### Test 10: ✗ FAIL

**Question:** Show orders with their customer names and total amounts

**Difficulty:** medium

**Generated SQL:**
```sql
N/A
```

- **Error:** Failed to generate SQL after 3 attempts: Rate limit exceeded. Please wait 51 seconds. Limits: 10 requests/min, 1500 requests/day

---

#### Test 11: ✗ FAIL

**Question:** Find the most popular product by quantity sold

**Difficulty:** difficult

**Generated SQL:**
```sql
N/A
```

- **Error:** Failed to generate SQL after 3 attempts: Rate limit exceeded. Please wait 51 seconds. Limits: 10 requests/min, 1500 requests/day

---

#### Test 12: ✗ FAIL

**Question:** Show monthly revenue for 2024

**Difficulty:** difficult

**Generated SQL:**
```sql
N/A
```

- **Error:** Failed to generate SQL after 3 attempts: Rate limit exceeded. Please wait 51 seconds. Limits: 10 requests/min, 1500 requests/day

---

#### Test 13: ✗ FAIL

**Question:** Which payment method is most commonly used?

**Difficulty:** medium

**Generated SQL:**
```sql
N/A
```

- **Error:** Failed to generate SQL after 3 attempts: Rate limit exceeded. Please wait 51 seconds. Limits: 10 requests/min, 1500 requests/day

---

#### Test 14: ✗ FAIL

**Question:** List customers who have never placed an order

**Difficulty:** difficult

**Generated SQL:**
```sql
N/A
```

- **Error:** Failed to generate SQL after 3 attempts: Rate limit exceeded. Please wait 51 seconds. Limits: 10 requests/min, 1500 requests/day

---

#### Test 15: ✗ FAIL

**Question:** Show the top 3 customers by total spending

**Difficulty:** difficult

**Generated SQL:**
```sql
N/A
```

- **Error:** Failed to generate SQL after 3 attempts: Rate limit exceeded. Please wait 51 seconds. Limits: 10 requests/min, 1500 requests/day

---

## Strategy Comparison Examples

### Show all customers

**Difficulty:** easy

#### Strategy 1: Schema-First

#### Strategy 2: Chain-of-Thought

---

### Show total sales by category

**Difficulty:** medium

#### Strategy 1: Schema-First

#### Strategy 2: Chain-of-Thought

---

### Find the most popular product by quantity sold

**Difficulty:** difficult

#### Strategy 1: Schema-First

#### Strategy 2: Chain-of-Thought

---

### List customers who have never placed an order

**Difficulty:** difficult

#### Strategy 1: Schema-First

#### Strategy 2: Chain-of-Thought

---

