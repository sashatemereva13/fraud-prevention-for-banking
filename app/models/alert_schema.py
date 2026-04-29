from datetime import datetime, timezone


class Alert:
    def __init__(self, user_id, alert_type, message, severity="MEDIUM"):
        self.user_id = user_id
        self.alert_type = alert_type
        self.message = message
        self.severity = severity
        self.timestamp = datetime.now(timezone.utc)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "alert_type": self.alert_type,
            "message": self.message,
            "severity": self.severity,
            "timestamp": self.timestamp
        }