"""
Secure File Sharing Routes
Handles secure file sharing with encrypted links
"""
import os
from flask import Blueprint, request, render_template_string, redirect, url_for, send_file, flash, jsonify, session
from secure_sharing import SecureFileSharing
from auth_routes import login_required
from utils import format_file_size
from templates import NAV_HEADER_TEMPLATE

# Create blueprint
sharing = Blueprint('sharing', __name__)

# Initialize secure sharing service (will be set in create_app)
secure_sharing_service = None

def init_sharing_routes(app):
    """Initialize sharing routes with app context"""
    global secure_sharing_service
    secure_sharing_service = SecureFileSharing(
        upload_folder=app.config['UPLOAD_FOLDER'],
        db_name=app.config['DATABASE_NAME'],
        kem_provider=getattr(app, 'kem_provider', None),
        key_mgmt=getattr(app, 'key_mgmt', None)
    )

@sharing.route('/create-share', methods=['POST'])
@login_required
def create_share():
    """Create a secure shareable file (public or private)"""
    file_id = request.form.get('file_id')
    
    if not file_id:
        return jsonify({'success': False, 'message': 'No file ID provided'}), 400
    
    # Get sharing options
    expiry_hours = int(request.form.get('expiry_hours', 24))
    max_downloads = request.form.get('max_downloads')
    max_downloads = int(max_downloads) if max_downloads and max_downloads.strip() else None
    
    # Get share type and target user for private shares
    share_type = request.form.get('share_type', 'public')
    target_user_id = request.form.get('target_user_id')
    user_password = request.form.get('user_password')  # For private shares
    
    user_id = session['user_id']
    
    # Validate private share requirements
    if share_type == 'private':
        if not target_user_id:
            return jsonify({'success': False, 'message': 'Target user is required for private shares'}), 400
        target_user_id = int(target_user_id)
    
    # Create shareable file from existing file
    result = secure_sharing_service.create_share_from_file_id(
        file_id=int(file_id),
        user_id=user_id,
        expiry_hours=expiry_hours,
        max_downloads=max_downloads,
        share_type=share_type,
        target_user_id=target_user_id,
        user_password=user_password
    )
    
    if result['success']:
        # Generate full URL for sharing
        from flask import request as flask_request
        base_url = flask_request.host_url.rstrip('/')
        full_share_url = f"{base_url}{result['share_url']}"
        
        return jsonify({
            'success': True,
            'share_url': full_share_url,
            'share_id': result['share_id'],
            'expiry': result['expiry']
        })
    else:
        return jsonify({'success': False, 'message': result['message']}), 400

@sharing.route('/share/<share_id>')
def share_download_page(share_id):
    """Display download page for shared file"""
    # Extract share token from URL fragment (will be handled by JavaScript)
    share_info = secure_sharing_service.get_share_info(share_id)
    
    if not share_info:
        return render_template_string(SHARE_ERROR_TEMPLATE, 
                                    error="Share not found or has expired")
    
    if share_info['is_expired']:
        return render_template_string(SHARE_ERROR_TEMPLATE, 
                                    error="This share has expired")
    
    return render_template_string(SHARE_DOWNLOAD_TEMPLATE, 
                                share_info=share_info,
                                format_file_size=format_file_size)

