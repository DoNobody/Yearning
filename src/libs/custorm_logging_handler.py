import logging 
from libs import util
from django.conf import settings

class DingdingErrorHandler(logging.StreamHandler):
    """
    A handler class which allows the cursor to stay on
    one line for selected messages
    """
    on_same_line = False
    def emit(self, record):
        try:
            msg = self.format(record)
            if hasattr(settings, "DINGDING_ERROR_URL"):
                dingding_error_url = settings.DINGDING_ERROR_URL
                if dingding_error_url:
                    util.dingding(msg, dingding_error_url)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)