class StupidError(Exception):
  status_code = 500

  def _get_err_msg(self, err_code: int) -> str:
    ERR_MSG_MAP = {
      0: "Unknown Error",
      10001: "Missing Value",
      10002: "Malformed Type"
    }

    if err_code is not None:
      return ERR_MSG_MAP.get(err_code) or self.args[0]

    return repr(self)
  
  @property
  def message(self) -> str:
    try:
      msg = self.args[0]

      if isinstance(msg, int):
        return self._get_err_msg(msg)
      
      return msg
    except IndexError:
      return self._get_err_msg(getattr(self, "error_code", None))
  
  @property
  def json(self):
    return self.args[1]


class BadStupidRequest(StupidError):
  status_code = 400

class MissingStupidValue(BadStupidRequest):
  error_code  = 10001

class MalformedStupidType(BadStupidRequest):
  error_code = 10002
