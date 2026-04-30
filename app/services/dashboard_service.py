from app.services.transaction_service import (
    daily_spending_analysis,
    suspicious_transaction_frequency
)

# DASHBOARD DATA AGGREGATION
def get_dashboard_data():
    return {
        "daily_spending": daily_spending_analysis(),
        "suspicious_transactions": suspicious_transaction_frequency()
    }