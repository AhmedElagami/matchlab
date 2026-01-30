# Playwright E2E Tests

This directory contains end-to-end tests for the Mentor-Mentee Matchmaker application using Playwright.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Install Playwright browsers:
   ```bash
   playwright install
   ```

## Running Tests

Run all tests:
```bash
pytest playwright_tests/
```

Run tests with browser UI visible:
```bash
pytest playwright_tests/ --headed
```

Run specific test file:
```bash
pytest playwright_tests/tests/test_admin_match_results.py
```

## Test Structure

- `conftest.py`: Shared fixtures and configuration
- `tests/`: Test files organized by feature area
- Each test file focuses on a specific UI area or workflow

## Writing Tests

- Use `data-testid` attributes for element selection
- Follow the Arrange-Act-Assert pattern
- Use Django fixtures for test data setup
- Test both happy paths and edge cases