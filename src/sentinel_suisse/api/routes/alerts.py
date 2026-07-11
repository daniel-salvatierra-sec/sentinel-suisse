"""Alert history and admin dispatch."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from sentinel_suisse.api.auth import get_current_user, verify_admin
from sentinel_suisse.api.deps import get_db
from sentinel_suisse.api.rate_limit import limiter
from sentinel_suisse.config import get_settings
from sentinel_suisse.models.alert_log import AlertLog
from sentinel_suisse.models.user import User
from sentinel_suisse.schemas.alert import AlertLogRead, DispatchStatsRead
from sentinel_suisse.services.alerts import AlertService

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertLogRead])
@limiter.limit(lambda: get_settings().rate_limit)
def list_my_alerts(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[AlertLog]:
    stmt = (
        select(AlertLog)
        .where(AlertLog.user_id == current_user.id)
        .order_by(AlertLog.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(db.scalars(stmt).all())


@router.post("/dispatch", response_model=DispatchStatsRead)
@limiter.limit(lambda: get_settings().rate_limit)
def dispatch_alerts(
    request: Request,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin),
    listing_id: int = Query(gt=0),
) -> DispatchStatsRead:
    try:
        stats = AlertService(db).dispatch_for_listing(listing_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return DispatchStatsRead(
        matched=stats.matched,
        sent=stats.sent,
        skipped=stats.skipped,
        failed=stats.failed,
    )
