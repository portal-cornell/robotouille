from typing import Dict, Any

import networking.server as robotouille_server
import networking.client as robotouille_client
import networking.utils.single_player as robotouille_single_player
import networking.utils.replay as robotouille_replay
import networking.utils.render as robotouille_render

def run_networking(environment_name: str, role: str, seed: int, noisy_randomization: bool, movement_mode: str, host: str, display_server: bool, recording: str):
    """Runs the provided Robotouille environment with the given role.

    Parameters:
        environment_name (str):
            The name of the environment to run.
            Find environment names under environments/env_generator/examples
        - role (str):
            The network role.
            "server" to run the server.
            "client" to run the client.
            "single" to run the server and client for a single-player game.
            "replay" to replay a recording.
            "render" to render a recording into a video.
        
        Optional parameters to run Robotouille with including:
            - seed (int):
                The seed for the environment.
            - noisy_randomization (bool):
                Whether to use noisy randomization.
                See environments/env_generator/README.md for more information.
            - movement_mode (str):
                The movement mode to use.
        Optional Network Parameters:
            - host (str):
                The host to connect to.
            - display_server (bool):
                Whether to display the server.
            - recording (str):
                The recording to replay.
            
    
    Returns:
        done (bool):
            Whether the environment is done.
        steps (int):
            The number of steps taken in the environment.
    """
    # We assume that if a recording is provided, then the user would like to replay it
    movement_mode = "traverse"
    if recording != "" and role != "replay" and role != "render":
        role = "replay"

    if role == "server":
        robotouille_server.run_server(environment_name, seed, noisy_randomization, movement_mode, display_server)
    elif role == "client":
        robotouille_client.run_client(environment_name, seed, noisy_randomization, movement_mode, host)
    elif role == "single":
        robotouille_single_player.run_single(environment_name, seed, noisy_randomization, movement_mode)
    elif role == "replay":
        robotouille_replay.run_replay(recording)
    elif role == "render":
        robotouille_render.run_render(recording)
    else:
        print("Invalid role:", role)