@sharing.route('/download-shared/<share_id>')
def download_shared_file(share_id):
    """Download shared file with embedded key"""
    # Get share token from query parameter (passed by JavaScript)
    share_token = request.args.get('token')
    user_password = request.args.get('password')  # For private shares
    
    if not share_token:
        flash('Invalid share link', 'error')
        return redirect(url_for('sharing.share_download_page', share_id=share_id))
    
    # Get current user if authenticated (required for private shares)
    current_user_id = session.get('user_id')
    
    file_info, error = secure_sharing_service.download_shared_file(
        share_id, 
        share_token,
        current_user_id=current_user_id,
        user_password=user_password
    )
    
    if error:
        return render_template_string(SHARE_ERROR_TEMPLATE, error=error)
    
    try:
        response = send_file(
            file_info['filepath'],
            as_attachment=True,
            download_name=file_info['original_filename']
        )
        
        # Clean up temporary file after sending
        if file_info.get('is_temp', False):
            import atexit
            atexit.register(lambda: os.remove(file_info['filepath']) if os.path.exists(file_info['filepath']) else None)
        
        return response
        
    except Exception as e:
        # Clean up temp file if error occurs
        if file_info.get('is_temp', False) and os.path.exists(file_info['filepath']):
            os.remove(file_info['filepath'])
        return render_template_string(SHARE_ERROR_TEMPLATE, 
                                    error=f'Error downloading file: {str(e)}')

@sharing.route('/my-shares')
@login_required
def my_shares():
    """Display user's shared files"""
    user_id = session['user_id']
    username = session['username']
    shares = secure_sharing_service.get_user_shares(user_id)
    
    # Render navigation header with active page
    nav_header = render_template_string(NAV_HEADER_TEMPLATE, username=username, active_page='shares')
    
    return render_template_string(MY_SHARES_TEMPLATE, 
                                shares=shares, 
                                format_file_size=format_file_size,
                                nav_header=nav_header,
                                username=username)

@sharing.route('/deactivate-share/<share_id>', methods=['POST'])
@login_required
def deactivate_share(share_id):
    """Deactivate a share"""
    user_id = session['user_id']
    success = secure_sharing_service.deactivate_share(share_id, user_id)
    
    if success:
        flash('Share deactivated successfully', 'success')
    else:
        flash('Failed to deactivate share', 'error')
    
    return redirect(url_for('sharing.my_shares'))

@sharing.route('/received-shares')
@login_required
def received_shares():
    """Display private shares received by the user"""
    user_id = session['user_id']
    username = session['username']
    
    # Get private shares targeted to this user
    import sqlite3
    conn = sqlite3.connect(secure_sharing_service.db_name)
    cursor = conn.cursor()
    
    # Check if private share columns exist
    cursor.execute("PRAGMA table_info(shares)")
    columns = [column[1] for column in cursor.fetchall()]
    has_private_columns = 'share_type' in columns
    
    if has_private_columns:
        cursor.execute('''
            SELECT share_id, original_filename, file_size, created_at, expiry_time,
                   max_downloads, download_count, is_active, user_id
            FROM shares 
            WHERE share_type = 'private' AND target_user_id = ? 
            ORDER BY created_at DESC
        ''', (user_id,))
        shares = cursor.fetchall()
    else:
        shares = []
    
    conn.close()
    
    # Get usernames for share creators
    from models import UserModel
    user_model = UserModel(secure_sharing_service.db_name)
    shares_with_creators = []
    for share in shares:
        creator_username = user_model.get_username_by_id(share[8])  # user_id is at index 8
        shares_with_creators.append(share + (creator_username,))
    
    # Render navigation header with active page
    nav_header = render_template_string(NAV_HEADER_TEMPLATE, username=username, active_page='received')
    
    return render_template_string(RECEIVED_SHARES_TEMPLATE, 
                                shares=shares_with_creators, 
                                format_file_size=format_file_size,
                                nav_header=nav_header,
                                username=username)

