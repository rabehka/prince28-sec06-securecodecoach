# SecureCodeCoach

[![CI](https://github.com/rabehka/prince28-sec06-securecodecoach/actions/workflows/ci.yml/badge.svg)](https://github.com/rabehka/prince28-sec06-securecodecoach/actions/workflows/ci.yml)
[![Live](https://img.shields.io/website?url=https%3A%2F%2Fsecurecodecoach.onrender.com%2Fhealth&label=live)](https://securecodecoach.onrender.com/health)
[![Uptime (30 days)](https://img.shields.io/uptimerobot/ratio/m804746261-840a5c0c422b016e93aa23e2)](https://stats.uptimerobot.com)

**Live:** https://securecodecoach.onrender.com · [API docs](https://securecodecoach.onrender.com/docs)
**Status:** Week 1 complete — Live at https://securecodecoach.onrender.com

**An AI-powered secure coding mentor that helps developers identify vulnerabilities and learn safer coding practices using OWASP guidance.**

## 1. Target Users

- Beginner software developers
- Computer science students
- Programmers learning secure coding
- Developers who want to improve application security

## 2. Problem Statement

Developers may write code without identifying security vulnerabilities. This can lead to SQL Injection, Cross-Site Scripting (XSS), insecure authentication, and other security risks.

SecureCodeCoach aims to help developers understand common vulnerabilities and follow secure coding practices through AI-powered explanations and OWASP-based guidance.

## 3. Data Sources

The project uses:

- OWASP Top 10 security guidance
- Sample security vulnerability records stored in `data/sample_records.json`
- Security information and examples used for learning and testing

## 4. Project Goals

- Identify common security vulnerabilities.
- Explain security risks in simple language.
- Provide OWASP-based secure coding guidance.
- Help developers improve their coding practices.
- Build a reliable backend using FastAPI.

## 5. Technology Stack

- Python 3.12
- FastAPI
- Pydantic Settings
- uv
- Pytest
- Ruff
- JSON

## 6. Hardest Problem

One of the challenging parts is building a reliable backend that loads security records correctly and handles errors safely.

Implementing request ID tracking and structured JSON logging is also important for debugging and monitoring API requests.

## 7. Target Metrics

- At least 20 security records in the dataset.
- All API endpoints should return the expected responses.
- At least 6 automated API tests should pass.
- Invalid requests should return proper HTTP error responses.
- Every application request log should include a unique `request_id`.
- Normal API requests should complete within 2 seconds.

## 8. Project Structure

```text
securecodecoach/
│
├── data/
│   └── sample_records.json
│
├── docs/
│   ├── QUESTIONS.md
│   └── REQUIREMENTS.md
│
├── src/
│   └── securecodecoach/
│       ├── api/
│       │   ├── routes/
│       │   │   ├── documents.py
│       │   │   └── health.py
│       │   └── main.py
│       ├── config.py
│       ├── data_loader.py
│       └── logging_setup.py
│
├── tests/
│   ├── test_api.py
│   ├── test_data_loader.py
│   └── test_health.py
│
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── pyproject.toml
├── uv.lock
└── README.md
