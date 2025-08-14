from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import User, Disease, DetectionLog
from app import db

bp = Blueprint('dashboard', __name__)

@bp.route('/dashboard')
@login_required
def dashboard():
    role = current_user.role

    stats = {
        'users': User.query.count(),
        'diseases': Disease.query.count(),
        'detections': DetectionLog.query.count()
    } if role == 'Admin' else {}
    diseases = Disease.query.order_by(Disease.id.desc()).all()

    return render_template('dashboard.html', role=role, stats=stats, diseases=diseases)


