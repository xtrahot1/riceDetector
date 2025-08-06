from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Disease
from app import db

bp = Blueprint('disease', __name__, url_prefix='/disease')

def admin_or_researcher_required(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.role not in ['Admin', 'Researcher']:
            flash("Access denied.")
            return redirect(url_for('detect.detect'))
        return f(*args, **kwargs)
    return wrapper

@bp.route('/')
@login_required
@admin_or_researcher_required
def list_diseases():
    diseases = Disease.query.all()
    return render_template('disease/list.html', diseases=diseases)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_or_researcher_required
def create_disease():
    if request.method == 'POST':
        name = request.form['name']
        desc = request.form['description']
        symptoms = request.form['symptoms']
        treatment = request.form['treatment']
        db.session.add(Disease(name=name, description=desc, symptoms=symptoms, treatment=treatment))
        db.session.commit()
        flash("Disease added.")
        return redirect(url_for('disease.list_diseases'))
    return render_template('disease/form.html')

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_or_researcher_required
def edit_disease(id):
    disease = Disease.query.get_or_404(id)
    if request.method == 'POST':
        disease.name = request.form['name']
        disease.description = request.form['description']
        symptoms = request.form['symptoms']
        treatment = request.form['treatment']
        db.session.commit()
        flash("Disease updated.")
        return redirect(url_for('disease.list_diseases'))
    return render_template('disease/form.html', disease=disease)

@bp.route('/delete/<int:id>')
@login_required
@admin_or_researcher_required
def delete_disease(id):
    disease = Disease.query.get_or_404(id)
    db.session.delete(disease)
    db.session.commit()
    flash("Disease deleted.")
    return redirect(url_for('disease.list_diseases'))
