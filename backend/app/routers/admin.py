"""Admin desk — mirrors the original pages/admin.py metrics:
Transactions / Success / Suspicious / Fraud / Volume / Success Rate,
risk tiers Low(<=25) Medium(<=50) High(<=75) Critical(<=100),
high-risk alerts (risk_score >= 80) and the transaction table."""
from fastapi import APIRouter, Depends

from .. import db
from ..fraud import models_available
from ..security import admin_claims

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _tier(score: float) -> str:
    if score <= 25:
        return "Low"
    if score <= 50:
        return "Medium"
    if score <= 75:
        return "High"
    return "Critical"


@router.get("/stats")
def stats(_claims: dict = Depends(admin_claims)):
    rows = db.list_transactions(limit=100000)
    total = len(rows)
    success = sum(1 for r in rows if r["status"] == "Success")
    suspicious = sum(1 for r in rows if r["status"] == "Suspicious")
    fraud = sum(1 for r in rows if r["status"] == "Fraud")
    volume = float(sum(r["amount"] or 0 for r in rows))
    success_rate = (success / total * 100) if total else 0.0

    tiers = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
    for r in rows:
        tiers[_tier(float(r["risk_score"] or 0))] += 1

    high_risk = [r for r in rows if float(r["risk_score"] or 0) >= 80][:50]
    recent = rows[:50]
    for r in list(recent) + high_risk:
        r["tier"] = _tier(float(r["risk_score"] or 0))

    return {
        "metrics": {
            "total_tx": total,
            "success": success,
            "suspicious": suspicious,
            "fraud": fraud,
            "volume": round(volume, 2),
            "success_rate": round(success_rate, 2),
        },
        "categories": [
            {"label": "Success", "count": success, "color": "#10B981"},
            {"label": "Suspicious", "count": suspicious, "color": "#F59E0B"},
            {"label": "Fraud", "count": fraud, "color": "#EF4444"},
        ],
        "risk_tiers": [
            {"label": "Low", "count": tiers["Low"], "color": "#3B82F6"},
            {"label": "Medium", "count": tiers["Medium"], "color": "#6366F1"},
            {"label": "High", "count": tiers["High"], "color": "#F59E0B"},
            {"label": "Critical", "count": tiers["Critical"], "color": "#EF4444"},
        ],
        "high_risk": high_risk,
        "recent": recent,
        "ml_model_loaded": models_available(),
    }


@router.get("/users")
def users(_claims: dict = Depends(admin_claims)):
    """Full user registry — everything the store knows about each shopper."""
    rows = db.list_users_with_stats()
    for r in rows:
        r.pop("profile_image", None)  # keep the payload light; image lives on the profile page
    return {"users": rows, "count": len(rows)}
