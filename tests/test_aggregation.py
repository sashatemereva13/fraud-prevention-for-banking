from app.services.transaction_service import (
    suspicious_transaction_frequency
)

results = suspicious_transaction_frequency()

print(results)

from app.services.transaction_service import (
    daily_spending_analysis
)

print("\nDaily Spending Analysis:\n")

results = daily_spending_analysis()

for result in results[:5]:
    print(result)