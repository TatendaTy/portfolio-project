"""
SportsWorldCentral API Client Module

This module provides the main client class for interacting with the SWC Fantasy Football API.
It handles HTTP requests, retry logic, and data validation for all API endpoints.
"""

import httpx  # HTTP client library for making API requests
import swcpy.swc_config as config  # Configuration module for client settings
from .schemas import League, Team, Player, Performance, Counts  # Pydantic models for data validation
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
        "https://raw.githubusercontent.com/TatendaTy"
        + "/portfolio-project/main/bulk/"
    ) 

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
                # replaced self.call_api with self.get_url
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

    def call_api(self, api_endpoint: str, api_params: dict = None) -> httpx.Response:
        """Makes API Call and logs errors for each SDK function."""

        if api_params:
            api_params = {key: val for key, val in api_params.items() if val is not None}

        try:
            # Set a longer timeout for Render's free tier which can take time to wake up
            timeout = httpx.Timeout(60.0, connect=60.0)
            with httpx.Client(base_url=self.swc_base_url, timeout=timeout) as client:
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

    # API endpoint methods

    def get_health_check(self) -> httpx.Response:
        """Checks if API is running and healthy.
        
        Calls the API health check endpoint and returns a standard message if the API is running normally.
        Can be used to check status of API before making more complicated API calls.

        Returns:
            An httpx.Response object that contains the HTTP status , JSON response and other information received
            from the API.
        """
        logger.debug("Entered health check")
        endpoint_url = self.HEALTH_CHECK_ENDPOINT
        return self.call_api(endpoint_url)
    
    def list_leagues(self, skip: int = 0,
        limit: int = 100,
        minimun_last_changed_date: str = None,
        league_name: str = None,
    ) -> List[League]:
        """Returns a List of Leagues filtered by parameters.
        
        Calls the API v0/leagues endpoint and returns a list of League objects.
        
        Returns:
        A List of schemas.League objects. Each represents one
        SportsWorldCentral fantasy league.
        """
        logger.debug("Entered list leagues")

        params = {
            "skip": skip,
            "limit": limit,
            "minimun_last_changed_date": minimun_last_changed_date,
            "league_name": league_name,
        }

        response = self.call_api(self.LIST_LEAGUES_ENDPOINT, params) # call the call_api method and pass in the query strings parameters as a dict
        return [League(**league) for league in response.json()] # parse the response JSON into a list of League objects using list comprehension

    """
    The general formula for each endpoint is:

    1. Define the method arguments to match the API's accepted query parameters (e.g., skip, limit, minimum_last_changed_date, etc.).
    2. Put these arguments into a params dictionary.
    3. Pass params and the endpoint URL (like self.LIST_TEAMS_ENDPOINT) inside self.call_api().
    4. Parse the returned JSON response using a list comprehension and the Pydantic models from schemas.py.
    """
    
    def get_league_by_id(self, league_id: int) -> League:
        """Returns a single League by its ID.
        
        Calls the API v0/leagues/{league_id} endpoint and returns a League object.
        This endpoint retrieves one specific league using its unique identifier.
        
        Args:
            league_id: The unique identifier for the league
            
        Returns:
            A schemas.League object representing the requested league
            
        Raises:
            httpx.HTTPStatusError: If league not found (404) or other HTTP error
        """
        logger.debug(f"Getting league with ID: {league_id}")
        
        endpoint_url = f"/v0/leagues/{league_id}"
        response = self.call_api(endpoint_url)
        
        return League(**response.json())

    def get_counts(self) -> Counts:
        """Returns counts of records for all entities in the API.
        
        Calls the API v0/counts endpoint and returns a Counts object

        """
        logger.debug("Entered get counts")
        response = self.call_api(self.GET_COUNTS_ENDPOINT)
        return Counts(**response.json())

    def list_teams(self, skip: int = 0,
            limit: int = 100,
            minimun_last_changed_date: str = None,
            team_name: str = None,
            league_id: int = None,
            ) -> List[Team]:
        """
        Returns a list of Teams filtered by parameters.
        
        Calls the API v0/teams endpoint and returns a list of Team objects.
        
        Returns:
        A List of schemas.Team objects. Each represents one SportsWorldCentral fantasy team.
        """
        logger.debug("Entered list teams")
        
        params = {
            "skip": skip,
            "limit": limit,
            "minimun_last_changed_date": minimun_last_changed_date,
            "team_name": team_name,
            "league_id": league_id,
        }
        
        # return the response from call_api and parse it into a list of Team objects using list comprehension
        response = self.call_api(self.LIST_TEAMS_ENDPOINT, params)
        return [Team(**team) for team in response.json()]

    def list_players(
        self,
        skip: int = 0,
        limit: int = 100,
        minimum_last_changed_date: str = None,
        first_name: str = None,
        last_name: str = None,
        position: str = None,
    ) -> List[Player]:
        """Returns a list of Players filtered by parameters.
        
        Calls the API v0/players endpoint and returns a list of Player objects.
        
        Returns:
        A List of schemas.Player objects. Each represents one SportsWorldCentral fantasy player.
        """
        logger.debug("Entered list players")

        params = {
            "skip": skip,
            "limit": limit,
            "minimum_last_changed_date": minimum_last_changed_date,
            "first_name": first_name,
            "last_name": last_name,
            "position": position,
        }
        
        response = self.call_api(self.LIST_PLAYERS_ENDPOINT, params)
        return [Player(**player) for player in response.json()]

    def get_player_id(self, player_id: int) -> int:
        """Returns a player's ID given their full name.
        
        This is a helper function that calls list_players and matches the full name to return the player ID.
        It can be used when you only have the player's name but need their ID for other API calls.

        Args:
            player_name: The full name of the player (e.g., "Tom Brady")
        
        Returns:
            The unique player_id corresponding to the given player name
            
        Raises:
            ValueError: If no player with the given name is found
        """
        logger.debug(f"Getting player ID")
        
        # build URL
        endpoint_url = f'{self.LIST_PLAYERS_ENDPOINT}{player_id}'
        # make the API call
        response = self.call_api(endpoint_url)
        responsePlayer = Player(**response.json())
        return responsePlayer

    def list_performances(
        self,
        skip: int = 0,
        limit: int = 100,
        minimum_last_changed_date: str = None,
    ) -> List[Performance]:
        '''
        Returns a list of Performances filtered by parameters.
        '''
        logger.debug("Entered list performances")
        
        params = {
            "skip": skip,
            "limit": limit,
            "minimum_last_changed_date": minimum_last_changed_date,
        }
        
        response = self.call_api(self.LIST_PERFORMANCES_ENDPOINT, params)
        return [Performance(**performance) for performance in response.json()]
        

    # bulk download endpoints

    def get_bulk_player_file(self) -> bytes:
        """Returns a bulk file with player data"""
        logger.debug("Entered get bulk player file")
        player_file_path = self.BULK_FILE_BASE_URL + self.BULK_FILE_NAMES["players"]
        response = httpx.get(player_file_path, follow_redirects=True)
        if response.status_code == 200:
            logger.debug("File downloaded successfully")
            return response.content

    def get_bulk_league_file(self) -> bytes:
        """Returns a CSV file with league data"""
        logger.debug("Entered get bulk league file")
        league_file_path = self.BULK_FILE_BASE_URL + self.BULK_FILE_NAMES["leagues"]
        response = httpx.get(league_file_path, follow_redirects=True)
        if response.status_code == 200:
            logger.debug("File downloaded successfully")
            return response.content

    def get_bulk_performance_file(self) -> bytes:
        """Returns a CSV file with performance data"""
        logger.debug("Entered get bulk performance file")
        performance_file_path = self.BULK_FILE_BASE_URL + self.BULK_FILE_NAMES["performances"]
        response = httpx.get(performance_file_path, follow_redirects=True)
        if response.status_code == 200:
            logger.debug("File downloaded successfully")
            return response.content
    
    def get_bulk_team_file(self) -> bytes:
        """Returns a CSV file with team data"""
        logger.debug("Entered get bulk team file")
        team_file_path = self.BULK_FILE_BASE_URL + self.BULK_FILE_NAMES["teams"]
        response = httpx.get(team_file_path, follow_redirects=True)
        if response.status_code == 200:
            logger.debug("File downloaded successfully")
            return response.content

    def get_bulk_team_player_file(self) -> bytes:
        """Returns a CSV file with team player data"""
        logger.debug("Entered get bulk team player file")
        team_player_file_path = self.BULK_FILE_BASE_URL + self.BULK_FILE_NAMES["team_players"]
        response = httpx.get(team_player_file_path, follow_redirects=True)
        if response.status_code == 200:
            logger.debug("File downloaded successfully")
            return response.content

        

    


        