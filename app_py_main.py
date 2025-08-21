#!/usr/bin/env python3
"""
CredTech Explainable Credit Intelligence Platform
Main Flask Application
"""

import os
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import pandas as pd
import numpy as np
from src.models.credit_scorer import CreditScorer
from src.models.explainer import ModelExplainer
from src.data.ingestion import DataIngestion
from config.settings import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS for frontend integration
CORS(app)

# Rate limiting
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Initialize components
data_ingestion = DataIngestion()
credit_scorer = CreditScorer()
explainer = ModelExplainer()

# Mock data for demonstration (replace with real data pipeline)
MOCK_DATA = {
    'AAPL': {
        'company_name': 'Apple Inc.',
        'sector': 'Technology',
        'current_score': 820,
        'score_letter': 'AA',
        'score_change': 1.2,
        'last_updated': datetime.now(),
        'features': {
            'debt_to_equity': 0.65,
            'current_ratio': 1.45,
            'roe': 0.28,
            'revenue_growth': 0.08,
            'market_volatility': 0.24,
            'news_sentiment': 0.72
        },
        'events': [
            {
                'timestamp': datetime.now() - timedelta(hours=2),
                'title': 'Q4 Earnings Beat Expectations',
                'source': 'SEC Filing',
                'impact': 'positive',
                'score_impact': 3.2,
                'description': 'Apple reported Q4 revenue of $119.6B, beating estimates'
            },
            {
                'timestamp': datetime.now() - timedelta(hours=8),
                'title': 'Vision Pro Launch Update',
                'source': 'Press Release',
                'impact': 'positive',
                'score_impact': 1.8,
                'description': 'Strong early adoption metrics for Vision Pro'
            }
        ]
    },
    'TSLA': {
        'company_name': 'Tesla Inc.',
        'sector': 'Automotive',
        'current_score': 680,
        'score_letter': 'BBB',
        'score_change': -3.2,
        'last_updated': datetime.now(),
        'features': {
            'debt_to_equity': 0.85,
            'current_ratio': 1.29,
            'roe': 0.19,
            'revenue_growth': 0.15,
            'market_volatility': 0.45,
            'news_sentiment': 0.42
        },
        'events': [
            {
                'timestamp': datetime.now() - timedelta(hours=1),
                'title': 'Production Target Concerns',
                'source': 'Earnings Call',
                'impact': 'negative',
                'score_impact': -4.5,
                'description': 'CEO warns of potential Q1 2025 production delays'
            }
        ]
    }
}

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/issuers')
@limiter.limit("100 per minute")
def get_issuers():
    """Get list of available issuers"""
    issuers = []
    for ticker, data in MOCK_DATA.items():
        issuers.append({
            'ticker': ticker,
            'company_name': data['company_name'],
            'sector': data['sector'],
            'current_score': data['current_score'],
            'score_letter': data['score_letter']
        })
    
    return jsonify({
        'issuers': issuers,
        'count': len(issuers)
    })

@app.route('/api/score/<ticker>')
@limiter.limit("500 per minute")
def get_credit_score(ticker):
    """Get current credit score for an issuer"""
    ticker = ticker.upper()
    
    if ticker not in MOCK_DATA:
        return jsonify({'error': 'Issuer not found'}), 404
    
    data = MOCK_DATA[ticker]
    
    # In production, this would call the actual credit scoring model
    # score_data = credit_scorer.calculate_score(ticker)
    
    return jsonify({
        'ticker': ticker,
        'company_name': data['company_name'],
        'score': data['current_score'],
        'score_letter': data['score_letter'],
        'score_change': data['score_change'],
        'last_updated': data['last_updated'].isoformat(),
        'confidence': 0.89,  # Model confidence
        'next_update': (datetime.now() + timedelta(minutes=15)).isoformat()
    })

