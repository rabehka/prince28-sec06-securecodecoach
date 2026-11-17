# \# SecureCodeCoach

# 

# SecureCodeCoach is an AI-powered secure coding mentor that helps developers understand common security vulnerabilities and write safer code using OWASP security guidance.

# 

# \## Problem Statement

# 

# Developers sometimes write code without identifying security vulnerabilities. This can lead to risks such as SQL injection, cross-site scripting, and insecure authentication. SecureCodeCoach aims to help developers identify these issues and understand secure coding practices.

# 

# \## Project Goals

# 

# \- Help developers understand common security vulnerabilities.

# \- Provide OWASP-based security guidance.

# \- Encourage secure coding practices.

# \- Build a reliable backend using FastAPI.

# 

# \## Technology Stack

# 

# \- Python 3.12

# \- FastAPI

# \- Pydantic Settings

# \- uv

# \- Pytest

# \- Ruff

# 

# \## Project Structure

# 

# ```text

# securecodecoach/

# ├── src/

# │   └── securecodecoach/

# ├── tests/

# ├── docs/

# ├── data/

# ├── pyproject.toml

# ├── uv.lock

# └── README.md

# ```

# 

# \## Getting Started

# 

# Install dependencies:

# 

# ```bash

# python -m uv sync

# ```

# 

# Run the application:

# 

# ```bash

# python -m uv run uvicorn securecodecoach.api.main:app --reload

# ```

# 

# \*The application command will be updated when the FastAPI application is created.\*

# 

# \## Project Status

# 

# Day 1 – Foundation setup in progress.

