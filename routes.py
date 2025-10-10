"""
Route handlers for the File Sharing Application
"""
import os
from flask import Blueprint, request, render_template_string, redirect, url_for, send_file, flash, jsonify, current_app, session
from services import FileService
from templates import HTML_TEMPLATE, NAV_HEADER_TEMPLATE
from utils import format_file_size
from auth_routes import login_required

# Create blueprint
main = Blueprint('main', __name__)

# Initialize file service (will be set in create_app)
file_service = None

def init_routes(app):
    """Initialize routes with app context"""
    global file_service
    file_service = FileService(
        upload_folder=app.config['UPLOAD_FOLDER'],
        db_name=app.config['DATABASE_NAME'],
        enable_encryption=app.config.get('ENABLE_ENCRYPTION', True),
        kem_provider=getattr(app, 'kem_provider', None),
        key_mgmt=getattr(app, 'key_mgmt', None)
    )

@main.route('/')
def root():
    """Root route - redirect to login if not authenticated, otherwise to dashboard"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return redirect(url_for('main.dashboard'))

@main.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    """Main dashboard with file upload and listing"""
    user_id = session['user_id']
    username = session['username']
    
    if request.method == 'POST':
        # Handle file upload
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file:
            result = file_service.upload_file(file, user_id)
            if result['success']:
                flash(result['message'], 'success')
            else:
                flash(result['message'], 'error')
            
            return redirect(url_for('main.dashboard'))
    
    # Get user's files for display
    files = file_service.get_user_files(user_id)
    
    # Render navigation header with active page
    nav_header = render_template_string(NAV_HEADER_TEMPLATE, username=username, active_page='home')
    
    return render_template_string(HTML_TEMPLATE, 
                                files=files, 
                                format_file_size=format_file_size, 
                                username=username, 
                                nav_header=nav_header)

@main.route('/download/<int:file_id>')
@login_required
def download_file(file_id):
    """Download a file by ID with decryption support"""
    user_id = session['user_id']
    file_info, error = file_service.get_file_for_download(file_id, user_id)
    
    if error:
        flash(error, 'error')
        return redirect(url_for('main.dashboard'))
    
    try:
        response = send_file(
            file_info['filepath'], 
            as_attachment=True, 
            download_name=file_info['original_filename']
        )
        
        # Clean up temporary decrypted file after sending
        if file_info.get('is_temp', False):
            import atexit
            atexit.register(lambda: os.remove(file_info['filepath']) if os.path.exists(file_info['filepath']) else None)
        
        return response
        
    except Exception as e:
        # Clean up temp file if error occurs
        if file_info.get('is_temp', False) and os.path.exists(file_info['filepath']):
            os.remove(file_info['filepath'])
        flash(f'Error downloading file: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))

@main.route('/delete/<int:file_id>')
@login_required
def delete_file(file_id):
    """Delete a file by ID"""
    user_id = session['user_id']
    success, message = file_service.delete_file(file_id, user_id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('main.dashboard'))

@main.route('/api/files')
@login_required
def api_files():
    """API endpoint to get file list as JSON"""
    user_id = session['user_id']
    files = file_service.get_user_files(user_id)
    file_list = []
    for file in files:
        file_list.append({
            'id': file[0],
            'filename': file[1],
            'size': file[2],
            'size_formatted': format_file_size(file[2]),
            'upload_date': file[3],
            'download_count': file[4]
        })
    return jsonify(file_list)
