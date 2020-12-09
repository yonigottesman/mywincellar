from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app import db
from app.main.forms import WineForm
from app.models import Wine
from app.main import bp

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = WineForm()
    if form.validate_on_submit():
        wine = Wine(body=form.description.data, author=current_user)
        db.session.add(wine)
        db.session.commit()
        flash('Added new wine!')
        return redirect(url_for('main.index'))
    
    wines = current_user.wines.all()
    return render_template("index.html", title='Home Page', form=form,
                           wines=wines)


