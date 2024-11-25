from discordrp import Presence
import time

def discord_connect(show, episode):
    client_id = '1292070065583165512'

    with Presence(client_id) as presence:
        presence.set(
            {
                "type": 3,
                "details": show,
                "state": "Watching episode "+episode,
            }
        )
        while True:
            time.sleep(15)