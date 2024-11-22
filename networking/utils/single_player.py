import threading
import time
import asyncio
import networking.server as robotouille_server
import networking.client as robotouille_client

def run_single(environment_name: str, seed: int, noisy_randomization: bool, movement_mode: str):
    event = threading.Event()
    
    server_thread = threading.Thread(
        target=run_server_in_loop,
        args=(environment_name, seed, noisy_randomization, movement_mode, event)
    )
    
    client_thread = threading.Thread(
        target=run_client_in_loop,
        args=(environment_name, seed, noisy_randomization, movement_mode)
    )
    
    server_thread.start()
    time.sleep(0.5)  # wait for server to initialize
    
    client_thread.start()
    
    client_thread.join()
    
    event.set()
    server_thread.join()

def run_server_in_loop(environment_name: str, seed: int, noisy_randomization: bool, movement_mode: str, event: threading.Event):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async_event = asyncio.Event()
    
    def set_async_event():
        loop.call_soon_threadsafe(async_event.set)
    
    # Watch the threading event
    def check_thread_event():
        if event.is_set():
            set_async_event()
        else:
            loop.call_later(0.1, check_thread_event)
    
    loop.call_soon(check_thread_event)
    
    loop.run_until_complete(
        robotouille_server.server_loop(
            environment_name=environment_name,
            seed=seed,
            noisy_randomization=noisy_randomization,
            movement_mode=movement_mode,
            display_server=False,
            event=async_event
        )
    )
    loop.close()

def run_client_in_loop(environment_name: str, seed: int, noisy_randomization: bool, movement_mode: str):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    loop.run_until_complete(
        robotouille_client.client_loop(
            environment_name=environment_name,
            seed=seed,
            noisy_randomization=noisy_randomization,
            movement_mode=movement_mode
        )
    )
    loop.close()