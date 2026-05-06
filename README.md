# Real-Time Fraud Detection System

A distributed fraud detection system that combines document storage (MongoDB), real-time behavioral analysis (Redis), and graph-based anomaly detection (Neo4j) to identify suspicious transactions in real time.

## 📌 Overview

This project simulates a real-world fraud detection system used in financial platforms.

It processes transactions in real time and evaluates risk using:

- behavioral anomalies (velocity, device, location)
- transaction history
- network relationships between users

Each transaction is assigned a dynamic risk score and classified as:

- approved
- flagged
- blocked

## 🏗️ Architecture

The system is composed of multiple specialized components:

- **FastAPI** → API layer
- **MongoDB** → persistent transaction storage
- **Redis** → real-time behavioral tracking
- **Neo4j** → graph-based fraud detection

### Data Flow

1. Transaction is received via API
2. Redis is queried for recent user behavior and contributes to the final risk score
3. Fraud engine evaluates risk:
   - rule-based checks
   - behavioral anomalies (Redis)
   - graph anomalies (Neo4j)
4. Transaction is stored in MongoDB
5. Graph relationships are updated in Neo4j
6. Risk score is returned

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **Cache / Real-Time Engine**: Redis
- **Graph Database**: Neo4j
- **Containerization**: Docker Compose

## ⚙️ Features

### 🔵 MongoDB (Persistence)

- Stores all transactions
- Stores user profiles
- Stores fraud alerts

### 🔴 Redis (Real-Time Behavior Engine)

Redis is used for real-time fraud detection by tracking user behavior across transactions.

We use multiple Redis data structures:

- **Sorted Sets (`ZSET`)**
  - Used for transaction velocity detection
  - Stores transaction timestamps per user
  - Enables detection of high-frequency activity within a time window

- **Sets (`SET`)**
  - Used for device tracking
  - Stores known devices per user
  - Detects new or suspicious devices

- **Strings (Key-Value with TTL)**
  - Used for storing recent location and last transaction time
  - Enables detection of geographic anomalies
  - Automatically expires to keep only recent behavior

- **Cooldown Keys (TTL-based)**
  - Prevent rapid repeated actions
  - Helps detect bot-like or automated behavior

These signals are combined into a behavioral risk score and integrated into the main fraud evaluation pipeline.

### 🟣 Neo4j (Graph Analysis)

- Detects transaction loops (money laundering)
- Identifies suspicious clusters
- Analyzes relationships between users

### 🧠 Fraud Engine

- Combines multiple signals into a risk score
- Classifies transactions as approved / flagged / blocked

## ▶️ How to Run

### 1. Clone the repository

```bash
git clone <repo-url>
cd fraud-detection-system
```

### 2. Start services

```bash
docker compose up -d
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the API

```bash
python run.py
```

## 🧪 How to Use

### Create a Transaction

**POST /transactions**

Example:

```json
{
  "sender": { "user_id": "user_1", "account_id": "acc_1", "username": "Alice" },
  "receiver": { "user_id": "user_2", "account_id": "acc_2", "username": "Bob" },
  "amount": 500,
  "currency": "EUR",
  "device": { "device_id": "device_123", "ip_address": "192.168.1.1" },
  "location": { "country": "FR", "city": "Paris" },
  "timestamp": "2026-01-01T10:00:00"
}
```

### Analyze Transaction Behavior (Redis)

**POST /analyze-transaction**

```json
{
  "user_id": "user_1",
  "device": "device_123",
  "location": "Paris"
}
```

### Get Dashboard Data

**GET /dashboard**

Returns aggregated fraud statistics.

### Get Alerts

**GET /alerts**

Returns all detected fraud alerts.

## 🌱 Seed Data

To populate the database with sample data:

```bash
python seed.py
```

This will create sample users and transactions for testing.
