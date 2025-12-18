import asyncio
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.models import ContentItem
from app.services.content_processor import processor

async def _backfill():
    db: Session = SessionLocal()
    try:
        items = db.query(ContentItem).all()
        for it in items:
            # skip items already processed or where you don't want reprocessing
            await processor.process_content_task(it.id)
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(_backfill())