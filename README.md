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
2. Redis is queried for recent user behavior
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

- Transaction velocity tracking (sorted sets)
- Device tracking (sets)
- Location tracking
- Temporary risk state using TTL

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
