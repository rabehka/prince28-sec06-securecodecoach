# SecureCodeCoach

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
- Every application log should include a
