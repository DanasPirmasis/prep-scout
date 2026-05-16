from datetime import datetime, timezone

from sqlalchemy.orm import Session

from db.models.price_history import PriceHistory


def record(
    session: Session,
    *,
    product_id: int,
    price: float,
    retail_price: float | None,
    special_price: float | None,
    is_available: bool,
) -> PriceHistory:
    entry = PriceHistory(
        product_id=product_id,
        price=price,
        retail_price=retail_price,
        special_price=special_price,
        is_available=is_available,
        created_at=datetime.now(timezone.utc),
    )
    session.add(entry)
    session.flush()
    return entry
