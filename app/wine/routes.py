import imghdr
import os
import uuid
from io import BytesIO

import pyheif
from flask import (
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    send_from_directory,
    url_for,
)
from flask_login import current_user, login_required
from PIL import Image
from sqlalchemy import desc
from werkzeug.utils import secure_filename

from app import db
from app.common import file_path, folder_path, silentremove
from app.models import Wine
from app.wine import bp
from app.wine.forms import EditWineForm, WineForm


def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    file_format = imghdr.what(None, header)
    if not file_format:
        return None
    return "." + (file_format if file_format != "jpeg" else "jpg")


def valid_file(uploaded_file):
    filename = secure_filename(uploaded_file.filename)
    file_ext = os.path.splitext(filename)[1]
    if file_ext not in current_app.config["UPLOAD_EXTENSIONS"]:
        return False
    return True


def store_file(uploaded_file):

    filename = secure_filename(uploaded_file.filename)
    directory = folder_path()
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_bytes = BytesIO(uploaded_file.read())
    if os.path.splitext(filename)[1] == ".HEIC":
        heif_file = pyheif.read(file_bytes)
        image = Image.frombytes(
            heif_file.mode,
            heif_file.size,
            heif_file.data,
            "raw",
            heif_file.mode,
            heif_file.stride,
        )
    else:
        image = Image.open(file_bytes)
    newfilename = f"{uuid.uuid1()}.jpg"
    image.convert("RGB").save(
        file_path(newfilename), format="JPEG", optimize=True, quality=10
    )
    return newfilename


@bp.route("/", methods=["GET", "POST"])
@bp.route("/index", methods=["GET", "POST"])
@login_required
def index():
    form = WineForm()
    if form.validate_on_submit():
        if form.image.data is not None and not valid_file(form.image.data):
            flash("Image Error!", "alert-danger")
            return redirect(url_for("wine.index"))
        wine = Wine(
            body=form.description.data, author=current_user, rating=form.rating.data
        )
        if form.image.data is not None:
            wine.file_name = store_file(form.image.data)

        db.session.add(wine)
        db.session.commit()
        flash("Added new wine!", "alert-info")
        return redirect(url_for("wine.index"))

    return render_template(
        "wine/index.html",
        form=form,
        wines=current_user.wines.order_by(desc(Wine.timestamp)).all(),
        wines_active_status="active",
    )


@bp.route("/uploads/<wine_id>")
@login_required
def upload(wine_id):
    wine = current_user.wines.filter_by(id=wine_id).first()
    if not wine:
        abort(404)
    return send_from_directory(folder_path(), wine.file_name)


@bp.route("/wines/<wine_id>", methods=["GET", "POST"])
@login_required
def edit_wine(wine_id):
    wine = current_user.wines.filter_by(id=wine_id).first()
    if not wine:
        abort(404)

    form = EditWineForm(rating=wine.rating, description=wine.body)
    if form.validate_on_submit():
        if form.image.data is not None and not valid_file(form.image.data):
            flash("Image Error!", "alert-danger")
            return redirect(url_for("wine.edit_wine", wine_id=wine_id))
        if form.delete.data:
            db.session.delete(wine)
        else:
            wine.body = form.description.data
            wine.rating = form.rating.data
            if form.image.data is not None:
                silentremove(file_path(wine.file_name))
                wine.file_name = store_file(form.image.data)
            if form.delete_image.data and wine.file_name:
                silentremove(file_path(wine.file_name))
                wine.file_name = None

        db.session.commit()
        flash("Edit Done!", "alert-info")
        return redirect(url_for("wine.index"))
    return render_template(
        "wine/edit_wine.html", form=form, wines_active_status="active"
    )
