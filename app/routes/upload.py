import os
import shutil
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename

bp = Blueprint('upload', __name__, url_prefix='/upload')

@bp.route('/', defaults={'subfolder': ''}, methods=['GET', 'POST'])
@bp.route('/<path:subfolder>', methods=['GET', 'POST'])
def upload_page(subfolder):
    upload_root = current_app.config['UPLOAD_FOLDER3']
    target_folder = os.path.join(upload_root, subfolder) if subfolder else upload_root
    os.makedirs(target_folder, exist_ok=True)

    if request.method == 'POST':
        # Folder creation
        if request.form.get('folder_name'):
            new_folder_path = os.path.join(target_folder, secure_filename(request.form['folder_name']))
            os.makedirs(new_folder_path, exist_ok=True)
            flash(f'Folder "{request.form["folder_name"]}" created.', 'success')
            return redirect(url_for('upload.upload_page', subfolder=subfolder))

        # File uploads
        if 'files[]' in request.files:
            for file in request.files.getlist('files[]'):
                if file.filename:
                    file.save(os.path.join(target_folder, secure_filename(file.filename)))
            flash('Files uploaded.', 'success')
            return redirect(url_for('upload.upload_page', subfolder=subfolder))

    # List contents
    folders, files = [], []
    for item in os.listdir(target_folder):
        path = os.path.join(target_folder, item)
        if os.path.isdir(path):
            folders.append(item)
        else:
            files.append(item)

    return render_template('upload_drive.html',
                           folders=folders,
                           files=files,
                           subfolder=subfolder)


@bp.route('/delete', methods=['POST'])
def delete_items():
    subfolder = request.form.get('subfolder', '')
    selected_items = request.form.getlist('selected_items')

    if not selected_items:
        flash('No items selected for deletion.', 'warning')
        return redirect(url_for('upload.upload_page', subfolder=subfolder))

    target_folder = os.path.join(current_app.config['UPLOAD_FOLDER3'], subfolder) if subfolder else current_app.config['UPLOAD_FOLDER3']

    for item in selected_items:
        item_path = os.path.join(target_folder, item)
        if os.path.exists(item_path):
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)  # delete folder
            else:
                os.remove(item_path)  # delete file

    flash(f'Deleted {len(selected_items)} item(s).', 'success')
    return redirect(url_for('upload.upload_page', subfolder=subfolder))
