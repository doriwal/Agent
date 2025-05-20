# 🧠 Agent-Based Incident Analyzer

This repository provides a practical introduction to building and orchestrating AI Agents using [Google's MCP framework](https://www.youtube.com/watch?v=P4VFL9nIaIA). 

The project demonstrates how autonomous agents can assist in **incident investigation and analysis** by connecting to real data sources such as **Elasticsearch**, **MySQL**, and various cloud observability tools.

---

## 🎯 Project Goal

Enable automated root cause analysis of production incidents by combining:

- ✅ Log data from **Elasticsearch**
- ✅ Relevant source **code**
- ✅ Database insights via **MySQL**
- ✅ Observability metrics from systems like **Prometheus** and **AWS**

---

## 🛠️ How It Works

1. **Log Retrieval**  
   The agent queries **Elasticsearch** to retrieve incident-related logs.

2. **Code Mapping**  
   It maps these logs to the corresponding **source code** that generated them.

3. **Error Analysis**  
   With access to both logs and code, the agent performs reasoning to analyze the root cause.

4. **Database Queries (Optional)**  
   If additional data is needed, the agent can query a **MySQL database** using:
   - Generic SQL queries
   - Predefined queries configured via a `config` file (no code changes required)

---

## 📡 Future Integrations

Planned enhancements include adding more agents using the MCP framework:

- 🔄 **Confluent MCP** – Automatically update on-call runbooks
- 📊 **Prometheus Agent** – Fetch CPU, memory, and custom metrics
- ☁️ **AWS Metrics Agent** – Gather cloud monitoring data

---

## ⚙️ MySQL Agent Highlights

- Supports a flexible `run_query` tool
- Allows defining reusable SQL snippets in a config file
- Keeps the logic externalized to avoid hardcoded SQL in code

---

## 📽️ Resources

- [Introduction to MCP and Agent Framework (YouTube)](https://www.youtube.com/watch?v=P4VFL9nIaIA)

---

## 💡 Who is this for?

This project is ideal for:

- DevOps engineers
- SREs
- Platform teams
- Developers exploring AI-driven automation for incident response

---

Feel free to clone, extend, or contribute!


