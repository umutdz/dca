import redis

from app.core.config import config


class CacheService:
    def __init__(self) -> None:
        self.client = redis.StrictRedis.from_url(
            config.REDIS_URL,
            decode_responses=True,
        )
        self.prefix = config.REDIS_PREFIX

    def _add_prefix(self, key) -> str:
        """
        Add prefix to the key.

        :param key: The original key.
        :return: The key with prefix.
        """
        return f"{self.prefix}{key}"

    def set(self, key, value, ex=None) -> None:
        """
        Set a key-value pair in the cache with an optional expiration time.

        :param key: The key to set.
        :param value: The value to set.
        :param ex: Expiration time in seconds.
        """
        prefixed_key = self._add_prefix(key)
        self.client.set(name=prefixed_key, value=value, ex=ex)

    def get(self, key) -> str:
        """
        Get the value of a key from the cache.

        :param key: The key to retrieve.
        :return: The value of the key, or None if the key does not exist.
        """
        prefixed_key = self._add_prefix(key)
        return self.client.get(name=prefixed_key)

    def delete(self, key) -> int:
        """
        Delete a key from the cache.

        :param key: The key to delete.
        :return: The number of keys that were removed.
        """
        prefixed_key = self._add_prefix(key)
        return self.client.delete(prefixed_key)

    def update(self, key, value, ex=None) -> None:
        """
        Update the value of an existing key in the cache.

        :param key: The key to update.
        :param value: The new value.
        :param ex: Expiration time in seconds.
        """
        prefixed_key = self._add_prefix(key)
        if self.client.exists(prefixed_key):
            self.client.set(name=prefixed_key, value=value, ex=ex)
        else:
            raise KeyError(f"Key '{key}' does not exist in cache.")

    def exists(self, key) -> bool:
        """
        Check if a key exists in the cache.

        :param key: The key to check.
        :return: True if the key exists, False otherwise.
        """
        prefixed_key = self._add_prefix(key)
        return self.client.exists(prefixed_key)

    def clear(self) -> None:
        """
        Clear all keys from the cache.
        """
        self.client.flushall()
