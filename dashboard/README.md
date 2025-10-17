# 🏘️ Microburbs Interactive Dashboard

Live interactive investment dashboard with filters and Cursor-like theme.

## Features

✅ **Interactive Filters:**
- State selection
- Score range (investment signal)
- Price range
- Data reliability
- Suburb search

✅ **Modern UI:**
- Cursor-inspired dark theme
- Sleek color palette
- Responsive design
- Smooth animations

✅ **Comprehensive Data:**
- 7 suburbs analyzed
- Investment scores (0-100)
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

## Future Enhancements

- [ ] Connect to Microburbs API
- [ ] Add more states (VIC, QLD, etc.)
- [ ] Real-time data updates
- [ ] Export functionality
- [ ] Comparison tool
- [ ] Email alerts

## Environment Variables

Create `.env` file:
```
MICROBURBS_API_KEY=your_api_key_here
DATABASE_URL=postgresql://... (if using database)
```

