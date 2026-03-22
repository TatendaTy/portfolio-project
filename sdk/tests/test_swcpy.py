import pytest
from swcpy import SWCClient
from swcpy import SWCConfig
from swcpy.schemas import League, Team, Player, Performance
from io import BytesIO
import pyarrow.parquet as pq
import pandas as pd

def test_health_check():
    """Tests health check from SDK"""
    config = SWCConfig(swc_base_url="http://0.0.0.0:8000", backoff=False)
    client = SWCClient(config)
    response = client.get_health_check()
    assert response.status_code == 200
    assert response.json() == {"message": "This is an API health check: status successful"}

def test_list_leagues():
    """Tests get leagues from SDK"""
    config = SWCConfig(swc_base_url="http://0.0.0.0:8000", backoff=False)
    client = SWCClient(config)
    leagues_response = client.list_leagues()
    # Assert the endpoint returned a list object
    assert isinstance(leagues_response, list)
    # Assert each item in the list is an instance of a Pydantic League object
    for league in leagues_response:
        assert isinstance(league, League)
    # Assert that 5 league objects are returned
    assert len(leagues_response) == 5

def test_bulk_player_file_parquet():
    """Tests bulk player download through SDK - Parquet"""

    config = SWCConfig(swc_base_url="http://0.0.0.0:8000", bulk_file_format = "parquet")
    client = SWCClient(config)

    player_file_parquet = client.get_bulk_player_file()

    # Assert the file has the correct number of records (including header)
    player_table = pq.read_table(BytesIO(player_file_parquet))
    player_df = player_table.to_pandas()
    assert len(player_df) == 1018 # 1 header + 1017 records
    
def test_list_teams():
    """Tests get teams from SDK"""
    config = SWCConfig(swc_base_url="http://0.0.0.0:8000", backoff=False)
    client = SWCClient(config)
    teams_response = client.list_teams(limit=5)
    # Assert the endpoint returned a list object
    assert isinstance(teams_response, list)
    # Assert each item in the list is an instance of a Pydantic Team object
    for team in teams_response:
        assert isinstance(team, Team)
    # Assert that 5 team objects are returned
    assert len(teams_response) == 5
    
def test_list_players():
    """Tests get players from SDK"""
    config = SWCConfig(swc_base_url="http://0.0.0.0:8000", backoff=False)
    client = SWCClient(config)
    players_response = client.list_players(limit=5)
    # Assert the endpoint returned a list object
    assert isinstance(players_response, list)
    # Assert each item in the list is an instance of a Pydantic Player object
    for player in players_response:
        assert isinstance(player, Player)
    # Assert that 5 player objects are returned
    assert len(players_response) == 5
    
def test_list_performances():
    """Tests get performances from SDK"""
    config = SWCConfig(swc_base_url="http://0.0.0.0:8000", backoff=False)
    client = SWCClient(config)
    performances_response = client.list_performances(limit=5)
    # Assert the endpoint returned a list object
    assert isinstance(performances_response, list)
    # Assert each item in the list is an instance of a Pydantic Performance object
    for performance in performances_response:
        assert isinstance(performance, Performance)
    # Assert that 5 performance objects are returned
    assert len(performances_response) == 5