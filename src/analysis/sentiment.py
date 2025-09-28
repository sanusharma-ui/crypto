from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd

def get_sentiment(texts):
    """
    Calculate average sentiment score from texts. Returns: {'avg': float, 'breakdown': list}
    """
    analyzer = SentimentIntensityAnalyzer()
    scores = []
    breakdown = []
    for text in texts:
        score = analyzer.polarity_scores(text)['compound']
        scores.append(score)
        if score > 0.05:
            breakdown.append("Positive")
        elif score < -0.05:
            breakdown.append("Negative")
        else:
            breakdown.append("Neutral")
    avg_score = sum(scores) / len(scores) if scores else 0
    return {'avg': avg_score, 'breakdown': breakdown}