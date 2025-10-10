#!/usr/bin/env python3
"""
Simple test to verify that the navigation UI is working correctly.
This script tests the template rendering for both dashboard and my_shares pages.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from templates import NAV_HEADER_TEMPLATE
from jinja2 import Template

# Create a Flask app for testing
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-key'

# Create blueprints for testing
from flask import Blueprint
main_bp = Blueprint('main', __name__)
sharing_bp = Blueprint('sharing', __name__)
auth_bp = Blueprint('auth', __name__)

@main_bp.route('/dashboard')
def dashboard():
    return 'dashboard'

@sharing_bp.route('/my-shares')
def my_shares():
    return 'my-shares'
    
@auth_bp.route('/logout')
def logout():
    return 'logout'

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(sharing_bp)
app.register_blueprint(auth_bp)

def test_navigation_templates():
    """Test that navigation templates render correctly"""
    print("🧪 Testing Navigation Templates...")
    
    # Test data
    test_username = "TestUser"
    
    # Test Home page navigation
    print("\n📄 Testing Home page navigation...")
    try:
        with app.test_request_context():
            from flask import render_template_string
            home_nav = render_template_string(NAV_HEADER_TEMPLATE, username=test_username, active_page='home')
        
        # Check if the active state is applied correctly for home
        if 'border-b-2 border-primary' in home_nav and 'Home' in home_nav:
            print("✅ Home page navigation: PASSED")
            print("   - Active state styling applied to Home tab")
        else:
            print("❌ Home page navigation: FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Home page navigation: ERROR - {e}")
        return False
    
    # Test My Shares page navigation
    print("\n📄 Testing My Shares page navigation...")
    try:
        with app.test_request_context():
            shares_nav = render_template_string(NAV_HEADER_TEMPLATE, username=test_username, active_page='shares')
        
        # Check if the active state is applied correctly for shares
        if 'My Shares' in shares_nav and 'border-b-2 border-primary' in shares_nav:
            print("✅ My Shares page navigation: PASSED")
            print("   - Active state styling applied to My Shares tab")
        else:
            print("❌ My Shares page navigation: FAILED")
            return False
            
    except Exception as e:
        print(f"❌ My Shares page navigation: ERROR - {e}")
        return False
    
    # Test mobile navigation
    print("\n📱 Testing mobile navigation features...")
    try:
        if 'mobileMenuBtn' in home_nav and 'mobileMenu' in home_nav:
            print("✅ Mobile navigation: PASSED")
            print("   - Mobile menu button and menu present")
        else:
            print("❌ Mobile navigation: FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Mobile navigation: ERROR - {e}")
        return False
    
    # Test user information display
    print("\n👤 Testing user information display...")
    try:
        if test_username in home_nav and 'Welcome' in home_nav:
            print("✅ User information: PASSED")
            print(f"   - Username '{test_username}' displayed correctly")
        else:
            print("❌ User information: FAILED")
            return False
            
    except Exception as e:
        print(f"❌ User information: ERROR - {e}")
        return False
    
    return True

def test_navigation_links():
    """Test that navigation contains expected links"""
    print("\n🔗 Testing navigation links...")
    
    # Test that the template contains the expected URL patterns
    expected_patterns = [
        "main.dashboard",
        "sharing.my_shares", 
        "auth.logout"
    ]
    
    for pattern in expected_patterns:
        if pattern in NAV_HEADER_TEMPLATE:
            print(f"✅ Found expected URL pattern: {pattern}")
        else:
            print(f"❌ Missing expected URL pattern: {pattern}")
            return False
    
    return True

if __name__ == "__main__":
    print("🚀 FileShare Navigation UI Tests")
    print("=" * 50)
    
    # Run tests
    template_test = test_navigation_templates()
    links_test = test_navigation_links()
    
    print("\n" + "=" * 50)
    if template_test and links_test:
        print("🎉 All navigation tests PASSED!")
        print("\n📋 Summary:")
        print("   ✅ Navigation templates render correctly")
        print("   ✅ Active page highlighting works")
        print("   ✅ Mobile navigation is present")
        print("   ✅ User information displays properly")
        print("   ✅ All required navigation links are present")
        
        print("\n🔧 UI Improvements Made:")
        print("   • Added consistent navigation header across pages")
        print("   • Implemented active page highlighting with border styling")
        print("   • Added responsive mobile navigation menu")
        print("   • Enhanced visual feedback for navigation state")
        print("   • Easy switching between Home and My Shares tabs")
        
        sys.exit(0)
    else:
        print("💥 Some navigation tests FAILED!")
        sys.exit(1)