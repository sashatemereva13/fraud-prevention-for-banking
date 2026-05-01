from pydantic import BaseModel
from datetime import datetime


class UserInfo(BaseModel):
    account_id: str
    user_id: str
    username: str


class DeviceInfo(BaseModel):
    device_id: str
    ip_address: str


class LocationInfo(BaseModel):
    country: str
    city: str


class TransactionCreate(BaseModel):
    sender: UserInfo
    receiver: UserInfo

    amount: float
    currency: str

    device: DeviceInfo
    location: LocationInfo

    status: str = "approved"
    timestamp: datetime