@app.route('/api/features/<ticker>')
@limiter.limit("200 per minute")
def get_feature_importance(ticker):
    """Get feature importance and explanations"""
    ticker = ticker.upper()
    
    if ticker not in MOCK_DATA:
        return jsonify({'error': 'Issuer not found'}), 404
    
    data = MOCK_DATA[ticker]
    features = data['features']
    
    # In production, this would use SHAP or similar explainability tools
    # explanations = explainer.explain_prediction(ticker, features)
    
    feature_importance = []
    for feature, value in features.items():
        # Mock feature importance calculation
        importance = abs(value - 0.5) * 100  # Simplified importance
        impact_type = 'positive' if value > 0.5 else 'negative'
        
        feature_importance.append({
            'feature': feature.replace('_', ' ').title(),
            'value': round(value * 100, 1),
            'importance': round(importance, 1),
            'impact': impact_type,
            'description': get_feature_description(feature)
        })
    
    # Sort by importance
    feature_importance.sort(key=lambda x: x['importance'], reverse=True)
    
    return jsonify({
        'ticker': ticker,
        'features': feature_importance,
        'model_version': '1.2.3',
        'explanation_method': 'SHAP',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/events/<ticker>')
@limiter.limit("100 per minute")
def get_recent_events(ticker):
    """Get recent events affecting the credit score"""
    ticker = ticker.upper()
    
    if ticker not in MOCK_DATA:
        return jsonify({'error': 'Issuer not found'}), 404
    
    events = MOCK_DATA[ticker]['events']
    
    formatted_events = []
    for event in events:
        formatted_events.append({
            'timestamp': event['timestamp'].isoformat(),
            'title': event['title'],
            'source': event['source'],
            'impact': event['impact'],
            'score_impact': event['score_impact'],
            'description': event['description'],
            'processed_by': 'NLP Engine v2.1'
        })
    
    return jsonify({
        'ticker': ticker,
        'events': formatted_events,
        'count': len(formatted_events)
    })

@app.route('/api/trend/<ticker>')
@limiter.limit("100 per minute")
def get_score_trend(ticker):
    """Get historical score trend data"""
    ticker = ticker.upper()
    
    if ticker not in MOCK_DATA:
        return jsonify({'error': 'Issuer not found'}), 404
    
    # Generate mock trend data (in production, query from database)
    base_score = MOCK_DATA[ticker]['current_score']
    
    trend_data = []
    for i in range(30, 0, -1):
        date = datetime.now() - timedelta(days=i)
        # Add some realistic variation
        variation = np.random.normal(0, 5)
        score = max(300, min(900, base_score + variation))
        
        trend_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'score': round(score, 1),
            'score_letter': score_to_letter(score)
        })
    
    return jsonify({
        'ticker': ticker,
        'trend_data': trend_data,
        'period': '30_days'
    })

@app.route('/api/compare/<ticker>')
@limiter.limit("50 per minute")
def compare_with_peers(ticker):
    """Compare issuer with sector peers"""
    ticker = ticker.upper()
    
    if ticker not in MOCK_DATA:
        return jsonify({'error': 'Issuer not found'}), 404
    
    data = MOCK_DATA[ticker]
    sector = data['sector']
    
    # Mock peer comparison data
    peers = []
    if sector == 'Technology':
        peers = [
            {'ticker': 'MSFT', 'score': 850, 'letter': 'AA'},
            {'ticker': 'GOOGL', 'score': 810, 'letter': 'AA'},
            {'ticker': 'META', 'score': 720, 'letter': 'A'},
        ]
    elif sector == 'Automotive':
        peers = [
            {'ticker': 'GM', 'score': 650, 'letter': 'BBB'},
            {'ticker': 'F', 'score': 580, 'letter': 'BB'},
            {'ticker': 'RIVN', 'score': 520, 'letter': 'BB'},
        ]
    
    sector_average = np.mean([p['score'] for p in peers])
    
    return jsonify({
        'ticker': ticker,
        'current_score': data['current_score'],
        'sector': sector,
        'sector_average': round(sector_average, 1),
        'peers': peers,
        'percentile': calculate_percentile(data['current_score'], [p['score'] for p in peers])
    })

def get_feature_description(feature):
    """Get human-readable description for features"""
    descriptions = {
        'debt_to_equity': 'Ratio of total debt to shareholder equity',
        'current_ratio': 'Ability to pay short-term obligations',
        'roe': 'Return on equity - profitability measure',
        'revenue_growth': 'Year-over-year revenue growth rate',
        'market_volatility': 'Stock price volatility indicator',
        'news_sentiment': 'Sentiment analysis of recent news coverage'
    }
    return descriptions.get(feature, 'Financial metric')

def score_to_letter(score):
    """Convert numeric score to letter grade"""
    if score >= 850: return 'AAA'
    elif score >= 800: return 'AA'
    elif score >= 750: return 'A'
    elif score >= 700: return 'BBB'
    elif score >= 650: return 'BB'
    elif score >= 600: return 'B'
    else: return 'CCC'

def calculate_percentile(score, peer_scores):
    """Calculate percentile rank among peers"""
    all_scores = peer_scores + [score]
    return round((sorted(all_scores).index(score) + 1) / len(all_scores) * 100, 1)

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(429)
def ratelimit_handler(error):
    return jsonify({'error': 'Rate limit exceeded'}), 429

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Development server
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('FLASK_ENV') == 'development'
    )
