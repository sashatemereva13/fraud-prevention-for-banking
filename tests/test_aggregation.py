from app.services.transaction_service import (
    suspicious_transaction_frequency
)

results = suspicious_transaction_frequency()

print(results)