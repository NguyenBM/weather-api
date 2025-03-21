"""Basic connection example.
"""

import redis

r = redis.Redis(
    host='redis-19809.c91.us-east-1-3.ec2.redns.redis-cloud.com',
    port=19809,
    decode_responses=True,
    username="default",
    password="nH3aMaeDnuSrrnm4xStRObevbOzxzE35",
)

success = r.set('foo', 'bar')
# True

result = r.get('foo')
print(result)
# >>> bar