@sharing.route('/claim-share', methods=['GET', 'POST'])
@login_required
def claim_share():
    """Claim a private share by pasting the link"""
    user_id = session['user_id']
    username = session['username']
    
    if request.method == 'POST':
        share_url = request.form.get('share_url', '')
        user_password = request.form.get('user_password')
        
        if not user_password:
            flash('Password is required to access private shares', 'error')
            return redirect(url_for('sharing.claim_share'))
        
        # Parse share_id and token from URL
        # Format: /share/{share_id}#{token} or full URL
        try:
            if '#' in share_url:
                parts = share_url.split('#')
                share_part = parts[0]
                share_token = parts[1]
                
                # Extract share_id from path
                if '/share/' in share_part:
                    share_id = share_part.split('/share/')[-1].strip('/')
                else:
                    flash('Invalid share link format', 'error')
                    return redirect(url_for('sharing.claim_share'))
            else:
                flash('Invalid share link - missing security token', 'error')
                return redirect(url_for('sharing.claim_share'))
            
            # Try to download the file
            file_info, error = secure_sharing_service.download_shared_file(
                share_id, 
                share_token,
                current_user_id=user_id,
                user_password=user_password
            )
            
            if error:
                flash(f'Error: {error}', 'error')
                return redirect(url_for('sharing.claim_share'))
            
            # Send the file
            try:
                response = send_file(
                    file_info['filepath'],
                    as_attachment=True,
                    download_name=file_info['original_filename']
                )
                
                # Clean up temporary file after sending
                if file_info.get('is_temp', False):
                    import atexit
                    atexit.register(lambda: os.remove(file_info['filepath']) if os.path.exists(file_info['filepath']) else None)
                
                flash('File downloaded successfully!', 'success')
                return response
                
            except Exception as e:
                # Clean up temp file if error occurs
                if file_info.get('is_temp', False) and os.path.exists(file_info['filepath']):
                    os.remove(file_info['filepath'])
                flash(f'Error downloading file: {str(e)}', 'error')
                return redirect(url_for('sharing.claim_share'))
                
        except Exception as e:
            flash(f'Error processing share link: {str(e)}', 'error')
            return redirect(url_for('sharing.claim_share'))
    
    # Render navigation header
    nav_header = render_template_string(NAV_HEADER_TEMPLATE, username=username, active_page='claim')
    
    return render_template_string(CLAIM_SHARE_TEMPLATE,
                                nav_header=nav_header,
                                username=username)

# Templates
SHARE_DOWNLOAD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secure File Download - FileShare</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        primary: '#4361ee',
                        secondary: '#3f37c9',
                        accent: '#4895ef',
                        success: '#4cc9f0',
                        warning: '#f72585',
                        danger: '#e63946'
                    }
                }
            }
        }
    </script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
        body { font-family: 'Poppins', sans-serif; }
    </style>
</head>
<body class="bg-gradient-to-br from-blue-50 to-indigo-100 min-h-screen">
    <div class="container mx-auto px-4 py-8">
        <div class="max-w-md mx-auto bg-white rounded-2xl shadow-xl p-8">
            <!-- Header -->
            <div class="text-center mb-8">
                <div class="w-16 h-16 rounded-2xl bg-primary flex items-center justify-center mx-auto mb-4">
                    <i class="fas fa-shield-alt text-white text-2xl"></i>
                </div>
                <h1 class="text-2xl font-bold text-gray-800">Secure File Download</h1>
                <p class="text-gray-600 mt-2">This file has been securely shared with you</p>
            </div>

            <!-- File Info -->
            <div class="bg-gray-50 rounded-xl p-6 mb-6">
                <div class="flex items-center mb-4">
                    <i class="fas fa-file text-primary text-2xl mr-4"></i>
                    <div>
                        <h3 class="font-semibold text-gray-800">{{ share_info.filename }}</h3>
                        <p class="text-sm text-gray-600">{{ format_file_size(share_info.file_size) }}</p>
                    </div>
                </div>
                
                <div class="grid grid-cols-2 gap-4 text-sm">
                    <div>
                        <span class="text-gray-500">Shared:</span>
                        <p class="font-medium">{{ share_info.created_at[:19] }}</p>
                    </div>
                    <div>
                        <span class="text-gray-500">Expires:</span>
                        <p class="font-medium">{{ share_info.expiry_time[:19] }}</p>
                    </div>
                </div>
            </div>

            <!-- Security Notice -->
            <div class="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
                <div class="flex items-start">
                    <i class="fas fa-lock text-green-600 mt-1 mr-3"></i>
                    <div>
                        <h4 class="font-semibold text-green-800">Secure Download</h4>
                        <p class="text-sm text-green-700 mt-1">
                            This file is encrypted and will be automatically decrypted for you. 
                            The encryption key is embedded in this secure link.
                        </p>
                    </div>
                </div>
            </div>

            <!-- Download Button -->
            <button id="downloadBtn" 
                    class="w-full bg-primary hover:bg-secondary text-white py-3 px-6 rounded-lg font-medium transition duration-300 mb-4">
                <i class="fas fa-download mr-2"></i>Download File
            </button>

            <!-- Footer -->
            <div class="text-center">
                <p class="text-xs text-gray-500">
                    Powered by <span class="font-semibold">FileShare</span> - Secure File Sharing
                </p>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('downloadBtn').addEventListener('click', function() {
            // Extract token from URL fragment
            const token = window.location.hash.substring(1);
            
            if (!token) {
                alert('Invalid share link - missing security token');
                return;
            }
            
            // Create download URL with token
            const downloadUrl = `/download-shared/{{ share_info.share_id }}?token=${encodeURIComponent(token)}`;
            
            // Start download
            window.location.href = downloadUrl;
        });
    </script>
