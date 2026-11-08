import click

from .extensions import db
from .models import Item

SAMPLE_ITEMS = [
    ("WID-001", "Widget", 120),
    ("GAD-002", "Gadget", 35),
    ("SPR-003", "Sprocket", 0),
    ("BOL-004", "Bolt M8", 500),
]


def register_cli(app):
    @app.cli.command("init-db")
    @click.option("--drop", is_flag=True, help="Drop all tables before creating them.")
    def init_db(drop):
        """Create database tables (idempotent)."""
        if drop:
            db.drop_all()
            click.echo("Dropped all tables.")
        db.create_all()
        click.echo(f"Initialised database at {db.engine.url}")

    @app.cli.command("seed-db")
    def seed_db():
        """Insert sample items that do not exist yet (idempotent)."""
        added = 0
        for sku, name, qty in SAMPLE_ITEMS:
            exists = db.session.execute(
                db.select(Item).filter_by(sku=sku)
            ).scalar_one_or_none()
            if exists is None:
                db.session.add(Item(sku=sku, name=name, quantity=qty))
                added += 1
        db.session.commit()
        click.echo(f"Seeded {added} item(s).")
