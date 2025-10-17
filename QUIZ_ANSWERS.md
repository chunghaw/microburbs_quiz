# Microburbs Quiz - Submission Answers

## Which task did you attempt?
**Option 1: Real estate metric**

---

## Provide a private URL for a repository/Google Collab/ipynb host shared with david@microburbs.com.au
**Repository URL:** https://github.com/chunghaw/microburbs_quiz

*(Repository will be shared privately with david@microburbs.com.au)*

---

## Paste the code here. Don't worry about formatting.

### Main Analysis Script (final_analysis.py):
```python
# See final_analysis.py in repository
# Full code available at: https://github.com/chunghaw/microburbs_quiz/blob/main/final_analysis.py
```

Key components:
- Data loading: transactions, GNAF properties, roads (4 data sources)
- 12-month time window calculation
- Road proximity analysis (accessibility scoring)
- Investment score formula: G(35%) + P(15%) + Y(25%) + A(15%) + L(10%)
- Rental yield estimation (Sydney benchmarks)
- Multi-chart visualization generation
- CSV export with investment signals

---

## Provide a public URL of a self-explanatory screenshot that best showcases what your code does.
**Screenshot URL:** https://raw.githubusercontent.com/chunghaw/microburbs_quiz/main/microburbs_final_with_interpretation.png

Shows: Investment scores with interpretation guide, component breakdowns, and clear buy/hold/avoid signals

---

## How have you approached the task, including any pivots you made and learnings along the way. (40 words max.)

Created comprehensive investment score combining five weighted factors: price growth (35%), affordability (15%), rental yield (25%), accessibility (15%), liquidity (10%). Changed from 6-month to 12-month window for better coverage. Implemented clear interpretation guide for non-technical investors.

---

## What does your final code do? (40 words max.)

Analyzes Sydney suburbs using weighted formula: Price Growth (35%), Affordability (15%), Rental Yield (25%), Accessibility (15%), Liquidity (10%). Generates investment scores (0-100) with clear buy/hold/avoid signals, detailed component breakdowns, and actionable recommendations for property investors.

---

## How should investors interpret your results? (40 words max.)

Scores above 60 indicate BUY opportunities with solid fundamentals. Scores 45-60 suggest HOLD for long-term accumulation. Below 45 requires caution. Each range has clear meaning and investment signal. Use alongside traditional due diligence, not as sole basis.

---

## What were your findings? How accurate is it? (40 words max.)

Roseville leads (71.5) with exceptional 337.5% twelve-month growth and strong liquidity. Five suburbs analyzed with 12-month data (51 transactions). Accuracy high for suburbs with 3+ sales. Reliable methodology combining multiple data sources including roads, prices, and transaction volumes.

---

## What tagline would you use to promote this? (20 words max.)

"Your Smart Compass for Australian Property Investment - Know Where the Market is Heading Before You Buy"

---

## What bugs does the code currently have? How could you fix them given more time? (40 words max.)

Rental yields are estimated (no actual data). Property types undifferentiated (houses/units). Limited to Sydney only. Fixes: integrate real rental APIs (Domain/REA), add property type segmentation, include school catchments, infrastructure projects, and expand to Melbourne/Brisbane datasets.

---

## What assumptions did you make? (40 words max.)

Twelve-month window captures meaningful trends. Minimum three transactions ensures statistical reliability. Rental yields estimated from Sydney benchmarks (3-6%). Proximity to major roads indicates accessibility. Past growth suggests future momentum. Median prices resist outliers. All transactions are arms-length sales.

---

## What functionality/analysis would you add if given more time? (40 words max.)

Real rental data integration (APIs), auction clearance rates, days-on-market analysis, school catchment quality scores. Interactive web dashboard with suburb comparison, email alerts, machine learning price forecasts, risk assessment models, ROI calculators with mortgage scenarios, and portfolio optimization tools.

---

## What challenges would you have scaling this for the whole country? What modifications would you make? (40 words max.)

Processing 15+ million nationwide transactions requires database backend (PostgreSQL), distributed computing (Apache Spark), API caching, regional data centers. Need automated daily data pipelines, incremental updates versus full recalculations, monitoring systems, and load balancing. Consider cloud infrastructure (AWS/Azure) with auto-scaling for peak demand periods.

---

## What did you think of the task? (40 words max.)

Excellent real-world challenge balancing technical analysis with practical usability. Appreciated focus on investor needs and accessibility. Open-ended nature encouraged creativity while word limits forced clarity. Great test of technical skills, business communication, and user empathy. Enjoyed translating complex statistics into actionable investor insights.


