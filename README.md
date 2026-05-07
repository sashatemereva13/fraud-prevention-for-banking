# Real-Time Fraud Detection System

A distributed fraud detection system that combines document storage (MongoDB), real-time behavioral analysis (Redis), and graph-based anomaly detection (Neo4j) to identify suspicious transactions in real time.

## 📌 Overview

This project simulates a real-world fraud detection system used in financial platforms.

It processes transactions in real time and evaluates risk using:

- behavioral anomalies (velocity, device, location)
- transaction history
- network relationships between users

Each transaction is assigned a dynamic risk score and classified as:

- allow
- review
- block

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

Neo4j is used to model relationships that are difficult to detect from a single transaction row. Instead of only storing transactions as documents, the system builds a graph of users, accounts, devices, IP addresses, and money transfers.

Main graph entities:

- `User`
- `Account`
- `Device`
- `IpAddress`

Main relationships:

- `(User)-[:OWNS]->(Account)`
- `(User)-[:USES]->(Device)`
- `(User)-[:LOGGED_IN_FROM]->(IpAddress)`
- `(Account)-[:TRANSFERRED_TO]->(Account)`

The Neo4j module detects:

- Circular transfer rings, where money returns to the same account through a chain of transfers
- Shared devices used by many different users
- Shared IP addresses used by many users in a short time window
- Rapid forwarding chains, where money moves quickly through several accounts
- Weak trust networks, where a user has no verified trusted connections

Script files:

- `scripts/test_live.py` - seeds Neo4j fraud patterns and runs live API checks
- `scripts/test_full_pipeline.py` - full demo showing Neo4j, MongoDB, and Redis working together

### 🧠 Fraud Engine

- Combines multiple signals into a risk score
- Classifies transactions as allow / review / block

The main orchestration happens in `app/core/fraud_engine.py`.

For each transaction:

1. Neo4j graph checks are executed through `run_all_checks(...)`
2. MongoDB history is checked for previous suspicious behavior and amount anomalies
3. Redis behavior checks are used for real-time signals such as velocity, new device, new IP, and cooldown
4. `app/core/risk_scoring.py` combines the subscores into one final risk score
5. The transaction is classified as `allow`, `review`, or `block`

## ▶️ How to Run

### 1. Clone the repository

```bash
git clone <repo-url>
cd fraud-detection-system
```

### 2. Configure environment

Create a `.env` file from the example and set the Neo4j password:

```bash
cp .env.example .env
```

Example:

```env
NEO4J_PASSWORD=your_password_here
```

### 3. Start services

Docker Compose starts MongoDB, Redis, Neo4j, and the FastAPI application.

```bash
docker compose up -d --build
```

The API is then available at:

- `http://localhost:8000`
- `http://localhost:8000/docs`

If you prefer running the API locally instead of inside Docker, start only the databases and then run the app:

