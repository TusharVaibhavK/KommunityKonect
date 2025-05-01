from datetime import datetime
from repair_service_platform.app.extensions import db

class MarketPrice(db.Model):
    __tablename__ = 'market_prices'
    
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    store = db.Column(db.String(100), nullable=False)
    date_scraped = db.Column(db.DateTime, default=datetime.utcnow)
    url = db.Column(db.String(512))
