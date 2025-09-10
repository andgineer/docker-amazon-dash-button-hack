# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Docker-based Amazon Dash Button hack that sniffs network traffic to detect Amazon Dash button presses and triggers various actions like writing to Google Sheets, Google Calendar, or firing IFTTT events. The project is primarily written in Python 3.12+ and uses Scapy for network packet inspection.

## Development Commands

### Environment Setup
```bash
# Set up or activate development environment
. ./activate.sh

# Install/upgrade dependencies
make reqs
```

### Testing and Quality
```bash
# Run tests with doctests
pytest

# Run network sniff check (requires sudo)
make check

# Type checking (via pre-commit hook)
mypy src/

# Linting (via pre-commit hook)
ruff check src/
ruff format src/
```

### Development Workflow
```bash
# Build documentation
make docs

# Version management
make ver-bug     # Bump bug version
make ver-feature # Bump feature version
make ver-release # Bump release version

# View all available make commands
make help
```

### Running the Application
```bash
# For development on macOS/Windows (cannot sniff in Docker)
sudo python src/amazon_dash.py

# For production (Linux with Docker)
docker run --net host -it --rm -v $PWD/../amazon-dash-private:/amazon-dash-private:ro andgineer/amazon-dash-button-hack
```

## Code Architecture

### Core Components

**Main Application (`src/amazon_dash.py`)**
- `AmazonDash` class: Main server that sniffs ARP traffic to detect button presses
- Uses Scapy for network packet inspection
- Implements debounce logic to prevent duplicate button press detection
- Loads configuration from JSON files in `amazon-dash-private/` directory

**Configuration Models (`src/models.py`)**
- Pydantic models for type-safe configuration
- Defines button actions, settings, time summaries, and dashboard items
- Uses Python 3.10+ `collections.abc` for type hints

**Action Processing (`src/action.py`)**
- `Action` class: Processes button press events and executes configured actions
- Coordinates between different service integrations (Google, IFTTT, OpenHab)
- Handles time-based action summaries and conditional logic

### Service Integrations

The project supports multiple external service integrations:
- **Google Services** (`google_api.py`, `google_sheet.py`, `google_calendar.py`): Google Sheets and Calendar integration
- **IFTTT** (`ifttt.py`): Webhook-based automation
- **OpenHab** (`openhab.py`): Home automation system integration

### Configuration Structure

Required configuration files in `amazon-dash-private/`:
- `settings.json`: Main application settings
- `buttons.json`: Button MAC addresses and action mappings
- `amazon-dash-hack.json`: Google API credentials
- `ifttt-key.json`: IFTTT webhook key
- `openweathermap-key.json`: Weather API key (optional)

### Code Quality Standards

- **Line length**: 100 characters (99 for tests)
- **Type checking**: MyPy enabled for src/ (excluded for tests/)
- **Linting**: Ruff with extensive rule set including Pylint, security checks, import ordering
- **Formatting**: Ruff formatter
- **Pre-commit hooks**: Automated code quality checks
- **Testing**: Pytest with doctests enabled

### Key Dependencies

- `scapy`: Network packet inspection
- `pydantic`: Configuration validation and type safety
- `google-api-python-client`: Google services integration
- `requests`: HTTP client for webhooks
- `python-dateutil`: Date/time handling

The application requires `sudo` privileges for network sniffing and works best on Linux systems where Docker can access host networking directly.
