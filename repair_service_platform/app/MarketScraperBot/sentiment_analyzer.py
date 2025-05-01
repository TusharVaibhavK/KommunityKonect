import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter

# Download necessary NLTK data (only needed once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class SentimentAnalyzer:
    """
    A class for analyzing sentiment in repair service reviews
    """
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        
        # Custom sentiment dictionaries for repair industry
        self.positive_words = {
            'professional', 'clean', 'timely', 'polite', 'expert', 'friendly',
            'helpful', 'knowledgeable', 'excellent', 'perfect', 'recommend',
            'fast', 'quick', 'efficient', 'fixed', 'solved', 'patient',
            'thorough', 'honest', 'reliable', 'quality', 'good', 'great',
            'amazing', 'best', 'satisfied', 'happy', 'skilled', 'neat',
            'organized', 'wonderful', 'awesome', 'fantastic', 'superb',
            'terrific', 'outstanding', 'exceptional', 'impressive'
        }
        
        self.negative_words = {
            'delay', 'late', 'rude', 'expensive', 'overcharge', 'unprofessional',
            'dirty', 'messy', 'slow', 'broke', 'damaged', 'poor', 'bad',
            'terrible', 'awful', 'horrible', 'worst', 'disappointing', 'useless',
            'incompetent', 'careless', 'sloppy', 'dishonest', 'unreliable',
            'problem', 'issue', 'fault', 'fail', 'waste', 'money', 'time',
            'unsatisfied', 'unhappy', 'didn\'t', 'not', 'never', 'wrong'
        }
        
        # Repair-specific phrases
        self.repair_issues = {
            'leak', 'drip', 'clog', 'block', 'noise', 'loose', 'tight',
            'broken', 'crack', 'rust', 'corrode', 'stuck', 'water pressure',
            'drainage', 'overflow', 'installation', 'replacement'
        }
    
    def analyze_review(self, review_text):
        """Analyze a single review for sentiment and repair-specific issues"""
        if not review_text:
            return {
                'sentiment': 'neutral',
                'positive_words': [],
                'negative_words': [],
                'repair_issues': [],
                'score': 0
            }
        
        # Convert to lowercase and tokenize
        tokens = word_tokenize(review_text.lower())
        
        # Remove stopwords and punctuation
        filtered_tokens = [word for word in tokens if word.isalnum() and word not in self.stop_words]
        
        # Count sentiment words
        positive_matches = [word for word in filtered_tokens if word in self.positive_words]
        negative_matches = [word for word in filtered_tokens if word in self.negative_words]
        
        # Look for repair-specific terms
        repair_matches = [word for word in filtered_tokens if word in self.repair_issues]
        
        # Calculate sentiment score
        sentiment_score = len(positive_matches) - len(negative_matches)
        
        # Determine overall sentiment
        if sentiment_score > 0:
            sentiment = 'positive'
        elif sentiment_score < 0:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'positive_words': positive_matches,
            'negative_words': negative_matches,
            'repair_issues': repair_matches,
            'score': sentiment_score
        }
    
    def analyze_multiple_reviews(self, reviews):
        """Analyze multiple reviews and provide aggregate insights"""
        if not reviews:
            return {
                'overall_sentiment': 'neutral',
                'positive_percentage': 0,
                'negative_percentage': 0,
                'neutral_percentage': 0,
                'common_positive_words': [],
                'common_negative_words': [],
                'common_repair_issues': []
            }
        
        results = [self.analyze_review(review) for review in reviews]
        
        # Count sentiment categories
        sentiment_counts = Counter([r['sentiment'] for r in results])
        total = len(results)
        
        # Collect all words for frequency analysis
        all_positive_words = [word for r in results for word in r['positive_words']]
        all_negative_words = [word for r in results for word in r['negative_words']]
        all_repair_issues = [word for r in results for word in r['repair_issues']]
        
        # Find most common words in each category
        common_positive = Counter(all_positive_words).most_common(5)
        common_negative = Counter(all_negative_words).most_common(5)
        common_issues = Counter(all_repair_issues).most_common(5)
        
        # Determine overall sentiment
        positive_count = sentiment_counts.get('positive', 0)
        negative_count = sentiment_counts.get('negative', 0)
        neutral_count = sentiment_counts.get('neutral', 0)
        
        if positive_count > negative_count and positive_count > neutral_count:
            overall = 'positive'
        elif negative_count > positive_count and negative_count > neutral_count:
            overall = 'negative'
        else:
            overall = 'neutral'
        
        return {
            'overall_sentiment': overall,
            'positive_percentage': (positive_count / total) * 100 if total > 0 else 0,
            'negative_percentage': (negative_count / total) * 100 if total > 0 else 0,
            'neutral_percentage': (neutral_count / total) * 100 if total > 0 else 0,
            'common_positive_words': common_positive,
            'common_negative_words': common_negative,
            'common_repair_issues': common_issues,
            'total_reviews': total
        }
