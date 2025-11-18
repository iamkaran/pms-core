import logging
import sys

# logging.basicConfig(# filename="newfile.log",
#                     format='%(asctime)s %(message)s'
#                     # filemode="w"
#                     )

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter(
    fmt="%(asctime)s %(filename)s:%(lineno)d [+] %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S.000'))
logger.addHandler(stream_handler)

# Blocking of logger:
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)