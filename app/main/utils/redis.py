import redis


def setup_redis():
    return redis.Redis(
        host='redis',
        port=6379,
    )
