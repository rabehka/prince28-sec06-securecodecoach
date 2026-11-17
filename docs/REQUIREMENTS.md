\# Project Requirements



\## 1. Functional Requirements



1\. The system must accept source code from users for security analysis.

2\. The system must identify common security vulnerabilities using OWASP guidance.

3\. The system must provide explanations for detected vulnerabilities.

4\. The system must suggest secure coding improvements.

5\. The system must provide API endpoints to check application health and readiness.



\## 2. Non-Functional Requirements



1\. \*\*Performance:\*\* The API should respond to normal requests within 2 seconds.

2\. \*\*Security:\*\* API keys and secrets must be stored in environment variables, not source code.

3\. \*\*Reliability:\*\* The application should handle invalid requests without crashing.

4\. \*\*Maintainability:\*\* The code should follow Python coding standards and pass Ruff checks.

5\. \*\*Testability:\*\* The application should have at least 10 automated tests with a target of 80% code coverage.



\## 3. Technology Requirements



\- Python 3.12

\- FastAPI

\- Pydantic Settings

\- Pytest

\- Ruff

\- OWASP security guidance
