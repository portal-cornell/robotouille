

class RobotouilleClient:
    def run_client(environment_name: str, seed: int, noisy_randomization: bool, movement_mode: str, host: str="ws://localhost:8765"):
        """
        Initialize the client configuration and runtime state.

        Args:
            environment_name (str): Name of the Robotouille environment.
            seed (int): Random seed for environment initialization.
            noisy_randomization (bool): Whether to enable noisy randomization.
            movement_mode (str): Movement mode for the agent.
            host (str): WebSocket URI of the server.
        """
        pass
    
    async def run(self):
        """
        Orchestrate the client lifecycle: connect,
        then concurrently run send_actions and receive_responses.
        """
        pass

    async def cleanup(self):
        """
        Clean up resources: close WebSocket, quit pygame, etc.
        """
        pass

    async def connect(self):
        """
        Establish WebSocket connection to the server, called once at the start.
        This method handles the initial connection and setup of the client.
        """
        pass

    async def send_connect(self):
        """
        Send a CONNECT message to register this client to a lobby in the server.
        """
        pass

    async def send_disconnect(self):
        """
        Notify the server that this client is disconnecting, and close the WebSocket.
        """
        pass

    async def send_post_status(self, choice: str):
        """
        Send a POST_STATUS message indicating whether the player wants to play 
        again or quit.

        Args:
            choice (str): Either 'PLAY_AGAIN' or 'QUIT'.
        """
        pass

    async def send_actions(self):
        """
        Main loop: poll pygame events, translate them into
        game actions, encode (pickle/base64) and send to server.
        """
        pass

    async def receive_responses(self):
        """
        Main loop: receive JSON-encoded messages from server,
        decode and dispatch to the appropriate handler.
        """
        pass

    async def _handle_opening_message(self, raw_message: str):
        """
        Handle the initial server message (e.g., assigning player index)
        before the game starts.

        Args:
            raw_message (str): JSON text from the server.
        """
        pass

    async def _handle_message(self, data: dict):
        """
        Dispatch incoming server messages based on their type
        field to the corresponding on_* handler.

        Args:
            data (dict): Parsed JSON payload with 'type' and 'payload'.
        """
        pass

    
    
    # Event handlers for different message types

    def on_player_list(self, payload: dict):
        """
        Handle a PLAYER_LIST update: update local lobby player list.

        Args:
            payload (dict): Contains list of players and statuses.
        """
        pass

    def on_start_game(self):
        """
        Handle START_GAME: switch from lobby to game screen,
        initialize player assignment.
        """
        pass

    def on_game_state(self, payload: dict):
        """
        Handle GAME_STATE: update local environment state and render.

        Args:
            payload (dict): Contains serialized env, obs, players, done flag.
        """
        pass

    def on_game_ended(self):
        """
        Handle GAME_ENDED: close game loop and transition to results screen.
        """
        pass

    def on_player_status(self, payload: dict):
        """
        Handle PLAYER_STATUS: update statuses on results screen.

        Args:
            payload (dict): Contains list of player statuses.
        """
        pass

    def on_results(self, payload: dict):
        """
        Handle RESULTS: display final scores and stars for each player.

        Args:
            payload (dict): Contains list of results records.
        """
        pass

    def on_restart(self):
        """
        Handle RESTART: reset local state and return to the game screen.
        """
        pass

    def on_auto_matchmaking(self):
        """
        Handle AUTO_MATCHMAKING: return player to lobby/matchmaking screen.
        """
        pass

   
