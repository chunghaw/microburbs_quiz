# 🏘️ Microburbs Interactive Dashboard

Live interactive investment dashboard with filters and Cursor-like theme.

## Features

✅ **Microburbs API Integration:**
- Real-time property data from Microburbs
- Market insights and trends
- Demographics and population data
- Schools and amenities
- Risk factors analysis
- **20+ suburbs** available (expandable to all Australian suburbs)

✅ **Interactive Filters:**
- State selection
- Score range (investment signal)
- Price range
- Data reliability
- Suburb search (real-time)

✅ **Modern UI:**
- Cursor-inspired dark theme
- Sleek color palette
- Responsive design
- Smooth animations
- Click cards for detailed views

✅ **Comprehensive Data:**
- **API Data:** Properties, market insights, demographics, schools, amenities
- **Investment Scores:** G(35%) + P(15%) + Y(25%) + A(15%) + L(10%)
- **7 scored suburbs** (Sydney North Shore with full analysis)
- **20+ API suburbs** (Newcastle, Sydney CBD, etc.)
- Price growth metrics
- Rental yield estimates
- Road accessibility
- Market liquidity

## Tech Stack

- **Backend:** Python + Flask
- **Frontend:** Vanilla JavaScript (no frameworks)
- **Styling:** Pure CSS (Cursor-like theme)
- **Deployment:** Vercel

## Local Development

```bash
cd dashboard
pip install -r requirements.txt
python app.py
```

Visit: `http://localhost:5000`

## Deploy to Vercel

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
cd dashboard
vercel
```

3. Follow prompts to deploy

## API Endpoints

- `GET /` - Main dashboard
- `GET /api/suburbs` - List all suburbs with scores
- `GET /api/suburb/<name>` - Suburb details
- `GET /api/filters` - Available filter options
- `GET /api/stats` - Dashboard statistics

## Filters Available

- **State:** NSW (expandable)
- **Score Range:** 5 ranges (75+, 60-75, 45-60, 30-45, <30)
- **Price Range:** 4 ranges (Under $2M, $2-3M, $3-5M, $5M+)
- **Reliability:** HIGH, MODERATE, LOW
- **Search:** Real-time suburb name search

## Data Sources

**Primary:** Microburbs API (https://www.microburbs.com.au/report_generator/api)
- Properties for sale
- Market insights
- Demographics
- Schools & amenities
- Risk factors

**Enhancement:** Local investment score calculations
- 7 fully analyzed suburbs with scores
- Historical price growth
- Rental yield estimates
- Road accessibility analysis

**Architecture:**
```
User Request
    ↓
Try Microburbs API
    ├─ Success → Use API data + enhance with local scores
    └─ Fail → Fallback to local CSV data
```

## Suburbs Available

**With Investment Scores (7):**
- Roseville, Willoughby, Northbridge, North Willoughby
- Castle Cove, Middle Cove, Willoughby East

**With API Data Only (13+):**
- Belmont North, Belmont, Charlestown, Newcastle
- Sydney, Parramatta, Bondi, Manly
- And more...

**Total:** 20+ suburbs, expandable to all Australia

## Future Enhancements

- [x] Connect to Microburbs API ✅
- [ ] Add more states (VIC, QLD, etc.)
- [ ] Calculate scores for all API suburbs
- [ ] Export functionality
- [ ] Suburb comparison tool
- [ ] Email alerts
- [ ] Save favorites

## Environment Variables

Create `.env` file:
```
MICROBURBS_API_KEY=your_api_key_here
DATABASE_URL=postgresql://... (if using database)
```

