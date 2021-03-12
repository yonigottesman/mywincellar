import errno
import os


def silentremove(filename):
    try:
        os.remove(filename)
    except OSError as error:
        if error.errno != errno.ENOENT:
            raise
