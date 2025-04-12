import threading
import time
import asyncio
import networking.server as robotouille_server
import networking.client as robotouille_client
import multiprocessing

def launch_server(environment_name, seed, noisy_randomization, movement_mode, event):
    robotouille_server.run_server(
        environment_name=environment_name,
        seed=seed,
        noisy_randomization=noisy_randomization,
        movement_mode=movement_mode,
        display_server=False,
        event=event  # multiprocessing.Event
    )

def run_single(environment_name: str, seed: int, noisy_randomization: bool, movement_mode: str):    
    server_ready = multiprocessing.Event()

    server_process = multiprocessing.Process(
        target=launch_server,
        args=(environment_name, seed, noisy_randomization, movement_mode, server_ready)
    )
    server_process.start()

    server_ready.wait()

    try:
        robotouille_client.run_client(
            environment_name=environment_name,
            seed=seed,
            noisy_randomization=noisy_randomization,
            movement_mode=movement_mode
        )
    finally:
        server_process.terminate()
        server_process.join()

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