</body>
</html>
'''

SHARE_ERROR_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Share Error - FileShare</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
        body { font-family: 'Poppins', sans-serif; }
    </style>
</head>
<body class="bg-gradient-to-br from-red-50 to-pink-100 min-h-screen">
    <div class="container mx-auto px-4 py-8">
        <div class="max-w-md mx-auto bg-white rounded-2xl shadow-xl p-8 text-center">
            <div class="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
                <i class="fas fa-exclamation-triangle text-red-600 text-2xl"></i>
            </div>
            <h1 class="text-2xl font-bold text-gray-800 mb-4">Share Unavailable</h1>
            <p class="text-gray-600 mb-6">{{ error }}</p>
            
            <a href="/" class="inline-block bg-blue-600 hover:bg-blue-700 text-white py-2 px-6 rounded-lg font-medium transition duration-300">
                <i class="fas fa-home mr-2"></i>Go to Homepage
            </a>
        </div>
    </div>
</body>
</html>
'''

MY_SHARES_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Shares - FileShare</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        primary: '#4361ee',
                        secondary: '#3f37c9',
                        accent: '#4895ef',
                        light: '#f8f9fa',
                        dark: '#212529',
                        success: '#4cc9f0',
                        warning: '#f72585',
                        danger: '#e63946'
                    }
                }
            }
        }
    </script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
        body { 
            font-family: 'Poppins', sans-serif; 
            background: linear-gradient(135deg, #f5f7fa 0%, #e4edf5 100%);
            min-height: 100vh;
        }
    </style>
</head>
<body class="text-dark">
{{ nav_header|safe }}
    
    <!-- Main Content -->
    <main class="container mx-auto px-4 py-8">
        <div class="max-w-4xl mx-auto">
            <!-- Page Header -->
            <div class="bg-white rounded-2xl shadow-lg p-6 mb-6">
                <div>
                    <h1 class="text-3xl font-bold text-gray-800">My Shared Files</h1>
                    <p class="text-gray-600 mt-2">Manage your secure file shares</p>
                </div>
            </div>

            <!-- Shares List -->
            <div class="bg-white rounded-2xl shadow-xl p-6">
                {% if shares %}
                    <div class="space-y-4">
                        {% for share in shares %}
                        <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition duration-300">
                            <div class="flex items-center justify-between">
                                <div class="flex items-center">
                                    <i class="fas fa-file text-primary text-xl mr-4"></i>
                                    <div>
                                        <h3 class="font-semibold text-gray-800">{{ share[1] }}</h3>
                                        <p class="text-sm text-gray-600">{{ format_file_size(share[2]) }}</p>
                                    </div>
                                </div>
                                
                                <div class="flex items-center space-x-4">
                                    <div class="text-sm text-gray-600">
                                        <div>Downloads: {{ share[6] }}{% if share[5] %}/{{ share[5] }}{% endif %}</div>
                                        <div>Expires: {{ share[4][:19] }}</div>
                                    </div>
                                    
                                    {% if share[7] %}
                                        <span class="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">Active</span>
                                    {% else %}
                                        <span class="px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs">Inactive</span>
                                    {% endif %}
                                    
                                    {% if share[7] %}
                                        <form method="POST" action="{{ url_for('sharing.deactivate_share', share_id=share[0]) }}" 
                                              onsubmit="return confirm('Deactivate this share?')" class="inline">
                                            <button type="submit" 
                                                    class="text-red-600 hover:text-red-800 transition duration-300">
                                                <i class="fas fa-times"></i>
                                            </button>
                                        </form>
                                    {% endif %}
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                {% else %}
                    <div class="text-center py-12">
                        <i class="fas fa-share-alt text-gray-400 text-6xl mb-4"></i>
                        <h3 class="text-xl font-semibold text-gray-600 mb-2">No Shares Yet</h3>
                        <p class="text-gray-500">Create your first secure file share from the dashboard</p>
                    </div>
                {% endif %}
            </div>
        </div>
    </main>
    
    <!-- Footer -->
    <footer class="bg-white border-t mt-12">
        <div class="container mx-auto px-4 py-8">
            <div class="flex flex-col md:flex-row justify-between items-center">
                <div class="mb-4 md:mb-0">
                    <div class="flex items-center">
                        <div class="w-8 h-8 rounded-lg bg-primary flex items-center justify-center mr-2">
                            <i class="fas fa-cloud-upload-alt text-white"></i>
                        </div>
                        <span class="text-xl font-bold text-dark">File<span class="text-primary">Share</span></span>
                    </div>
                    <p class="text-gray-500 text-sm mt-2">Secure and reliable file sharing platform</p>
                </div>
                <div class="flex space-x-6">
                    <a href="#" class="text-gray-500 hover:text-primary">
                        <i class="fab fa-facebook-f"></i>
                    </a>
                    <a href="#" class="text-gray-500 hover:text-primary">
                        <i class="fab fa-twitter"></i>
                    </a>
                    <a href="#" class="text-gray-500 hover:text-primary">
                        <i class="fab fa-instagram"></i>
                    </a>
                    <a href="#" class="text-gray-500 hover:text-primary">
                        <i class="fab fa-linkedin-in"></i>
                    </a>
                </div>
            </div>
            <div class="border-t border-gray-200 mt-6 pt-6 text-center text-gray-500 text-sm">
                <p>© 2023 FileShare. All rights reserved.</p>
            </div>
        </div>
    </footer>
</body>
</html>
'''

RECEIVED_SHARES_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Received Shares - FileShare</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        primary: '#4361ee',
                        secondary: '#3f37c9',
                        accent: '#4895ef'
                    }
                }
            }
        }
    </script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
        body { font-family: 'Poppins', sans-serif; }
    </style>
</head>
<body class="bg-gradient-to-br from-blue-50 to-indigo-100 min-h-screen">
{{ nav_header|safe }}
    
    <main class="container mx-auto px-4 py-8">
        <div class="max-w-4xl mx-auto">
            <div class="bg-white rounded-2xl shadow-lg p-6 mb-6">
                <h1 class="text-3xl font-bold text-gray-800">📨 Received Private Shares</h1>
                <p class="text-gray-600 mt-2">Quantum-secure files shared with you</p>
            </div>

            <div class="bg-white rounded-2xl shadow-xl p-6">
                {% if shares %}
                    <div class="space-y-4">
                        {% for share in shares %}
                        <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition duration-300">
                            <div class="flex items-center justify-between">
                                <div class="flex items-center">
                                    <i class="fas fa-lock text-primary text-xl mr-4"></i>
                                    <div>
                                        <h3 class="font-semibold text-gray-800">{{ share[1] }}</h3>
                                        <p class="text-sm text-gray-600">{{ format_file_size(share[2]) }} • From: {{ share[9] }}</p>
                                    </div>
                                </div>
                                
                                <div class="flex items-center space-x-4">
                                    <div class="text-sm text-gray-600">
                                        <div>Expires: {{ share[4][:19] }}</div>
                                    </div>
                                    
                                    {% if share[7] %}
                                        <span class="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">Active</span>
                                    {% else %}
                                        <span class="px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs">Expired</span>
                                    {% endif %}
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                {% else %}
                    <div class="text-center py-12">
                        <i class="fas fa-inbox text-gray-400 text-6xl mb-4"></i>
                        <h3 class="text-xl font-semibold text-gray-600 mb-2">No Private Shares Yet</h3>
                        <p class="text-gray-500">When someone shares a file privately with you, it will appear here</p>
                        <a href="{{ url_for('sharing.claim_share') }}" class="inline-block mt-4 bg-primary hover:bg-secondary text-white py-2 px-6 rounded-lg transition duration-300">
                            <i class="fas fa-plus mr-2"></i>Claim a Share
                        </a>
                    </div>
                {% endif %}
            </div>
        </div>
    </main>
</body>
</html>
'''

CLAIM_SHARE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Claim Private Share - FileShare</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        primary: '#4361ee',
                        secondary: '#3f37c9',
                        accent: '#4895ef'
                    }
                }
            }
        }
    </script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
        body { font-family: 'Poppins', sans-serif; }
    </style>
