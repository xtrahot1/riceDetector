import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import DetectionLog, Disease
from app import db
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np

bp = Blueprint('detect', __name__, url_prefix='/detect')

MODEL = load_model('rice_model.h5')
LABELS = ['Bacterial Leaf Blight', 'Brown_Spot', 'Healthy Rice Leaf', 'Rice Blast', 'Rice Tungro', 'Not Rice Leaf']

@bp.route('/', methods=['GET', 'POST'])
@login_required
def detect():
    result = None
    confidence = None
    disease = None
    page = request.args.get('page', 1, type=int)
    logs = DetectionLog.query.filter_by(user_id=current_user.id).order_by(DetectionLog.timestamp.desc()).paginate(page=page, per_page=5)

    if request.method == 'POST':
        img_file = request.files.get('image')
        if img_file:
            filename = os.path.join('app/static/uploads', img_file.filename)
            save_path = os.path.join('app/static/uploads', img_file.filename)
            img_file.save(save_path)

            # Preprocess image for prediction
            img = image.load_img(save_path, target_size=(224, 224))
            x = image.img_to_array(img)
            x = np.expand_dims(x, axis=0)
            x /= 255.0

            # Predict
            prediction = MODEL.predict(x)
            pred_index = np.argmax(prediction)
            pred_label = LABELS[pred_index]
            pred_conf = float(prediction[0][pred_index]) * 100

            # Save detection log
            # relative_path = save_path.split('static/')[-1]
            relative_path = os.path.relpath(save_path, "static").replace("\\", "/")
            log = DetectionLog(
                image_path=relative_path,
                result=pred_label,
                confidence=pred_conf,
                user=current_user
            )
            db.session.add(log)
            db.session.commit()

            # Refresh logs
            logs = DetectionLog.query.filter_by(user_id=current_user.id).order_by(DetectionLog.timestamp.desc()).all()

            # Fetch disease details
            disease = Disease.query.filter_by(name=pred_label).first()

            # Set result and confidence to display
            result = pred_label
            confidence = pred_conf

    return render_template('detect.html', result=result, confidence=confidence, disease=disease, logs=logs)

@bp.route('/logs')
@login_required
def logs():
    if current_user.role == 'Admin':
        page = request.args.get('page', 1, type=int)
        logs = DetectionLog.query.filter_by(user_id=current_user.id) \
        .order_by(DetectionLog.timestamp.desc()) \
        .paginate(page=page, per_page=5)
    else:
        logs = DetectionLog.query.filter_by(user_id=current_user.id).order_by(DetectionLog.timestamp.desc()).all()
    return render_template('logs.html', logs=logs)



