import requests
import urllib
from .constants import TEXT_BOLD, TEXT_NEWLINE


def format_message(app, msg):
    return msg.format(**
        {"bold_open": TEXT_BOLD['open'][app],
        "bold_close": TEXT_BOLD['close'][app],
        "newline":TEXT_NEWLINE[app]}
    )

