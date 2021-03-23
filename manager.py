from logbook import Logger
from quart import Quart, json, jsonify, request
from stupid.state import StupidStateStore
from stupid.errors import StupidError, MissingStupidValue, MalformedStupidType

log = Logger(__name__)
app = Quart(__name__)
store = StupidStateStore()

@app.route("/state/<key>", methods=["GET"])
async def get_state_value_by_key(key: str):
  log.debug("requested state value with key: {}", key)

  return jsonify({
    "key": key,
    "value": store.get(key)
  })

@app.route("/state/<key>", methods=["POST", "PATCH", "PUT"])
async def set_state_value_by_key(key: str):
  j = await request.get_json()

  if not j["value"]:
    log.debug("requested state set with key: {} but is missing value", key)
    raise MissingStupidValue()
  
  log.debug("requested state set with key: {} and value: {}", key, j["value"])

  store.set(key, j["value"])
  
  return jsonify({
    "key": key,
    "value": store.get(key)
  })

@app.route("/state", methods=["GET"])
async def get_state_values_with_keys():
  j = await request.get_json()

  karr = isinstance(j["keys"], list) and all(isinstance(key, str) for key in j["keys"])

  if not karr:
    log.debug("requested multiple state key get with malformed key list")
    raise MalformedStupidType()
  
  log.debug("requested multiple state key get with keys: {}", ", ".join(j["keys"]))

  return jsonify(
    [{
      "key": k,
      "value": store.get(k)
    } for k in j["keys"]]
  )

@app.route("/state", methods=["POST", "PATCH", "PUT"])
async def set_state_values_with_keys():
  j = await request.get_json()

  karr = isinstance(j["keys"], list) and all(isinstance(key, str) for key in j["keys"])
  varr = isinstance(j["values"], list) and all(isinstance(value, str) for value in j["values"])

  if not karr or not varr or not ( len(j["keys"]) == len(j["values"]) ):
    log.debug("requested multiple state key set with malformed value")
    raise MalformedStupidType()
  
  log.debug("requested multiple state key set with keys: {}", ", ".join(j["keys"]))

  for k, v in zip(j["keys"], j["values"]):
    store.set(k, v)
  
  return jsonify(
    [{
      "key": k,
      "value": store.get(k)
    } for k in j["keys"]]
  )

@app.errorhandler(404)
async def handle_404(_err):
  return (
    jsonify({"message": "404: Not Found", "code": 0}),
    404
  )

@app.errorhandler(405)
async def handle_405(_err):
  return (
    jsonify({"message": "405: Method Not Allowed", "code": 0}),
    405
  )

@app.errorhandler(500)
async def handle_500(err):
  return (
    jsonify({"message": repr(err), "code": 0, "internal": True}),
    500
  )

@app.errorhandler(StupidError)
async def handle_stupid_error(err: StupidError):
  try:
    ejson = err.json
  except IndexError:
    ejson = {}
  
  try:
    ejson["code"] = err.error_code
  except AttributeError:
    ejson["code"] = 0
  
  return (
    jsonify(
      { "message": err.message, **ejson }
    ),
    err.status_code
  )
