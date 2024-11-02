import asyncio
import networking.server as robotouille_server
import networking.client as robotouille_client

def run_single(environment_name: str, seed: int=42, noisy_randomization: bool=False, movement_mode: str='traverse'):
    asyncio.run(single_player(environment_name, seed, noisy_randomization, movement_mode))

async def single_player(environment_name: str, seed: int=42, noisy_randomization: bool=False, bool=False, movement_mode: str='traverse'):
    event = asyncio.Event()
    server = asyncio.create_task(robotouille_server.server_loop(environment_name=environment_name, seed=seed, noisy_randomization=noisy_randomization, movement_mode=movement_mode, event=event))
    await asyncio.sleep(0.5)  # wait for server to initialize
    client = asyncio.create_task(robotouille_client.client_loop(environment_name=environment_name, seed=seed, noisy_randomization=noisy_randomization, movement_mode=movement_mode))
    await client
    event.set()
    await server
