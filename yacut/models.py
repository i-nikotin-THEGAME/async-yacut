from datetime import datetime
from yacut import db
from settings import Config


class URLMap(db.Model):
    __tablename__ = "url_map"

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(256), nullable=False)
    short = db.Column(db.String(16), unique=True, nullable=False, index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return f"<URLMap {self.short} -> {self.original}>"

    def to_dict(self):
        """Преобразует модель в словарь для API ответов"""
        return dict(
            url=self.original,
            short_link=f"{Config.BASE_URL}/{self.short}")

    def from_dict(self, data):
        """Десериализатор: словарь из JSON -> объект модели"""
        mapping = {"url": "original", "custom_id": "short"}

        for json_key, model_field in mapping.items():
            if json_key in data:
                setattr(self, model_field, data[json_key])
