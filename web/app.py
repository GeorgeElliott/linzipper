import os
import shutil
import subprocess
from flask import Flask, request, send_file, render_template
from werkzeug.exceptions import RequestEntityTooLarge

app = Flask(__name__)

# Read upload limit from environment (value is in megabytes). If not set, default to 100 MB.
# Flask's `MAX_CONTENT_LENGTH` expects bytes.
max_mb = int(os.getenv('MAX_CONTENT_MB', '100'))
app.config['MAX_CONTENT_LENGTH'] = max_mb * 1024 * 1024

# Temp location to store uploaded files
UPLOAD_ROOT = '/tmp/linzipper_uploads'

@app.route('/', methods=['GET', 'POST'])
def upload_folder():
    if request.method == 'POST':
        files = request.files.getlist('file_folder')
        if not files or files[0].filename == '':
            return render_template('index.html', max_upload_mb=(app.config['MAX_CONTENT_LENGTH'] // (1024*1024)), error_message="No files selected"), 400

        # prepare a clean workspace
        batch_id = "current_job"
        batch_dir = os.path.join(UPLOAD_ROOT, batch_id)
        if os.path.exists(batch_dir):
            shutil.rmtree(batch_dir)
        os.makedirs(batch_dir)

        # save uploaded files, preserving directory structure
        for file in files:
            rel_path = file.filename
            dest_path = os.path.join(batch_dir, rel_path)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            file.save(dest_path)

        try:
            # determine the top-level folder saved in the batch directory
            top_level_items = next(os.walk(batch_dir))[1]
            if not top_level_items:
                return render_template('index.html', max_upload_mb=(app.config['MAX_CONTENT_LENGTH'] // (1024*1024)), error_message="Could not identify the folder structure"), 500
            
            top_folder_name = top_level_items[0]
            target_dir = os.path.join(batch_dir, top_folder_name)

            # create a zip archive from inside the top folder (produces a flat archive)
            output_zip_path = f"/tmp/{top_folder_name}.zip"
            
            # run zip via shell so we can change directory then archive
            subprocess.run(
                f"cd '{target_dir}' && zip -r '{output_zip_path}' .", 
                shell=True, 
                check=True
            )

            return send_file(
                output_zip_path, 
                as_attachment=True, 
                download_name=f"{top_folder_name}.zip"
            )

        except Exception as e:
            return render_template('index.html', max_upload_mb=(app.config['MAX_CONTENT_LENGTH'] // (1024*1024)), error_message=f"Error during zipping: {str(e)}"), 500

    return render_template('index.html', max_upload_mb=(app.config['MAX_CONTENT_LENGTH'] // (1024*1024)))


@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    limit_mb = app.config['MAX_CONTENT_LENGTH'] // (1024*1024)
    return render_template('index.html', max_upload_mb=limit_mb, error_message=f"Uploaded data is too large. Maximum allowed is {limit_mb} MB."), 413

if __name__ == '__main__':
    # listen on all interfaces
    app.run(host='0.0.0.0', port=5000)
