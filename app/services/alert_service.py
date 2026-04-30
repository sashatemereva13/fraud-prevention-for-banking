from app.db.mongo import alerts_collection
from app.models.alert_schema import Alert


# CREATE ALERT
def create_alert(user_id, alert_type, message, severity="MEDIUM"):
    alert = Alert(
        user_id=user_id,
        alert_type=alert_type,
        message=message,
        severity=severity
    )

    alerts_collection.insert_one(alert.to_dict())

    return {
        "message": "Alert created successfully",
        "user_id": user_id
    }


# GET ALL ALERTS
def get_all_alerts():
    return list(alerts_collection.find({}, {"_id": 0}))