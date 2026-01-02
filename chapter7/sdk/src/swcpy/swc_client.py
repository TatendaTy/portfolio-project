"""
SportsWorldCentral API Client Module

This module provides the main client class for interacting with the SWC Fantasy Football API.
It handles HTTP requests, retry logic, and data validation for all API endpoints.
"""

import httpx  # HTTP client library for making API requests
import swcpy.swc_config as config  # Configuration module for client settings
from .schemas import League, Team, Player, Performance  # Pydantic models for data validation
from typing import List  # Type hints for better code clarity
import backoff  # Exponential backoff decorator for retrying failed requests
import logging  # Logging functionality for debugging and monitoring

# Initialize logger for this module to track client operations
logger = logging.getLogger(__name__)

class SWCClient:
    """Interacts with the SportsWorldCentral API.

        This SDK class simplifies the process of using the SWC Fantasy Football API.
        It supports all the functions of the SWC API and returns validated data types.
    
    Typical usage example:

        client = SWCClient()
        response = client.get_health_check()
    """

    # API Endpoint Constants
    # These define the URL paths for each API endpoint relative to the base URL
    HEALTH_CHECK_ENDPOINT = "/"  # Verify API is running
    LIST_LEAGUES_ENDPOINT = "/v0/leagues/"  # Get all leagues
    LIST_PLAYERS_ENDPOINT = "/v0/players/"  # Get all players
    LIST_PERFORMANCES_ENDPOINT = "/v0/performances/"  # Get player performance stats
    LIST_TEAMS_ENDPOINT = "/v0/teams/"  # Get all teams
    GET_COUNTS_ENDPOINT = "/v0/counts/"  # Get record counts for all entities

    # Base URL for bulk data files hosted on GitHub
    # These files contain CSV/Parquet exports of the database for bulk operations
    BULK_FILE_BASE_URL = (
        "https://raw.githubusercontent.com/46075417"
        + "/portfolio-project/main/bulk/"
    ) # Replace [github_id] with your GitHub ID 

    def __init__(self, input_config: config.SWCConfig):
        """Class constructor that sets variables from configuration object.
        
        Initializes the SWC client with configuration settings including base URL,
        retry behavior, and bulk file format preferences.
        
        Args:
            input_config: SWCConfig object containing all client configuration settings
        """

        # Log the bulk file URL for debugging purposes
        logger.debug(f"Bulk file base URL: {self.BULK_FILE_BASE_URL}")

        # Log the incoming configuration for troubleshooting
        logger.debug(f"Input config: {input_config}")

        # Extract configuration values from the input config object
        self.swc_base_url = input_config.swc_base_url  # Base URL of the SWC API
        self.backoff = input_config.swc_backoff  # Whether to enable retry logic
        self.backoff_max_time = input_config.swc_backoff_max_time  # Maximum retry duration
        self.bulk_file_format = input_config.swc_bulk_file_format  # File format (CSV/Parquet)

        # Dictionary mapping entity types to their bulk file names (without extension)
        # This allows easy reference to bulk data files for each entity type
        self.BULK_FILE_NAMES = {
            "players": "player_data",
            "leagues": "league_data",
            "performances": "performance_data",
            "teams": "team_data",
            "team_players": "team_player_data",
        }

        # Configure retry/backoff behavior if enabled
        if self.backoff:
            # Apply exponential backoff decorator to the call_api method
            # This automatically retries failed HTTP requests with increasing delays
            # Handles both network errors (RequestError) and HTTP errors (HTTPStatusError)
            self.get_url = backoff.on_exception(
                # replace self.call_api with self.get_url
                wait_gen=backoff.expo,  # Exponential wait time between retries
                exception=(httpx.RequestError, httpx.HTTPStatusError),  # Exceptions to catch
                max_time=self.backoff_max_time,  # Maximum total time to spend retrying
                jitter=backoff.random_jitter,  # Add randomness to prevent thundering herd
            )(self.call_api)

        # Add file extensions to bulk file names based on configured format
        if self.bulk_file_format.lower() == "parquet":
            # Use Parquet format for better compression and faster reads
            self.BULK_FILE_NAMES = {
                key: value + ".parquet" for key, value in
                self.BULK_FILE_NAMES.items()
            }
        else:
            # Default to CSV format for better compatibility
            self.BULK_FILE_NAMES = {
                key: value + ".csv" for key, value in
                self.BULK_FILE_NAMES.items()
            }

        # Log the final bulk file names dictionary for verification
        logger.debug(f"Bulk file dictionary: {self.BULK_FILE_NAMES}")

    def call_api(self,
            api_endpoint: str,
            api_params: dict = None        
    ) -> httpx.Response:
    """Makes API Call and logs errors for each SDK function."""

    if api_params:
        api_params = {key: val for key, val in api_params.items() if val is not None}

    try:
        with httpx.Client(base_url=self.swc_base_url) as client:
            logger.debug(f"base_url: {self.swc_base_url}, api_endpoint: {api_endpoint}, api_params: {api_params}")
            response = client.get(api_endpoint, params=api_params)
            logger.debug(f"Response JSON: {response.json()}")
            return response
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP status error occurred: {e.response.status_code} {e.response.text}")
        raise
    except httpx.RequestError as e:
        logger.error(f"Request error occurred: {str(e)}")
        raise



        