"""
HTML templates for the File Sharing Application
"""

# Shared navigation header component
NAV_HEADER_TEMPLATE = '''
    <!-- Header -->
    <header class="bg-white shadow-sm">
        <div class="container mx-auto px-4 py-4">
            <div class="flex justify-between items-center">
                <div class="flex items-center space-x-2">
                    <div class="w-10 h-10 rounded-lg bg-primary flex items-center justify-center">
                        <i class="fas fa-cloud-upload-alt text-white text-xl"></i>
                    </div>
                    <h1 class="text-2xl font-bold text-primary">File<span class="text-secondary">Share</span></h1>
                </div>
                
                <!-- Desktop Navigation -->
                <nav class="hidden md:flex space-x-6">
                    <a href="{{ url_for('main.dashboard') }}" class="{{ 'text-primary font-medium border-b-2 border-primary pb-1' if active_page == 'home' else 'text-gray-600 hover:text-primary' }} transition duration-300">Home</a>
                    <a href="{{ url_for('sharing.my_shares') }}" class="{{ 'text-primary font-medium border-b-2 border-primary pb-1' if active_page == 'shares' else 'text-gray-600 hover:text-primary' }} transition duration-300">My Shares</a>
                    <a href="{{ url_for('sharing.received_shares') }}" class="{{ 'text-primary font-medium border-b-2 border-primary pb-1' if active_page == 'received' else 'text-gray-600 hover:text-primary' }} transition duration-300">Received</a>
                    <a href="{{ url_for('sharing.claim_share') }}" class="{{ 'text-primary font-medium border-b-2 border-primary pb-1' if active_page == 'claim' else 'text-gray-600 hover:text-primary' }} transition duration-300">Claim Share</a>
                </nav>
                
                <!-- Desktop User Menu -->
                <div class="hidden md:flex items-center space-x-4">
                    <span class="text-gray-600">Welcome, <strong>{{ username }}</strong></span>
                    <a href="{{ url_for('auth.logout') }}" class="bg-danger hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition duration-300">
                        <i class="fas fa-sign-out-alt mr-1"></i> Logout
                    </a>
                </div>
                
                <!-- Mobile Menu Button -->
                <button id="mobileMenuBtn" class="md:hidden text-gray-600 hover:text-primary focus:outline-none">
                    <i class="fas fa-bars text-xl"></i>
                </button>
            </div>
            
            <!-- Mobile Navigation Menu -->
            <div id="mobileMenu" class="md:hidden hidden mt-4 pt-4 border-t border-gray-200">
                <nav class="flex flex-col space-y-3">
                    <a href="{{ url_for('main.dashboard') }}" class="{{ 'text-primary font-medium bg-blue-50 px-3 py-2 rounded-lg' if active_page == 'home' else 'text-gray-600 hover:text-primary px-3 py-2' }} transition duration-300">
                        <i class="fas fa-home mr-2"></i>Home
                    </a>
                    <a href="{{ url_for('sharing.my_shares') }}" class="{{ 'text-primary font-medium bg-blue-50 px-3 py-2 rounded-lg' if active_page == 'shares' else 'text-gray-600 hover:text-primary px-3 py-2' }} transition duration-300">
                        <i class="fas fa-share-alt mr-2"></i>My Shares
                    </a>
                    <a href="{{ url_for('sharing.received_shares') }}" class="{{ 'text-primary font-medium bg-blue-50 px-3 py-2 rounded-lg' if active_page == 'received' else 'text-gray-600 hover:text-primary px-3 py-2' }} transition duration-300">
                        <i class="fas fa-inbox mr-2"></i>Received
                    </a>
                    <a href="{{ url_for('sharing.claim_share') }}" class="{{ 'text-primary font-medium bg-blue-50 px-3 py-2 rounded-lg' if active_page == 'claim' else 'text-gray-600 hover:text-primary px-3 py-2' }} transition duration-300">
                        <i class="fas fa-key mr-2"></i>Claim Share
                    </a>
                    <div class="border-t border-gray-200 pt-3 mt-3">
                        <span class="text-gray-600 text-sm px-3 block mb-2">Welcome, <strong>{{ username }}</strong></span>
                        <a href="{{ url_for('auth.logout') }}" class="bg-danger hover:bg-red-700 text-white px-3 py-2 rounded-lg text-sm font-medium transition duration-300 inline-block">
                            <i class="fas fa-sign-out-alt mr-1"></i> Logout
                        </a>
                    </div>
                </nav>
            </div>
        </div>
    </header>
    
    <script>
        // Mobile menu toggle
        document.addEventListener('DOMContentLoaded', function() {
            const mobileMenuBtn = document.getElementById('mobileMenuBtn');
            const mobileMenu = document.getElementById('mobileMenu');
            
            if (mobileMenuBtn && mobileMenu) {
                mobileMenuBtn.addEventListener('click', function() {
                    mobileMenu.classList.toggle('hidden');
                    const icon = this.querySelector('i');
                    if (mobileMenu.classList.contains('hidden')) {
                        icon.className = 'fas fa-bars text-xl';
                    } else {
                        icon.className = 'fas fa-times text-xl';
                    }
                });
            }
        });
    </script>
'''

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FileShare - Modern File Sharing Platform</title>
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
        
        .file-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        }
        
        .upload-area {
            border: 2px dashed #4361ee;
            transition: all 0.3s ease;
        }
        
        .upload-area:hover, .upload-area.dragover {
            background-color: rgba(67, 97, 238, 0.05);
            border-color: #3f37c9;
        }
        
        .file-icon {
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 10px;
        }
        
        .progress-bar {
            height: 6px;
            border-radius: 3px;
            background-color: #e9ecef;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4361ee, #3f37c9);
            border-radius: 3px;
            transition: width 0.4s ease;
        }
        
        .animate-pulse-slow {
            animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .toast {
            transform: translateX(100%);
            transition: transform 0.3s ease;
        }
        
        .toast.show {
            transform: translateX(0);
        }
    </style>
</head>
<body class="text-dark">
{{ nav_header|safe }}

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-8">
        <!-- Flash Messages -->
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <div class="mb-8">
                    <div class="flash-messages space-y-3">
                        {% for category, message in messages %}
                            {% if category == 'success' %}
                                <div class="flash-success flex items-center p-4 bg-green-100 text-green-800 rounded-lg border border-green-200">
                                    <i class="fas fa-check-circle text-xl mr-3"></i>
                                    <div>
                                        <p class="font-medium">{{ message }}</p>
                                        <p class="text-sm">Your file is now available for sharing</p>
                                    </div>
                                    <button class="ml-auto text-green-600 hover:text-green-800 close-flash">
                                        <i class="fas fa-times"></i>
                                    </button>
                                </div>
                            {% elif category == 'error' %}
                                <div class="flash-error flex items-center p-4 bg-red-100 text-red-800 rounded-lg border border-red-200">
                                    <i class="fas fa-exclamation-circle text-xl mr-3"></i>
                                    <div>
                                        <p class="font-medium">{{ message }}</p>
                                        <p class="text-sm">Please try again with a smaller file</p>
                                    </div>
                                    <button class="ml-auto text-red-600 hover:text-red-800 close-flash">
                                        <i class="fas fa-times"></i>
                                    </button>
                                </div>
                            {% endif %}
                        {% endfor %}
                    </div>
                </div>
            {% endif %}
        {% endwith %}

        <!-- Upload Section -->
        <section class="mb-12">
            <div class="bg-white rounded-2xl shadow-lg p-6 md:p-8">
                <div class="flex items-center justify-between mb-6">
                    <h2 class="text-2xl font-bold text-dark">Upload Files</h2>
                    <span class="text-sm text-gray-500">Maximum file size: 16MB</span>
                </div>
                
                <form method="POST" enctype="multipart/form-data" id="uploadForm">
                    <div class="upload-area rounded-xl p-8 text-center cursor-pointer transition-all duration-300" id="dropZone">
                        <div class="flex flex-col items-center justify-center">
                            <div class="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center mb-4">
                                <i class="fas fa-cloud-upload-alt text-primary text-2xl"></i>
                            </div>
                            <h3 class="text-xl font-semibold mb-2">Drag & Drop files here</h3>
                            <p class="text-gray-500 mb-4">or</p>
                            <button type="button" class="bg-primary hover:bg-secondary text-white px-6 py-3 rounded-lg font-medium transition duration-300 flex items-center" onclick="document.getElementById('fileInput').click()">
                                <i class="fas fa-folder-open mr-2"></i> Browse Files
                            </button>
                            <p class="text-gray-400 text-sm mt-4">Supports: PDF, DOC, JPG, PNG, MP4, ZIP</p>
                        </div>
                        <input type="file" name="file" id="fileInput" class="hidden" accept="*/*">
                    </div>
                    
                    <!-- Upload Progress -->
                    <div class="mt-6 hidden" id="uploadProgress">
                        <div class="flex justify-between mb-2">
                            <span class="font-medium" id="uploadFileName">Uploading: document.pdf</span>
                            <span id="uploadPercent">0%</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" id="progressFill" style="width: 0%"></div>
                        </div>
                    </div>
                </form>
            </div>
        </section>

        <!-- Files Section -->
        <section>
            <div class="flex justify-between items-center mb-6">
                <h2 class="text-2xl font-bold text-dark">Your Files ({{ files|length }} files)</h2>
                <div class="flex space-x-2">
                    <div class="relative">
                        <button id="filterBtn" class="bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium">
                            <i class="fas fa-filter mr-1"></i> Filter
                        </button>
                        <div id="filterDropdown" class="hidden absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border z-10">
                            <div class="py-2">
                                <button class="block w-full text-left px-4 py-2 hover:bg-gray-100 filter-option" data-filter="all">All Files</button>
                                <button class="block w-full text-left px-4 py-2 hover:bg-gray-100 filter-option" data-filter="pdf">PDF Documents</button>
                                <button class="block w-full text-left px-4 py-2 hover:bg-gray-100 filter-option" data-filter="image">Images</button>
                                <button class="block w-full text-left px-4 py-2 hover:bg-gray-100 filter-option" data-filter="video">Videos</button>
                                <button class="block w-full text-left px-4 py-2 hover:bg-gray-100 filter-option" data-filter="archive">Archives</button>
                                <button class="block w-full text-left px-4 py-2 hover:bg-gray-100 filter-option" data-filter="document">Documents</button>
                            </div>
                        </div>
                    </div>
                    <div class="relative">
                        <button id="sortBtn" class="bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium">
                            <i class="fas fa-sort mr-1"></i> Sort
                        </button>
                        <div id="sortDropdown" class="hidden absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border z-10">
                            <div class="py-2">
                                <button class="block w-full text-left px-4 py-2 hover:bg-gray-100 sort-option" data-sort="name-asc">Name (A-Z)</button>
                                <button class="block w-full text-left px-4 py-2 hover:bg-gray-100 sort-option" data-sort="name-desc">Name (Z-A)</button>
                                <button class="block w-full text-left px-4 py-2 hover:bg-gray-100 sort-option" data-sort="size-asc">Size (Small to Large)</button>
                                <button class="block w-full text-left px-4 py-2 hover:bg-gray-100 sort-option" data-sort="size-desc">Size (Large to Small)</button>
                                <button class="block w-full text-left px-4 py-2 hover:bg-gray-100 sort-option" data-sort="date-asc">Date (Oldest First)</button>
                                <button class="block w-full text-left px-4 py-2 hover:bg-gray-100 sort-option" data-sort="date-desc">Date (Newest First)</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Files Grid -->
            {% if files %}
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {% for file in files %}
                        <div class="file-card bg-white rounded-xl shadow-md overflow-hidden transition-all duration-300">
                            <div class="p-5">
                                <div class="flex items-start">
                                    <div class="file-icon mr-4">
                                        {% set ext = file[1].split('.')[-1].lower() %}
                                        {% if ext in ['pdf'] %}
                                            <div class="file-icon bg-red-100 text-red-600">
                                                <i class="fas fa-file-pdf text-xl"></i>
                                            </div>
                                        {% elif ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp'] %}
                                            <div class="file-icon bg-green-100 text-green-600">
                                                <i class="fas fa-file-image text-xl"></i>
                                            </div>
                                        {% elif ext in ['mp4', 'avi', 'mov', 'wmv', 'flv'] %}
                                            <div class="file-icon bg-purple-100 text-purple-600">
                                                <i class="fas fa-file-video text-xl"></i>
                                            </div>
                                        {% elif ext in ['mp3', 'wav', 'ogg', 'aac'] %}
                                            <div class="file-icon bg-yellow-100 text-yellow-600">
                                                <i class="fas fa-file-audio text-xl"></i>
                                            </div>
                                        {% elif ext in ['zip', 'rar', '7z', 'tar'] %}
                                            <div class="file-icon bg-orange-100 text-orange-600">
                                                <i class="fas fa-file-archive text-xl"></i>
                                            </div>
                                        {% elif ext in ['doc', 'docx'] %}
                                            <div class="file-icon bg-blue-100 text-blue-600">
                                                <i class="fas fa-file-word text-xl"></i>
                                            </div>
                                        {% elif ext in ['xls', 'xlsx'] %}
                                            <div class="file-icon bg-green-100 text-green-600">
                                                <i class="fas fa-file-excel text-xl"></i>
                                            </div>
                                        {% else %}
                                            <div class="file-icon bg-gray-100 text-gray-600">
                                                <i class="fas fa-file text-xl"></i>
                                            </div>
                                        {% endif %}
                                    </div>
                                    <div class="flex-1">
                                        <h3 class="font-bold text-lg truncate">{{ file[1] }}</h3>
                                        <p class="text-gray-500 text-sm">{{ ext.upper() }} Document</p>
                                        <div class="flex items-center mt-2 text-sm">
                                            <span class="text-gray-500 mr-3">{{ format_file_size(file[2]) }}</span>
                                            <span class="text-gray-500">{{ file[3] }}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="px-5 py-3 bg-gray-50 flex justify-between items-center">
                                <div class="flex items-center text-sm text-gray-500">
                                    <i class="fas fa-download mr-1"></i>
                                    <span>{{ file[4] }} downloads</span>
                                </div>
                                <div class="flex space-x-2">
                                    <a href="{{ url_for('main.download_file', file_id=file[0]) }}" class="bg-primary hover:bg-secondary text-white p-2 rounded-lg transition duration-300" title="Download">
                                        <i class="fas fa-download"></i>
                                    </a>
                                    <button class="bg-green-500 hover:bg-green-600 text-white p-2 rounded-lg transition duration-300" title="Secure Share" onclick="openShareModal({{ file[0] }}, '{{ file[1] }}')">
                                        <i class="fas fa-shield-alt"></i>
                                    </button>
                                    <a href="{{ url_for('main.delete_file', file_id=file[0]) }}" class="bg-danger hover:bg-red-700 text-white p-2 rounded-lg transition duration-300 delete-btn" title="Delete">
                                        <i class="fas fa-trash"></i>
                                    </a>
                                </div>
                            </div>
                        </div>
                    {% endfor %}
                </div>
            {% else %}
                <!-- Empty State -->
                <div class="col-span-full text-center py-12" id="emptyState">
                    <div class="mx-auto w-24 h-24 rounded-full bg-blue-100 flex items-center justify-center mb-6">
                        <i class="fas fa-file-upload text-primary text-3xl"></i>
                    </div>
                    <h3 class="text-xl font-semibold mb-2">No files uploaded yet</h3>
                    <p class="text-gray-500 mb-6">Upload your first file using the upload area above</p>
                </div>
            {% endif %}
        </section>
    </main>

    <!-- Toast Notification (hidden by default) -->
    <div class="fixed bottom-6 right-6 z-50 toast hidden" id="toastNotification">
        <div class="bg-white rounded-lg shadow-lg p-4 flex items-center border-l-4 border-primary">
            <i class="fas fa-check-circle text-green-500 text-xl mr-3" id="toastIcon"></i>
            <div>
                <p class="font-medium" id="toastTitle">File uploaded successfully!</p>
                <p class="text-sm text-gray-500" id="toastMessage">Your file is now available for sharing</p>
            </div>
            <button class="ml-4 text-gray-500 hover:text-gray-700" onclick="hideToast()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    </div>

    <!-- Secure Share Modal -->
    <div id="shareModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 hidden flex items-center justify-center">
        <div class="bg-white rounded-2xl p-8 max-w-md w-full mx-4">
            <div class="text-center mb-6">
                <div class="w-16 h-16 rounded-2xl bg-green-100 flex items-center justify-center mx-auto mb-4">
                    <i class="fas fa-shield-alt text-green-600 text-2xl"></i>
                </div>
                <h2 class="text-2xl font-bold text-gray-800">Secure Share</h2>
                <p class="text-gray-600 mt-2">Create an encrypted share link</p>
            </div>

            <form id="shareForm">
                <input type="hidden" id="shareFileId" name="file_id">
                
                <div class="mb-4">
                    <label class="block text-sm font-medium text-gray-700 mb-2">File</label>
                    <div class="bg-gray-50 rounded-lg p-3">
                        <i class="fas fa-file text-primary mr-2"></i>
                        <span id="shareFileName" class="font-medium"></span>
                    </div>
                </div>

                <div class="mb-4">
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        <i class="fas fa-shield-alt mr-1"></i>Share Type
                    </label>
                    <select id="shareType" name="share_type" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary focus:border-transparent" onchange="togglePrivateShareOptions()">
                        <option value="public">🌐 Public Share - Anyone with link can access</option>
                        <option value="private">🔐 Quantum-Secure Private Share - Specific user only</option>
                    </select>
                </div>

                <div id="privateShareOptions" class="mb-4 hidden">
                    <label class="block text-sm font-medium text-gray-700 mb-2">
                        <i class="fas fa-user-lock mr-1"></i>Target User
                    </label>
                    <select id="targetUserId" name="target_user_id" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary focus:border-transparent">
                        <option value="">Select a user...</option>
                    </select>
                    <p class="text-xs text-gray-500 mt-1">The file will be encrypted with their Kyber public key</p>
                </div>

                <div class="mb-4">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Expires In</label>
                    <select name="expiry_hours" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary focus:border-transparent">
                        <option value="1">1 Hour</option>
                        <option value="6">6 Hours</option>
                        <option value="24" selected>24 Hours</option>
                        <option value="72">3 Days</option>
                        <option value="168">1 Week</option>
                    </select>
                </div>

                <div class="mb-6">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Max Downloads (Optional)</label>
                    <input type="number" name="max_downloads" min="1" max="100" placeholder="Unlimited" 
                           class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary focus:border-transparent">
                </div>

                <div class="flex space-x-3">
                    <button type="button" onclick="closeShareModal()" 
                            class="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 py-2 px-4 rounded-lg font-medium transition duration-300">
                        Cancel
                    </button>
                    <button type="submit" 
                            class="flex-1 bg-primary hover:bg-secondary text-white py-2 px-4 rounded-lg font-medium transition duration-300">
                        <i class="fas fa-share mr-2"></i>Create Share
                    </button>
                </div>
            </form>
        </div>
    </div>

    <!-- Share Success Modal -->
    <div id="shareSuccessModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 hidden flex items-center justify-center">
        <div class="bg-white rounded-2xl p-8 max-w-md w-full mx-4">
            <div class="text-center mb-6">
                <div class="w-16 h-16 rounded-2xl bg-green-100 flex items-center justify-center mx-auto mb-4">
                    <i class="fas fa-check-circle text-green-600 text-2xl"></i>
                </div>
                <h2 class="text-2xl font-bold text-gray-800">Share Created!</h2>
                <p class="text-gray-600 mt-2">Your secure share link is ready</p>
            </div>

            <div class="mb-6">
                <label class="block text-sm font-medium text-gray-700 mb-2">Share URL</label>
                <div class="flex">
                    <input type="text" id="shareUrlDisplay" readonly 
                           class="flex-1 bg-gray-50 border border-gray-300 rounded-l-lg px-3 py-2 text-sm">
                    <button onclick="copyShareUrl()" 
                            class="bg-primary hover:bg-secondary text-white px-4 py-2 rounded-r-lg transition duration-300">
                        <i class="fas fa-copy"></i>
                    </button>
                </div>
            </div>

            <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <div class="flex items-start">
                    <i class="fas fa-info-circle text-blue-600 mt-1 mr-3"></i>
                    <div>
                        <h4 class="font-semibold text-blue-800">Security Note</h4>
                        <p class="text-sm text-blue-700 mt-1">
                            This link contains an embedded encryption key. Recipients will get the decrypted file 
                            but cannot see the encryption key.
                        </p>
                    </div>
                </div>
            </div>

            <button onclick="closeShareSuccessModal()" 
                    class="w-full bg-primary hover:bg-secondary text-white py-2 px-4 rounded-lg font-medium transition duration-300">
                Done
            </button>
        </div>
    </div>

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

    <script>
        // Drag and drop functionality
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');
        const uploadForm = document.getElementById('uploadForm');
        
        // Handle file input change
        fileInput.addEventListener('change', function() {
            if (this.files.length) {
                handleFileUpload(this.files[0]);
            }
        });
        
        // Drag and drop events
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, unhighlight, false);
        });
        
        function highlight() {
            dropZone.classList.add('dragover');
        }
        
        function unhighlight() {
            dropZone.classList.remove('dragover');
        }
        
        dropZone.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0) {
                fileInput.files = files;
                handleFileUpload(files[0]);
            }
        }
        
        function handleFileUpload(file) {
            // Show upload progress
            const uploadProgress = document.getElementById('uploadProgress');
            const uploadFileName = document.getElementById('uploadFileName');
            const uploadPercent = document.getElementById('uploadPercent');
            const progressFill = document.getElementById('progressFill');
            
            uploadFileName.textContent = `Uploading: ${file.name}`;
            uploadProgress.classList.remove('hidden');
            
            // Submit the form after showing progress
            setTimeout(() => {
                uploadForm.submit();
            }, 500);
        }
        
        // Secure sharing functions
        let availableUsers = [];
        
        // Load available users for private sharing
        async function loadUsers() {
            try {
                const response = await fetch('/api/users');
                availableUsers = await response.json();
            } catch (error) {
                console.error('Failed to load users:', error);
            }
        }
        
        // Load users on page load
        loadUsers();
        
        function togglePrivateShareOptions() {
            const shareType = document.getElementById('shareType').value;
            const privateOptions = document.getElementById('privateShareOptions');
            const targetUserSelect = document.getElementById('targetUserId');
            
            if (shareType === 'private') {
                privateOptions.classList.remove('hidden');
                
                // Populate user dropdown
                targetUserSelect.innerHTML = '<option value="">Select a user...</option>';
                availableUsers.forEach(user => {
                    const option = document.createElement('option');
                    option.value = user.id;
                    option.textContent = `${user.username} (${user.email})`;
                    targetUserSelect.appendChild(option);
                });
            } else {
                privateOptions.classList.add('hidden');
            }
        }
        
        function openShareModal(fileId, filename) {
            document.getElementById('shareFileId').value = fileId;
            document.getElementById('shareFileName').textContent = filename;
            document.getElementById('shareType').value = 'public';
            togglePrivateShareOptions();
            document.getElementById('shareModal').classList.remove('hidden');
        }

        function closeShareModal() {
            document.getElementById('shareModal').classList.add('hidden');
        }

        function closeShareSuccessModal() {
            document.getElementById('shareSuccessModal').classList.add('hidden');
        }

        function copyShareUrl() {
            const urlInput = document.getElementById('shareUrlDisplay');
            urlInput.select();
            navigator.clipboard.writeText(urlInput.value).then(() => {
                showToast('URL Copied!', 'Share URL copied to clipboard', 'success');
            });
        }

        // Handle share form submission
        document.getElementById('shareForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const shareType = document.getElementById('shareType').value;
            const targetUserId = document.getElementById('targetUserId').value;
            
            // Validate private share requirements
            if (shareType === 'private' && !targetUserId) {
                showToast('Validation Error', 'Please select a target user for private share', 'error');
                return;
            }
            
            const formData = new FormData();
            formData.append('file_id', document.getElementById('shareFileId').value);
            formData.append('expiry_hours', this.expiry_hours.value);
            formData.append('share_type', shareType);
            
            if (this.max_downloads.value) {
                formData.append('max_downloads', this.max_downloads.value);
            }
            
            if (shareType === 'private') {
                formData.append('target_user_id', targetUserId);
                // Note: For private shares, password would be collected when claiming, not here
            }

            try {
                const response = await fetch('/create-share', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (result.success) {
                    closeShareModal();
                    
                    if (shareType === 'private') {
                        // For private shares, show different message
                        showToast('Private Share Created', result.message, 'success');
                        // Optionally copy the link to clipboard
                        navigator.clipboard.writeText(result.share_url).then(() => {
                            showToast('Link Copied', 'Private share link copied to clipboard', 'success');
                        });
                    } else {
                        document.getElementById('shareUrlDisplay').value = result.share_url;
                        document.getElementById('shareSuccessModal').classList.remove('hidden');
                    }
                } else {
                    showToast('Share Failed', result.message, 'error');
                }
            } catch (error) {
                showToast('Share Failed', 'Network error occurred', 'error');
            }
        });
        
        // Legacy share function (kept for compatibility)
        function shareFile(filename) {
            const url = window.location.href;
            if (navigator.share) {
                navigator.share({
                    title: 'File Share',
                    text: `Check out this file: ${filename}`,
                    url: url
                });
            } else {
                // Fallback: copy to clipboard
                navigator.clipboard.writeText(url).then(() => {
                    showToast('Link copied to clipboard!', 'Link copied successfully', 'success');
                });
            }
        }
        
        // Toast notification functions
        function showToast(title, message, type = 'success') {
            const toast = document.getElementById('toastNotification');
            const toastIcon = document.getElementById('toastIcon');
            const toastTitle = document.getElementById('toastTitle');
            const toastMessage = document.getElementById('toastMessage');
            
            toastTitle.textContent = title;
            toastMessage.textContent = message;
            
            // Set icon based on type
            if (type === 'success') {
                toastIcon.className = 'fas fa-check-circle text-green-500 text-xl mr-3';
            } else if (type === 'error') {
                toastIcon.className = 'fas fa-exclamation-circle text-red-500 text-xl mr-3';
            }
            
            toast.classList.remove('hidden');
            toast.classList.add('show');
            
            // Auto hide after 5 seconds
            setTimeout(() => {
                hideToast();
            }, 5000);
        }
        
        function hideToast() {
            const toast = document.getElementById('toastNotification');
            toast.classList.remove('show');
            setTimeout(() => {
                toast.classList.add('hidden');
            }, 300);
        }
        
        // Close buttons for flash messages
        document.querySelectorAll('.close-flash').forEach(button => {
            button.addEventListener('click', function() {
                this.closest('.flash-success, .flash-error').style.display = 'none';
            });
        });
        
        // Delete button confirmation
        document.querySelectorAll('.delete-btn').forEach(button => {
            button.addEventListener('click', function(e) {
                if (!confirm('Are you sure you want to delete this file?')) {
                    e.preventDefault();
                }
            });
        });
        
        // File type detection for icons
        function getFileIcon(filename) {
            const ext = filename.split('.').pop().toLowerCase();
            const iconMap = {
                pdf: 'fa-file-pdf',
                doc: 'fa-file-word',
                docx: 'fa-file-word',
                xls: 'fa-file-excel',
                xlsx: 'fa-file-excel',
                ppt: 'fa-file-powerpoint',
                pptx: 'fa-file-powerpoint',
                jpg: 'fa-file-image',
                jpeg: 'fa-file-image',
                png: 'fa-file-image',
                gif: 'fa-file-image',
                mp4: 'fa-file-video',
                avi: 'fa-file-video',
                mov: 'fa-file-video',
                mp3: 'fa-file-audio',
                wav: 'fa-file-audio',
                zip: 'fa-file-archive',
                rar: 'fa-file-archive',
                '7z': 'fa-file-archive'
            };
            return iconMap[ext] || 'fa-file';
        }
        
        // Initialize page
        document.addEventListener('DOMContentLoaded', function() {
            // Show toast if there are flash messages
            const flashMessages = document.querySelectorAll('.flash-success, .flash-error');
            if (flashMessages.length > 0) {
                const firstMessage = flashMessages[0];
                const isSuccess = firstMessage.classList.contains('flash-success');
                const title = firstMessage.querySelector('p').textContent;
                showToast(title, isSuccess ? 'Operation completed successfully' : 'Please try again', isSuccess ? 'success' : 'error');
            }
            
            // Filter and Sort dropdown functionality
            setupDropdowns();
            setupFilterAndSort();
        });
        
        // Setup dropdown menus
        function setupDropdowns() {
            const filterBtn = document.getElementById('filterBtn');
            const filterDropdown = document.getElementById('filterDropdown');
            const sortBtn = document.getElementById('sortBtn');
            const sortDropdown = document.getElementById('sortDropdown');
            
            // Filter dropdown toggle
            filterBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                filterDropdown.classList.toggle('hidden');
                sortDropdown.classList.add('hidden');
            });
            
            // Sort dropdown toggle
            sortBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                sortDropdown.classList.toggle('hidden');
                filterDropdown.classList.add('hidden');
            });
            
            // Close dropdowns when clicking outside
            document.addEventListener('click', function() {
                filterDropdown.classList.add('hidden');
                sortDropdown.classList.add('hidden');
            });
        }
        
        // Setup filter and sort functionality
        function setupFilterAndSort() {
            const fileCards = document.querySelectorAll('.file-card');
            
            // Filter functionality
            document.querySelectorAll('.filter-option').forEach(option => {
                option.addEventListener('click', function() {
                    const filterType = this.dataset.filter;
                    filterFiles(filterType, fileCards);
                    document.getElementById('filterDropdown').classList.add('hidden');
                });
            });
            
            // Sort functionality
            document.querySelectorAll('.sort-option').forEach(option => {
                option.addEventListener('click', function() {
                    const sortType = this.dataset.sort;
                    sortFiles(sortType, fileCards);
                    document.getElementById('sortDropdown').classList.add('hidden');
                });
            });
        }
        
        // Filter files function
        function filterFiles(filterType, fileCards) {
            fileCards.forEach(card => {
                const filename = card.querySelector('h3').textContent.toLowerCase();
                const ext = filename.split('.').pop();
                let show = true;
                
                switch(filterType) {
                    case 'pdf':
                        show = ext === 'pdf';
                        break;
                    case 'image':
                        show = ['jpg', 'jpeg', 'png', 'gif', 'bmp'].includes(ext);
                        break;
                    case 'video':
                        show = ['mp4', 'avi', 'mov', 'wmv', 'flv'].includes(ext);
                        break;
                    case 'archive':
                        show = ['zip', 'rar', '7z', 'tar'].includes(ext);
                        break;
                    case 'document':
                        show = ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'].includes(ext);
                        break;
                    case 'all':
                    default:
                        show = true;
                        break;
                }
                
                card.style.display = show ? 'block' : 'none';
            });
        }
        
        // Sort files function
        function sortFiles(sortType, fileCards) {
            const container = document.querySelector('.grid');
            const cardsArray = Array.from(fileCards);
            
            cardsArray.sort((a, b) => {
                const aName = a.querySelector('h3').textContent;
                const bName = b.querySelector('h3').textContent;
                const aSizeText = a.querySelector('.text-gray-500').textContent;
                const bSizeText = b.querySelector('.text-gray-500').textContent;
                
                switch(sortType) {
                    case 'name-asc':
                        return aName.localeCompare(bName);
                    case 'name-desc':
                        return bName.localeCompare(aName);
                    case 'size-asc':
                        return getSizeInBytes(aSizeText) - getSizeInBytes(bSizeText);
                    case 'size-desc':
                        return getSizeInBytes(bSizeText) - getSizeInBytes(aSizeText);
                    case 'date-asc':
                    case 'date-desc':
                        // For date sorting, we'd need timestamp data from backend
                        return sortType === 'date-asc' ? aName.localeCompare(bName) : bName.localeCompare(aName);
                    default:
                        return 0;
                }
            });
            
            // Re-append sorted cards
            cardsArray.forEach(card => container.appendChild(card));
        }
        
        // Helper function to convert size text to bytes for sorting
        function getSizeInBytes(sizeText) {
            const parts = sizeText.trim().split(' ');
            if (parts.length < 2) return 0;
            
            const size = parseFloat(parts[0]);
            const unit = parts[1].toLowerCase();
            
            switch(unit) {
                case 'kb': return size * 1024;
                case 'mb': return size * 1024 * 1024;
                case 'gb': return size * 1024 * 1024 * 1024;
                default: return size;
            }
        }
    </script>
</body>
</html>
'''
