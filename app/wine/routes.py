from flask import render_template, flash, redirect, url_for, request, abort, current_app ,send_from_directory
from flask_login import current_user, login_required
from app import db
from app.wine.forms import WineForm, EditWineForm
from app.models import Wine
from app.wine import bp
from werkzeug.utils import secure_filename
import os
import imghdr
from PIL import Image
from io import BytesIO
from sqlalchemy import desc
from app.common import silentremove

def validate_image(stream):
    header = stream.read(512)
    stream.seek(0) 
    file_format = imghdr.what(None, header)
    if not file_format:
        return None
    return '.' + (file_format if file_format != 'jpeg' else 'jpg')


def get_path(wine_id):
    directory = os.path.join(current_app.root_path, 
                             current_app.config['UPLOAD_PATH'],
                             current_user.get_id(),
                             str(wine_id))
    return directory



def valid_file(uploaded_file):
    filename = secure_filename(uploaded_file.filename)
    file_ext = os.path.splitext(filename)[1]
    if file_ext not in current_app.config['UPLOAD_EXTENSIONS'] or \
        file_ext != validate_image(uploaded_file.stream):                    
            return False

    return True


def store_file(uploaded_file, wine):
    if wine.file_name:
        silentremove(wine.file_name)
    filename = secure_filename(uploaded_file.filename)
    directory = get_path(wine.id)
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_bytes = BytesIO(uploaded_file.read())
    Image.open(file_bytes).convert('RGB') \
        .save(os.path.join(directory, filename),format='JPEG',optimize=True,quality=10)
    wine.file_name = os.path.join(get_path(wine.id), secure_filename(uploaded_file.filename))


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = WineForm()
    if form.validate_on_submit():
        wine = Wine(body=form.description.data, author=current_user, rating=form.rating.data)
        db.session.add(wine)
        db.session.commit()
        uploaded_file = form.image.data        
        if uploaded_file != None:
            if not valid_file(uploaded_file):
                flash('Image Error!','alert-danger')
                return redirect(url_for('wine.index'))
            store_file(uploaded_file, wine)
            
        db.session.commit()
        flash('Added new wine!','alert-info')
        return redirect(url_for('wine.index'))
    
    return render_template("wine/index.html", form=form,
                           wines=current_user.wines.order_by(desc(Wine.timestamp)).all(),
                           wines_active_status='active')


@bp.route('/uploads/<wine_id>')
@login_required
def upload(wine_id):
    wine = current_user.wines.filter_by(id=wine_id).first()
    if not wine:
        abort(404)
    filename = wine.file_name
    os.path.split(filename)
    return send_from_directory(os.path.dirname(filename),os.path.basename(filename))


@bp.route('/wines/<wine_id>', methods=['GET', 'POST'])
@login_required
def edit_wine(wine_id):
    wine = current_user.wines.filter_by(id=wine_id).first()
    if not wine: abort(404)
        
    form = EditWineForm(rating=wine.rating, description=wine.body)
    if form.validate_on_submit():
        if form.delete.data:
            db.session.delete(wine)
        else:
            wine.body=form.description.data
            wine.rating=form.rating.data
            uploaded_file = form.image.data        
            if uploaded_file != None:
                if not valid_file(uploaded_file):
                    flash('Image Error!','alert-danger')
                    return redirect(url_for('wine.edit_wine',wine_id=wine_id))
                store_file(uploaded_file, wine)
            if form.delete_image.data and wine.file_name:
                silentremove(wine.file_name)
                wine.file_name = None

        db.session.commit()
        flash('Edit Done!','alert-info')
        return redirect(url_for('wine.index'))
    return render_template('wine/edit_wine.html', form=form, 
                           wines_active_status='active')