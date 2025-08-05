# ⚖️ Distributed Load Balancer & Scalable Server Architecture

## 📌 Overview

A **Python-based multi-threaded load balancer** designed to simulate real-world distributed system behavior — including **sticky sessions**, **rate limiting**, **health checks**, and **auto-scaling** server nodes. This project demonstrates advanced systems design, networking, and concurrency principles, aligned with production-level infrastructure used in cloud environments.

> ✅ Built entirely in **Python** using low-level socket programming and threading.

---

## 🛠️ Tech Stack

- **Language:** Python 3.x  
- **Concurrency:** `threading`, `ThreadPoolExecutor`  
- **Networking:** `socket`, `select`, (TLS planned with `ssl`)  
- **Utilities:** `logging`, `time`, `random`, `uuid`  
- **Optional:** Flask (for dashboard), `argparse` (CLI)

---

## 🚀 Features

- 🚦 **Multi-threaded load balancer** that handles 2000+ concurrent clients using socket communication
- 🧠 **Smart server selection** based on real-time server load and response time
- 🔁 **Sticky sessions** using session IDs for consistent routing
- 📈 **Dynamic server scaling**: auto-spawns/kills server instances based on load
- 🛡️ **Health checks & failover**: replaces failed nodes without interrupting sessions
- 🔒 **Rate limiting** per IP to avoid abuse (DoS protection); TLS planned
- 📊 **Thread-safe logging** of traffic, health stats, and client session activity

---

## 🧠 Architecture

```text
+-----------+      +-------------------+      +--------------------+
|  Clients  | <--> |  Load Balancer.py  | <--> |  ServerPool (n)     |
+-----------+      |  (Python Threaded) |      |  ServerX.py         |
                   +-------------------+      +--------------------+
                            |  |  |
                      Health Check Thread
                      Session ID Routing
                      Rate Limit Filter
                      Auto-scaling Manager
