from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


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


class FraudDecision(str, Enum):
    ALLOW = "allow"
    REVIEW = "review"
    BLOCK = "block"


class GraphSignals(BaseModel):
    ring_detected: bool = False
    ring_hop_count: int = 0
    shared_device_users: int = 0
    shared_ip_users: int = 0
    rapid_forward_chain: bool = False
    trust_links: int = 0
    cluster_fraud_members: int = 0


class TransactionCreate(BaseModel):
    sender: UserInfo
    receiver: UserInfo

    amount: float
    currency: str

    device: DeviceInfo
    location: LocationInfo

    status: str = "approved"
    timestamp: datetime

    risk_score: float = 0.0
    decision: FraudDecision = FraudDecision.ALLOW
    graph_signals: GraphSignals = Field(default_factory=GraphSignals)
