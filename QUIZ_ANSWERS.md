# Microburbs Quiz - Submission Answers

## Which task did you attempt?
**Option 1: Real estate metric**

---

## Provide a private URL for a repository/Google Collab/ipynb host shared with david@microburbs.com.au
**Repository URL:** https://github.com/chunghaw/microburbs_quiz

*(Repository will be shared privately with david@microburbs.com.au)*

---

## Paste the code here. Don't worry about formatting.

### Main Analysis Script (create_analysis.py):
```python
# See create_analysis.py in repository
# Full code available at: https://github.com/chunghaw/microburbs_quiz/blob/main/create_analysis.py
```

Key components:
- Data loading and cleaning (transactions.parquet, gnaf_prop.parquet)
- Momentum score calculation algorithm
- Visualization generation (matplotlib/seaborn)
- CSV export functionality

---

## Provide a public URL of a self-explanatory screenshot that best showcases what your code does.
**Screenshot URL:** Will be uploaded to GitHub repository as `market_momentum_overview.png`

Public URL: https://raw.githubusercontent.com/chunghaw/microburbs_quiz/main/market_momentum_overview.png

---

## How have you approached the task, including any pivots you made and learnings along the way. (40 words max.)

Started creating a composite metric balancing price growth, market activity, and value. Pivoted from purely quantitative scoring to include value assessment preventing overvaluation alerts. Changed technical terms to emoji-based categories for accessibility. Learned data quality is critical; spent significant time filtering invalid transactions.

---

## What does your final code do? (40 words max.)

Calculates Market Momentum Score (0-100) for suburbs combining price growth (40%), market activity (30%), and value indicators (30%). Categorizes suburbs as Hot, Growing, Stable, Cooling, or Cold. Generates visualizations and exports ranked CSV files identifying high-potential investment opportunities for property investors.

---

## How should investors interpret your results? (40 words max.)

Higher scores (80-100) indicate hot markets with strong growth requiring quick action. Mid-range scores (60-79) offer balanced opportunities. Lower scores suggest caution. Think of it like weather: hot means high activity/competition, cold means slow market. Use alongside traditional due diligence, not as sole investment basis.

---

## What were your findings? How accurate is it? (40 words max.)

North Willoughby leads with 75.0 score and 49.3% six-month growth. Northbridge shows stability at premium price point ($5.5M). Accuracy is high for data-rich suburbs with 100+ transactions. Limited by minimum transaction threshold (3), requiring careful validation for smaller markets. Reliable for established areas.

---

## What tagline would you use to promote this? (20 words max.)

"Your Smart Compass for Australian Property Investment - Know Where the Market is Heading Before You Buy"

---

## What bugs does the code currently have? How could you fix them given more time? (40 words max.)

Limited suburbs due to strict minimum transaction threshold. Property type not differentiated (houses vs units). No seasonal adjustments. Fixes: lower threshold to 2 with confidence intervals, add property segmentation, integrate rental yield data, include infrastructure impact analysis, and seasonal normalization algorithms.

---

## What assumptions did you make? (40 words max.)

Assumed six-month windows capture meaningful trends. Minimum three transactions per suburb ensures reliability. Price per square meter indicates value when available. Past growth predicts future momentum. Transaction volume reflects market health. Median prices are more robust than means for outlier resistance. All sales are arms-length transactions.

---

## What functionality/analysis would you add if given more time? (40 words max.)

Add days-on-market trends, auction clearance rates, rental yield analysis, school catchment scoring. Build interactive web dashboard with email alerts for score changes. Implement machine learning price forecasts, infrastructure impact modeling, risk assessment algorithms, suburb comparison tools, and ROI calculators with mortgage scenario planning.

---

## What challenges would you have scaling this for the whole country? What modifications would you make? (40 words max.)

Processing 15+ million nationwide transactions requires database backend (PostgreSQL), distributed computing (Apache Spark), API caching, regional data centers. Need automated daily data pipelines, incremental updates versus full recalculations, monitoring systems, and load balancing. Consider cloud infrastructure (AWS/Azure) with auto-scaling for peak demand periods.

---

## What did you think of the task? (40 words max.)

Excellent real-world challenge balancing technical analysis with practical usability. Appreciated focus on investor needs and accessibility. Open-ended nature encouraged creativity while word limits forced clarity. Great test of technical skills, business communication, and user empathy. Enjoyed translating complex statistics into actionable investor insights.

---

## Quilgo Test ID
*This question is filled automatically ✋ DO NOT EDIT OR REMOVE*
⬇️ Skip this question ⬇️                                                                                                                              DO NOT REMOVE OR EDIT! ### JANGAN HAPUS ATAU EDIT! ### ¡NO QUITAR NI EDITAR! ### hataen ya sampaadit na karen! ### @#@#@pM2yM6NXPtsvsasC

