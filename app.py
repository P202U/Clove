from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Flask template filter to list files in the images folder dynamically
@app.template_filter('listdir')
def listdir_filter(path):
    return os.listdir(path)

@app.route('/')
def index():
    # Dynamically read the file list each time
    image_files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', image_files=image_files)

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if there are files in the request
    if 'file' not in request.files:
        return redirect(request.url)
    
    files = request.files.getlist('file')
    
    for file in files:
        if file.filename == '':
            continue

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    app.run(debug=True)