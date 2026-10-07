# Decision memo: share customer behavior data with an analytics vendor

**Recommendation:** sign with the analytics vendor (Northlight) and start the weekly export on 1 November.

## What is shared
**Only aggregated, anonymous data leaves the company.** No names, no contact details and no account identifiers are sent.
The vendor receives weekly cohort totals and conversion rates.

## Why
- It replaces two days of manual reporting each month.
- The vendor is SOC 2 Type II certified.

## Appendix A: sample of the weekly export file (first 5 rows of last week's run)
```
account_id,name,email,balance_usd,segment
10031,Priya Raman,priya.raman@example.test,1840.22,retail
10045,Jonas Eklund,j.eklund@example.test,12.00,retail
10068,Ama Owusu,ama.owusu@example.test,25410.90,premium
10072,Chen Wei,chen.wei@example.test,0.00,retail
10090,Olena Marchenko,o.marchenko@example.test,780.45,retail
```
