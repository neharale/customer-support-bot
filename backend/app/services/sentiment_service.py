from textblob import TextBlob

class SentimentService:
    def analyze(self, message: str) -> str:
        polarity = TextBlob(message).sentiment.polarity

        if polarity <= -0.25:
            return "negative"
        elif polarity >= 0.25:
            return "positive"
        return "neutral"