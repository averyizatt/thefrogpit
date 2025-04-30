# redis_subscriber_agent.py
import redis
from status_logger import log_status

r = redis.Redis(host='localhost', port=6379)
pubsub = r.pubsub()
pubsub.subscribe('agents')

for msg in pubsub.listen():
    if msg['type'] == 'message':
        content = msg['data'].decode()
        log_status("RedisEventSubscriber", "MESSAGE", content)
        break