</head>
<body class="bg-gradient-to-br from-blue-50 to-indigo-100 min-h-screen">
{{ nav_header|safe }}
    
    <main class="container mx-auto px-4 py-8">
        <div class="max-w-2xl mx-auto">
            <div class="bg-white rounded-2xl shadow-xl p-8">
                <div class="text-center mb-8">
                    <div class="w-16 h-16 rounded-2xl bg-primary flex items-center justify-center mx-auto mb-4">
                        <i class="fas fa-key text-white text-2xl"></i>
                    </div>
                    <h1 class="text-3xl font-bold text-gray-800">Claim Private Share</h1>
                    <p class="text-gray-600 mt-2">Paste your quantum-secure private share link below</p>
                </div>

                <form method="POST" action="{{ url_for('sharing.claim_share') }}">
                    <div class="mb-6">
                        <label class="block text-gray-700 font-medium mb-2">
                            <i class="fas fa-link mr-2"></i>Share Link
                        </label>
                        <input type="text" 
                               name="share_url" 
                               placeholder="Paste the complete share link here"
                               class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                               required>
                        <p class="text-sm text-gray-500 mt-2">Example: http://localhost:5000/share/abc123#tokenhere</p>
                    </div>

                    <div class="mb-6">
                        <label class="block text-gray-700 font-medium mb-2">
                            <i class="fas fa-lock mr-2"></i>Your Password
                        </label>
                        <input type="password" 
                               name="user_password" 
                               placeholder="Enter your account password"
                               class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                               required>
                        <p class="text-sm text-gray-500 mt-2">Required to decrypt the file using your Kyber private key</p>
                    </div>

                    <button type="submit" 
                            class="w-full bg-primary hover:bg-secondary text-white py-3 px-6 rounded-lg font-medium transition duration-300">
                        <i class="fas fa-download mr-2"></i>Claim and Download
                    </button>
                </form>

                <div class="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <h3 class="font-semibold text-blue-800 mb-2">
                        <i class="fas fa-info-circle mr-2"></i>How it works
                    </h3>
                    <ul class="text-sm text-blue-700 space-y-1">
                        <li>• The sender encrypted the file with AES-256</li>
                        <li>• The AES key was wrapped using your Kyber public key</li>
                        <li>• Your password decrypts your Kyber private key</li>
                        <li>• Your private key unwraps the AES key to decrypt the file</li>
                        <li>• 🔐 Quantum-secure end-to-end encryption!</li>
                    </ul>
                </div>
            </div>
        </div>
    </main>
</body>
</html>
'''
