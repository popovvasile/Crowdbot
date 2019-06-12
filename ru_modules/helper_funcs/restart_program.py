import os
import sys
from ru_modules.helper_funcs.helper import get_help


def restart_program(bot, update):
    # """Restarts the current program, with file objects and descriptors
    #    cleanup
    # """
    #
    # try:
    #     p = psutil.Process(os.getpid())
    #     for handler in p.get_open_files() + p.connections():
    #         os.close(handler.fd)
    # except Exception as e:
    #     logging.error(e)
    get_help(bot, update)

    python = sys.executable
    os.execl(python, python, *sys.argv)

