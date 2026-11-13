# review-insights-llm
LLM-powered analysis of customer reviews: sentiment, issue category and summary extraction with Gemini, evaluated against real ratings.
### Category evaluation (LLM vs. manual labels)

| Reference labels | Reviews | Accuracy | Macro F1 |
|---|---|---|---|
| Original manual labels | 99 | 77.8% | 0.663 |
| Revised labels (documented guidelines) | 100 | 87.0% | 0.779 |

After the first evaluation, I reviewed all 22 disagreements between the model and my labels.
Some were labeling mistakes on my side (e.g. reviews that only mentioned the delivery date were labeled as "delay"),
and others came from category boundaries that were not clearly defined.
I wrote explicit labeling guidelines and revised 10 labels based on them.

All 10 revisions moved toward the model's answer, so I report both numbers for transparency.
The original labels are kept in `data/processed/manual_labels_original.xlsx`.

### Insights

- **Most complaints are about operations, not the product itself.** Wrong or incomplete orders (29%) and undelivered orders (28%) account for 57% of negative reviews; adding delays (12%), delivery and fulfillment issues make up about 7 in 10 negative reviews. Product quality and damage together account for only 14%.
- **Not receiving the order is the most damaging experience.** Reviews classified as "not delivered" have an average rating of 1.2 stars, versus 2.4 for delays.
- *Caveat:* categories were assigned by the LLM (87% agreement with manual labels). "Damaged product" has low recall (0.25), so its share is likely underestimated.

Percentages are weighted to reflect the real distribution of ratings in the dataset, since the sample is balanced (100 reviews per rating).