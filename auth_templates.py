"""
Authentication templates for the File Sharing Application
"""

LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - FileShare</title>
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
    <div class="min-h-screen flex items-center justify-center">
        <div class="max-w-md w-full mx-4">
            <!-- Logo -->
            <div class="text-center mb-8">
                <div class="w-16 h-16 rounded-2xl bg-primary flex items-center justify-center mx-auto mb-4">
                    <i class="fas fa-cloud-upload-alt text-white text-2xl"></i>
                </div>
                <h1 class="text-3xl font-bold text-primary">File<span class="text-secondary">Share</span></h1>
                <p class="text-gray-600 mt-2">Secure file sharing platform</p>
            </div>

            <!-- Flash Messages -->
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    <div class="mb-6">
                        {% for category, message in messages %}
                            {% if category == 'error' %}
                                <div class="bg-red-100 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
                                    <i class="fas fa-exclamation-circle mr-2"></i>{{ message }}
                                </div>
                            {% elif category == 'success' %}
                                <div class="bg-green-100 border border-green-200 text-green-800 px-4 py-3 rounded-lg">
                                    <i class="fas fa-check-circle mr-2"></i>{{ message }}
                                </div>
                            {% endif %}
                        {% endfor %}
                    </div>
                {% endif %}
            {% endwith %}

            <!-- Login Form -->
            <div class="bg-white rounded-2xl shadow-lg p-8">
                <h2 class="text-2xl font-bold text-center mb-6">Welcome Back</h2>
                
                <form method="POST">
                    <div class="mb-4">
                        <label for="username" class="block text-gray-700 text-sm font-medium mb-2">
                            <i class="fas fa-user mr-2"></i>Username
                        </label>
                        <input type="text" id="username" name="username" required
                               class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                               placeholder="Enter your username">
                    </div>
                    
                    <div class="mb-6">
                        <label for="password" class="block text-gray-700 text-sm font-medium mb-2">
                            <i class="fas fa-lock mr-2"></i>Password
                        </label>
                        <input type="password" id="password" name="password" required
                               class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                               placeholder="Enter your password">
                    </div>
                    
                    <button type="submit" class="w-full bg-primary hover:bg-secondary text-white py-3 rounded-lg font-medium transition duration-300">
                        <i class="fas fa-sign-in-alt mr-2"></i>Sign In
                    </button>
                </form>
                
                <div class="mt-6 text-center">
                    <p class="text-gray-600">Don't have an account? 
                        <a href="{{ url_for('auth.signup') }}" class="text-primary hover:text-secondary font-medium">Sign up</a>
                    </p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''

SIGNUP_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sign Up - FileShare</title>
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
    <div class="min-h-screen flex items-center justify-center">
        <div class="max-w-md w-full mx-4">
            <!-- Logo -->
            <div class="text-center mb-8">
                <div class="w-16 h-16 rounded-2xl bg-primary flex items-center justify-center mx-auto mb-4">
                    <i class="fas fa-cloud-upload-alt text-white text-2xl"></i>
                </div>
                <h1 class="text-3xl font-bold text-primary">File<span class="text-secondary">Share</span></h1>
                <p class="text-gray-600 mt-2">Create your account</p>
            </div>

            <!-- Flash Messages -->
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    <div class="mb-6">
                        {% for category, message in messages %}
                            {% if category == 'error' %}
                                <div class="bg-red-100 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
                                    <i class="fas fa-exclamation-circle mr-2"></i>{{ message }}
                                </div>
                            {% elif category == 'success' %}
                                <div class="bg-green-100 border border-green-200 text-green-800 px-4 py-3 rounded-lg">
                                    <i class="fas fa-check-circle mr-2"></i>{{ message }}
                                </div>
                            {% endif %}
                        {% endfor %}
                    </div>
                {% endif %}
            {% endwith %}

            <!-- Signup Form -->
            <div class="bg-white rounded-2xl shadow-lg p-8">
                <h2 class="text-2xl font-bold text-center mb-6">Create Account</h2>
                
                <form method="POST">
                    <div class="mb-4">
                        <label for="username" class="block text-gray-700 text-sm font-medium mb-2">
                            <i class="fas fa-user mr-2"></i>Username
                        </label>
                        <input type="text" id="username" name="username" required
                               class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                               placeholder="Choose a username">
                    </div>
                    
                    <div class="mb-4">
                        <label for="email" class="block text-gray-700 text-sm font-medium mb-2">
                            <i class="fas fa-envelope mr-2"></i>Email
                        </label>
                        <input type="email" id="email" name="email" required
                               class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                               placeholder="Enter your email">
                    </div>
                    
                    <div class="mb-4">
                        <label for="password" class="block text-gray-700 text-sm font-medium mb-2">
                            <i class="fas fa-lock mr-2"></i>Password
                        </label>
                        <input type="password" id="password" name="password" required
                               class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                               placeholder="Create a password">
                    </div>
                    
                    <div class="mb-6">
                        <label for="confirm_password" class="block text-gray-700 text-sm font-medium mb-2">
                            <i class="fas fa-lock mr-2"></i>Confirm Password
                        </label>
                        <input type="password" id="confirm_password" name="confirm_password" required
                               class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                               placeholder="Confirm your password">
                    </div>
                    
                    <button type="submit" class="w-full bg-primary hover:bg-secondary text-white py-3 rounded-lg font-medium transition duration-300">
                        <i class="fas fa-user-plus mr-2"></i>Create Account
                    </button>
                </form>
                
                <div class="mt-6 text-center">
                    <p class="text-gray-600">Already have an account? 
                        <a href="{{ url_for('auth.login') }}" class="text-primary hover:text-secondary font-medium">Sign in</a>
                    </p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''
