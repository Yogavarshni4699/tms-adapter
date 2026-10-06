# Test Suite Guide

## Overview

Comprehensive pytest-based test suite for TMS adapter with 19 tests covering connection, commands, response parsing, protocol framing, security, and known load data.

## Test Structure

### Test Classes (19 tests total)

- **TestTMSClientConnection** (4 tests) — Client initialization, real TMS connection, timeout handling
- **TestTMSClientCommands** (5 tests) — DEBUG_ECHO, LOAD_GET, LOAD_QUERY commands
- **TestTMSResponseParsing** (3 tests) — Response parsing and field extraction
- **TestTMSProtocolFraming** (2 tests) — CRLF framing, UTF-8 decoding
- **TestTMSSecurityRules** (2 tests) — Token handling, environment variables
- **TestTMSKnownLoadData** (3 tests) — Load LD00903 verification

## Running Tests

### Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

### Run All Tests

```bash
pytest tests/test_tms_client.py -v
```

### Run with Coverage

```bash
pytest tests/test_tms_client.py --cov=tms_client --cov-report=term-missing
```

### Run Specific Test Class

```bash
pytest tests/test_tms_client.py::TestTMSClientConnection -v
```

## Results

- Tests: 19 passed
- Coverage: 85% (tms_client.py)
- Connection: Verified with real TMS
- Protocol: CRLF framing confirmed
