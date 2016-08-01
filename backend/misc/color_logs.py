import os
import coloredlogs

def color_logs():
    os.environ["COLOREDLOGS_LOG_FORMAT"]='[%(name)s] %(asctime)s - %(message)s'
    os.environ["COLOREDLOGS_DATE_FORMAT"]='%H:%M:%S'
    os.environ["COLOREDLOGS_LEVEL_STYLES"]='debug=green;warning=yellow;error=red;critical=red,bold'
    coloredlogs.install(level='DEBUG')