```bash
docker compose up -d mongodb redis neo4j
pip install -r requirements.txt
python3 run.py
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

You can also test the Redis behavior engine directly:

### Analyze Transaction Behavior (Redis)

**POST /analyze-transaction**

```json
{
  "user_id": "user_1",
  "device": "device_123",
  "location": "France:Paris",
  "ip_address": "192.168.1.1"
}
```

### Get Dashboard Data

**GET /dashboard**

Returns aggregated fraud statistics.

### Get Alerts

**GET /alerts**

Returns all detected fraud alerts.

## 🧪 Live Tests And Demo Scripts

Make sure Docker services and the API are running before using the live scripts:

```bash
docker compose up -d --build
```

### Full Pipeline Demo

This is the recommended professor demo because it shows all three databases contributing to fraud detection.

```bash
python3 scripts/test_full_pipeline.py
```

It demonstrates:

- Neo4j graph fraud detection
- MongoDB transaction history scoring
- Redis real-time behavior scoring
- A clean transaction used as a control case

### Neo4j-Focused Live Test

This script seeds Neo4j with graph fraud patterns, then sends transactions to the API.

```bash
python3 scripts/test_live.py
```

It demonstrates:

- Circular transfer ring detection
- Shared device detection
- Shared IP detection
- Redis velocity behavior
- Clean transaction comparison

### Neo4j Graph Simulation Helper

This helper creates graph structures directly in Neo4j for manual testing.

```bash
python3 scripts/simulate_fraud.py
```

It creates:

- A circular transfer ring
- A rapid forwarding chain

After running it, the printed account IDs can be checked through the API endpoints.

## 🔎 Neo4j API Checks

Inspect whether an account is part of a circular transfer ring:

```http
GET /transactions/graph/ring/{account_id}
```

Inspect how many users share a device fingerprint:

```http
GET /transactions/graph/device/{fingerprint}
```

Example:

```bash
curl http://localhost:8000/transactions/graph/ring/acc-ring-A
curl http://localhost:8000/transactions/graph/device/SHARED-DEVICE-001
```

## 🌱 Seed Data

Seed sample Neo4j users and devices:

```bash
python3 scripts/seed_users.py
```

Seed sample MongoDB transactions:

```bash
python3 scripts/seed_transactions.py
```

Note: `scripts/seed_transactions.py` clears the MongoDB transactions collection before inserting sample data.

## 🔵 MongoDB (Persistence & Aggregation Analysis)

MongoDB is used as the primary document database for persistent transaction storage in the fraud detection system.

A document-oriented database was chosen because financial transactions contain nested and flexible data structures such as:

- sender information
- receiver information
- device metadata
- location data
- fraud analysis results

MongoDB allows these complex transaction objects to be stored naturally as JSON-like documents without requiring rigid relational schemas.

Main MongoDB collections:

- `transactions`
- `users`
- `fraud_alerts`

Example transaction document:

```json
{
  "id": "txn_001",
  "sender": {
    "account_id": "acc_001",
    "user_id": "user_001",
    "username": "alice"
  },
  "receiver": {
    "account_id": "acc_002",
    "user_id": "user_002",
    "username": "bob"
  },
  "amount": 500,
  "currency": "EUR",
  "device": {
    "device_id": "dev_001",
    "ip_address": "192.168.1.10"
  },
  "location": {
    "country": "France",
    "city": "Paris"
  },
  "status": "approved",
  "timestamp": "2026-05-07T12:00:00Z",
  "risk_score": 25,
  "decision": "allow"
}
````

MongoDB is also used for analytical fraud detection using aggregation pipelines.

### Aggregation Pipeline 1 — Suspicious Transaction Frequency

Function:

```python
suspicious_transaction_frequency()
```

Purpose:

This aggregation groups transactions by sender account and counts how many transactions each account performs within a period of time.

It helps identify:

* unusually active accounts
* bot-like transaction behavior
* potential fraud rings
* high-frequency suspicious transfers

Example pipeline stages:

* `$group`
* `$sum`
* `$match`
* `$sort`

### Aggregation Pipeline 2 — Daily Spending Analysis

Function:

```python
daily_spending_analysis()
```

Purpose:

This aggregation calculates:

* total transaction amount per day
* number of transactions per day

It helps detect:

* abnormal spending spikes
* sudden increases in transaction activity
* suspicious financial patterns

Example pipeline stages:

* `$group`
* `$project`
* `$sum`
* `$sort`

Testing was performed using:

```bash
python -m tests.test_aggregation
```

Example output:

```bash
Daily Spending Analysis:

{'_id': {'date': None}, 'total_amount': 1150, 'transaction_count': 3}
```

MongoDB functionality was verified through:

* Docker container deployment
* MongoDB Compass inspection
* Manual transaction insertion
* Aggregation pipeline execution
* API-based transaction storage

MongoDB provides scalable document storage together with flexible aggregation capabilities for fraud analytics and historical transaction analysis.


