from datetime import datetime, timezone

class Transaction:
    def __init__(self, user_id, amount, location, device_id, is_fraud=False):
        self.user_id = user_id
        self.amount = amount
        self.location = location
        self.device_id = device_id
        self.timestamp = datetime.now(timezone.utc)
        self.is_fraud = is_fraud

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "amount": self.amount,
            "location": self.location,
            "device_id": self.device_id,
            "timestamp": self.timestamp,
            "is_fraud": self.is_fraud
        }