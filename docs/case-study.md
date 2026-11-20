# Case study: Churn Early Warning

## The question

A retention team can contact a limited number of customers each month. Who should be on the list, and how much does a churn model add over a rule or a checklist the team could write itself?

## Data

IBM Telco customer churn sample (Apache 2.0). This is sample data, not a real company's results.

- 7,043 customers, 1,869 of whom left (27%).
- For each customer: contract, months as a customer, phone and internet services, add-ons such as tech support, billing method, monthly and total charges, and four personal fields (gender, senior citizen flag, partner, dependents).
- One snapshot. Who left and what they had were recorded at the same point, with no history over time.
- 11 customers in their first month have a blank total charges field. I set them to 0, because nothing had been billed yet. None of them left.

## Approach

1. Rank every customer four ways:
   - **Rule:** month-to-month contracts first, newest customers first within them. Anyone can build this in a CRM.
   - **Points checklist:** one point each for a month-to-month contract, 12 months or less as a customer, paying by electronic check, fiber optic internet and no tech support. These are well-known flags for this sample, so the checklist has some hindsight.
   - **Logistic regression** on all fields.
   - **Gradient boosting** on all fields.
2. Score the models with 5-fold cross validation, so each customer's score comes from a model that never saw them. See [decision 0001](decisions/0001-cross-validation-not-a-time-split.md).
3. Turn each ranking into contact lists of 1% to 50% of customers. Measure the share of all leavers the list reaches, the share of the list that left, and the share of leavers' monthly charges the list covers.
4. Extra tests: the model without personal fields, ranking by revenue at risk, a profile of leavers the list misses, and predicted against actual leavers.

## Findings

### 1. List size matters more than the method (confirmed)

| List size | Rule | Checklist | Logistic regression | Gradient boosting |
|---|---|---|---|---|
| 5% (352) | 11% | 15% | 15% | 16% |
| 10% (704) | 23% | 27% | 29% | 29% |
| 20% (1,409) | 42% | 49% | 51% | 50% |
| 30% (2,113) | 58% | 65% | 67% | 65% |

Share of all leavers reached. Doubling the list from 10% to 20% adds 22 points for the model. Moving from the checklist to the model at 20% adds 2. How many customers the team can contact is the bigger decision.

### 2. A 5 flag checklist gets close to the model (confirmed, with a caveat)

At 20%, the checklist reaches 49% of leavers and 65% of its list left. The model reaches 51% and 68%. The two lists share 82% of their customers. The simple contract rule is clearly behind (42% and 55%). Caveat: the five flags are well known for this sample. A team without the data would have to guess them, and might guess worse.

### 3. The more complex model adds nothing (confirmed)

Gradient boosting ranks leavers no better than logistic regression (ranking score 0.842 against 0.845, with fold to fold spreads of 0.03 to 0.04). Logistic regression is easier to explain to a retention team, so it is the one used for the rest of the page.

### 4. Personal fields add nothing, so leave them out (confirmed)

Without gender, the senior citizen flag, partner and dependents, the model ranks the same (0.845) and reaches the same 51% of leavers at 20%. See [decision 0002](decisions/0002-leave-out-personal-fields.md).

### 5. Ranking by revenue at risk is a tradeoff (confirmed)

| List size | Leavers on the list, by risk → by revenue at risk | Revenue covered, by risk → by revenue at risk | Same customers |
|---|---|---|---|
| 5% | 15% → 14% | 18% → 18% | 58% |
| 10% | 29% → 27% | 32% → 34% | 71% |
| 20% | 51% → 49% | 55% → 58% | 86% |
| 30% | 67% → 63% | 71% → 73% | 85% |

Ranking by chance of leaving times monthly charges swaps in more valuable customers. It covers a little more revenue and reaches a few fewer leavers. Which is right depends on the team's goal. See [decision 0003](decisions/0003-rank-by-risk-by-default.md).

### 6. The list misses longer-term customers (confirmed)

At 20%, the list reaches 952 leavers and misses 917. The leavers it reaches have a median of 5 months as customers, and all are on month-to-month contracts. The ones it misses have a median of 22 months, and 77% are on month-to-month contracts. Nothing in this data separates them from the long-term customers who stay. Usage, complaints or support contacts might (hypothesis).

### 7. The model's numbers can be used to plan (confirmed)

The model expected 1,871 leavers in total, and 1,869 left. Across ten groups from lowest to highest risk, predicted and actual shares stay close, with the largest gap 5 points in one group. A team can use the predicted numbers to size its effort.

## What I learned as a PM

- Start from the team's capacity, not the model score. "Who are the top 1,409 customers to call?" is a question a retention lead can act on.
- Check how far a simple checklist gets before building a model. Here it got most of the way. A model still adds a little, plus numbers that can be trusted for planning.
- A model that ranks well is not the same as a team that saves customers. Nothing here shows whether a call keeps anyone. That needs a test with a group that is not contacted.
- Leaving out personal fields cost nothing here. Checking that is cheap, and it removes a fairness question before anyone asks it.

## Limits

- Sample data, one snapshot. A real early warning test trains on one period and checks who leaves in the next. This data can't do that, so the results are likely better than a real deployment would see.
- The checklist flags were chosen with knowledge of this sample.
- Monthly charges stand in for customer value. The dataset gives no currency, margin or lifetime value.
- No data on what contacting customers achieves.

## What I would do next

1. Repeat on data with history over time: score customers in one month, check who leaves in the next.
2. Add usage and support signals to find the longer-term leavers the list misses.
3. Design a holdout test: contact half of the list, leave half alone, and measure the difference. That gives the save rate, which turns this into a business case: [save rate] × [value of a saved customer] against [cost per contact].

## My role

I defined the question, chose the methods and the list based view, and wrote the findings. Claude (Anthropic) wrote and ran the code with me.
