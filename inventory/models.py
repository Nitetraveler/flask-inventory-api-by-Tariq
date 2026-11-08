from datetime import datetime, timezone

from .extensions import db


def _utcnow():
    return datetime.now(timezone.utc)


class Item(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(32), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "sku": self.sku,
            "name": self.name,
            "quantity": self.quantity,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
