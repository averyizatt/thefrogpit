# redis_subscriber_agent.py
# Subscribes to the 'agents' Redis pub/sub channel and logs incoming messages.
# Useful for cross-agent event signalling on the local network.

import redis

from status_logger import log_status

REDIS_HOST = "localhost"
REDIS_PORT = 6379
CHANNEL = "agents"
AGENT = "RedisEventSubscriber"


def listen_once() -> None:
    """Connect to Redis, wait for one message on the agents channel, then exit."""
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
    pubsub = r.pubsub()
    pubsub.subscribe(CHANNEL)

    for msg in pubsub.listen():
        if msg["type"] == "message":
            content = msg["data"].decode()
            log_status(AGENT, "MESSAGE", content)
            break


if __name__ == "__main__":
    listen_once()
