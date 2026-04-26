from app.services.transaction_service import create_transaction

transaction = {
    "user_id": "user_1",
    "amount": 1000,
    "location": "Paris",
    "device_id": "device_abc"
}

result = create_transaction(transaction)

print(result)