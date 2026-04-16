# swcpy Software Development Kit (SDK)

Python SDK for interacting with the SportsWorldCentral Fantasy Football API.

## Install

Install from PyPI:

```bash
python -m pip install swcpy-tydennis0501
```

Note: The distribution name on PyPI is `swcpy-tydennis0501`, but imports use `swcpy`.

## Configure Base URL

Set your API base URL with an environment variable or pass it directly in `SWCConfig`.

Example `.env` file:

```env
SWC_API_BASE_URL=https://azure-api-container-hfa4e5dbfehtaad5.eastus-01.azurewebsites.net
```

## Quick Start

```python
from swcpy import SWCClient, SWCConfig

config = SWCConfig(
    swc_base_url="https://azure-api-container-hfa4e5dbfehtaad5.eastus-01.azurewebsites.net",
    backoff=False,
)
client = SWCClient(config)

health = client.get_health_check()
print(health.json())

leagues = client.list_leagues(limit=5)
print(leagues)
```

## Bulk File Download Example

Bulk endpoints return bytes. Write them to disk as shown below:

```python
from swcpy import SWCClient, SWCConfig

config = SWCConfig(
    swc_base_url="https://azure-api-container-hfa4e5dbfehtaad5.eastus-01.azurewebsites.net"
)
client = SWCClient(config)

player_file = client.get_bulk_player_file()

with open("players_file.csv", "wb") as f:
    f.write(player_file)
```

## Common Methods

- Health and analytics: `get_health_check()`, `get_counts()`
- List endpoints: `list_leagues()`, `list_teams()`, `list_players()`, `list_performances()`
- By ID endpoints: `get_league_by_id()`, `get_team_by_id()`, `get_player_by_id()`
- Bulk downloads: `get_bulk_player_file()`, `get_bulk_league_file()`, `get_bulk_performance_file()`, `get_bulk_team_file()`, `get_bulk_team_player_file()`

## Release Process

1. Bump `version` in `pyproject.toml`.
2. Build and validate distributions:

```bash
rm -rf dist build *.egg-info src/*.egg-info
python -m build
python -m twine check dist/*
```

3. Upload to TestPyPI:

```bash
python -m twine upload --repository testpypi dist/*
```

4. Upload to PyPI:

```bash
python -m twine upload dist/*
```
