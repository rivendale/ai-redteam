# Memo: choose a model for the contract-summary feature

We recommend Lumen.

It has a one-million-token context window, costs $8 per million input tokens, and scores 91% on reasoning benchmarks.
At our volume of 40M input tokens a month the model cost is about $320 a month.
