from flask import Flask, jsonify, render_template
import random

app = Flask(__name__)

# --- Mock Data Sources ---
# In a real app, these would be API calls or database lookups
MOCK_FINANCIAL_DATA = {
    'AAPL': {'revenue_growth': 0.12, 'debt_to_equity': 0.8},
    'TSLA': {'revenue_growth': 0.25, 'debt_to_equity': 1.5},
    'MSFT': {'revenue_growth': 0.15, 'debt_to_equity': 0.5},
    'GOOGL': {'revenue_growth': 0.18, 'debt_to_equity': 0.6},
    'AMZN': {'revenue_growth': 0.22, 'debt_to_equity': 1.1},
}

MOCK_NEWS_DATA = {
    'AAPL': [
        {'title': 'New Product Launch Announced', 'sentiment': 'positive'},
        {'title': 'Supply Chain Concerns Reported', 'sentiment': 'negative'},
    ],
    'TSLA': [
        {'title': 'Production Target Concerns', 'sentiment': 'negative'},
        {'title': 'Supercharger Network Expansion', 'sentiment': 'positive'},
    ],
    'MSFT': [
        {'title': 'AI Partnership Announced', 'sentiment': 'positive'},
        {'title': 'Regulatory Scrutiny', 'sentiment': 'negative'},
    ],
    'GOOGL': [
        {'title': 'Search Update Improves Ad Yield', 'sentiment': 'positive'},
        {'title': 'Antitrust Hearing Scheduled', 'sentiment': 'negative'},
    ],
    'AMZN': [
        {'title': 'Logistics Network Efficiency Gains', 'sentiment': 'positive'},
        {'title': 'Labor Dispute Renewed', 'sentiment': 'negative'},
    ],
}


# --- Core Credit Model Logic ---
class CreditModel:
    def __init__(self, ticker):
        self.ticker = ticker

    def calculate_score(self):
        """Calculates a dynamic credit score based on mock data."""
        financials = MOCK_FINANCIAL_DATA.get(self.ticker, {'revenue_growth': 0, 'debt_to_equity': 0})
        news = MOCK_NEWS_DATA.get(self.ticker, [])

        # Simple weighted scoring logic
        financial_score = (financials['revenue_growth'] * 50) - (financials['debt_to_equity'] * 10)

        sentiment_score = 0
        for event in news:
            if event['sentiment'] == 'positive':
                sentiment_score += 5
            elif event['sentiment'] == 'negative':
                sentiment_score -= 5

        base_score = 75  # A good starting point
        total_score = base_score + financial_score + sentiment_score

        # Add some random fluctuation to simulate real-time updates
        total_score += random.uniform(-2, 2)
        return round(max(60, min(100, total_score)))  # Keep score between 60 and 100

    def get_score_drivers(self):
        """Returns the key factors influencing the score."""
        drivers = []
        financials = MOCK_FINANCIAL_DATA.get(self.ticker, {'revenue_growth': 0, 'debt_to_equity': 0})
        news = MOCK_NEWS_DATA.get(self.ticker, [])

        if financials['revenue_growth'] > 0.1:
            drivers.append({'name': 'Strong Revenue Growth', 'impact': 'positive', 'value': f"+{int(financials['revenue_growth']*100)}%"})
        if financials['debt_to_equity'] < 1.0:
            drivers.append({'name': 'Low Debt', 'impact': 'positive', 'value': f"-{int(financials['debt_to_equity']*10)}%"})

        positive_news = [e for e in news if e['sentiment'] == 'positive']
        if positive_news:
            drivers.append({'name': f"{len(positive_news)} Positive News Events", 'impact': 'positive', 'value': '+5%'})

        negative_news = [e for e in news if e['sentiment'] == 'negative']
        if negative_news:
            drivers.append({'name': f"{len(negative_news)} Negative News Events", 'impact': 'negative', 'value': '-5%'})

        return drivers


# --- Web Routes ---
@app.route('/')
def index():
    return render_template('index.html')


# --- API Routes ---
@app.route('/api/score/<ticker>')
def get_score(ticker):
    model = CreditModel(ticker)
    score = model.calculate_score()
    drivers = model.get_score_drivers()

    # Simulate data source health
    source_health = {
        'SEC Filings': 'green',
        'News API': 'green',
        'Social Media': random.choice(['green', 'yellow', 'red']),
        'Market Data': 'green'
    }

    return jsonify({
        'score': score,
        'change': round(random.uniform(-3, 3), 1),  # Placeholder for real change
        'percentile': random.randint(60, 99),
        'drivers': drivers,
        'source_health': source_health
    })


@app.route('/api/timeline/<ticker>')
def get_timeline(ticker):
    # This is still mock data but shows the structure
    timeline_events = MOCK_NEWS_DATA.get(ticker, [])
    formatted_events = []
    for event in timeline_events:
        formatted_events.append({
            'title': event['title'],
            'date': 'Today',  # Placeholder for real date
            'impact': event['sentiment'],
            'description': f"Event related to {event['title']}."  # Simplified description
        })
    return jsonify({'events': formatted_events})


if __name__ == '__main__':
    # Bind to all interfaces for external access
    app.run(host='0.0.0.0', port=5000, debug=True)

