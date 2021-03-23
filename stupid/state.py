from logbook import Logger
from typing import Any
import redis

log = Logger(__name__)

class StupidStateStore:
  """
  General wrapper because redis is 
  kinda stupid and doesn't have defaults
  """

  def __init__(self):
    self._redis = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
  
  def get(self, token: str, default=None) -> Any:
    log.debug("getting value for token: {}", token)

    v = self._redis.get(f"ss_store:{token}") or default
    
    log.debug("found value: {}", v)
    log.debug("returning value")
    return v
  
  def set(self, token: str, value: Any):
    log.debug("setting value: {}", value)
    log.debug("for token: {}", token)
    self._redis.set(f"ss_store:{token}", value)
