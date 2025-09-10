#!/usr/bin/env python3
"""
Deployment Check Script for Strategy Agent 3.0
This script helps verify that all required files and dependencies are properly deployed.
"""

import os
import sys
import subprocess
import importlib.util

def check_file_exists(filepath, description):
    """Check if a file exists and log the result"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - NOT FOUND")
        return False

def check_directory_exists(dirpath, description):
    """Check if a directory exists and log the result"""
    if os.path.isdir(dirpath):
        print(f"✅ {description}: {dirpath}")
        return True
    else:
        print(f"❌ {description}: {dirpath} - NOT FOUND")
        return False

def check_python_package(package_name):
    """Check if a Python package is installed"""
    try:
        spec = importlib.util.find_spec(package_name)
        if spec is not None:
            print(f"✅ Python package: {package_name}")
            return True
        else:
            print(f"❌ Python package: {package_name} - NOT INSTALLED")
            return False
    except ImportError:
        print(f"❌ Python package: {package_name} - NOT INSTALLED")
        return False

def run_command(command, description):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description}")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description}")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} - Exception: {str(e)}")
        return False

def main():
    """Main deployment check function"""
    print("🔍 Strategy Agent 3.0 - Deployment Check")
    print("=" * 50)
    
    # Check current working directory
    print(f"📁 Current working directory: {os.getcwd()}")
    print(f"📁 Files in current directory: {', '.join(os.listdir('.'))}")
    print()
    
    # Check required files
    print("📄 Checking required files...")
    required_files = [
        ("main.py", "Main application file"),
        ("api_endpoint.py", "API endpoint file"),
        ("pdf_report_generator.py", "PDF report generator"),
        ("requirements.txt", "Python dependencies file"),
        ("api_keys.env", "API keys configuration"),
    ]
    
    files_ok = True
    for filepath, description in required_files:
        if not check_file_exists(filepath, description):
            files_ok = False
    
    print()
    
    # Check required directories
    print("📁 Checking required directories...")
    required_dirs = [
        ("data", "Data directory"),
        ("recommendations", "Recommendations directory"),
        ("reports", "Reports directory"),
    ]
    
    dirs_ok = True
    for dirpath, description in required_dirs:
        if not check_directory_exists(dirpath, description):
            dirs_ok = False
    
    print()
    
    # Check Python packages
    print("🐍 Checking Python packages...")
    required_packages = [
        "pandas",
        "requests", 
        "fastapi",
        "uvicorn",
        "pydantic",
        "reportlab",  # This is the critical one for PDF generation
        "numpy",
        "dotenv"
    ]
    
    packages_ok = True
    for package in required_packages:
        if not check_python_package(package):
            packages_ok = False
    
    print()
    
    # Check if we can import the main modules
    print("🔧 Checking module imports...")
    try:
        from main import OptimizedRecommendationEngine
        print("✅ Main module import: OptimizedRecommendationEngine")
    except Exception as e:
        print(f"❌ Main module import: {str(e)}")
        packages_ok = False
    
    try:
        from pdf_report_generator import PDFReportGenerator
        print("✅ PDF generator import: PDFReportGenerator")
    except Exception as e:
        print(f"❌ PDF generator import: {str(e)}")
        packages_ok = False
    
    print()
    
    # Summary
    print("📊 Deployment Check Summary")
    print("=" * 30)
    print(f"Files: {'✅ OK' if files_ok else '❌ ISSUES FOUND'}")
    print(f"Directories: {'✅ OK' if dirs_ok else '❌ ISSUES FOUND'}")
    print(f"Packages: {'✅ OK' if packages_ok else '❌ ISSUES FOUND'}")
    
    if files_ok and dirs_ok and packages_ok:
        print("\n🎉 All checks passed! Your deployment looks good.")
        return 0
    else:
        print("\n⚠️  Issues found. Please fix the problems above.")
        print("\n💡 Common solutions:")
        print("   - Install missing packages: pip install -r requirements.txt")
        print("   - Ensure all files are uploaded to the correct directory")
        print("   - Check file permissions")
        return 1

if __name__ == "__main__":
    sys.exit(main())
