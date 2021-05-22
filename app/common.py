import errno
import os

from flask import current_app
from flask_login import current_user


def folder_path():
    directory = os.path.join(
        current_app.root_path, current_app.config["UPLOAD_PATH"], current_user.get_id()
    )
    return directory


def file_path(file_name):
    if file_name is None:
        return None
    else:
        return os.path.join(folder_path(), file_name)


def silentremove(filename):
    try:
        os.remove(filename)
    except OSError as error:
        if error.errno != errno.ENOENT:
            raise
