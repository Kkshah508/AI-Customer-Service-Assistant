import sys
import os
import subprocess

def check_python_version():
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"[OK] Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"[ERROR] Python {version.major}.{version.minor} - Need 3.9+")
        return False

def check_node():
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] Node.js {result.stdout.strip()}")
            return True
    except:
        pass
    print("[ERROR] Node.js not found - Install from https://nodejs.org/")
    return False

def check_npm():
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] npm {result.stdout.strip()}")
            return True
    except:
        pass
    print("[ERROR] npm not found")
    return False

def check_dependencies():
    try:
        import flask
        import transformers
        import torch
        print("[OK] Core Python packages installed")
        return True
    except ImportError as e:
        print(f"[ERROR] Missing Python packages: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def check_env_file():
    if os.path.exists('.env'):
        print("[OK] .env file exists")
        return True
    else:
        print("[WARNING] No .env file - copy .env.example to .env")
        return False

def check_database():
    try:
        from src.database import Database
        db = Database("test_verify.db")
        db.close()
        if os.path.exists("test_verify.db"):
            os.remove("test_verify.db")
        print("[OK] Database module working")
        return True
    except Exception as e:
        print(f"[ERROR] Database check failed: {e}")
        return False

def check_frontend():
    frontend_path = os.path.join("frontend", "react-app", "package.json")
    if os.path.exists(frontend_path):
        print("[OK] React frontend found")
        node_modules = os.path.join("frontend", "react-app", "node_modules")
        if os.path.exists(node_modules):
            print("[OK] Frontend dependencies installed")
            return True
        else:
            print("[WARNING] Frontend dependencies not installed")
            print("Run: cd frontend/react-app && npm install")
            return False
    else:
        print("[ERROR] React frontend not found")
        return False

def main():
    print("=" * 60)
    print("AI Customer Service Assistant - Setup Verification")
    print("=" * 60)
    print()
    
    checks = []
    
    print("Checking Python...")
    checks.append(check_python_version())
    
    print("\nChecking Node.js...")
    checks.append(check_node())
    checks.append(check_npm())
    
    print("\nChecking Python dependencies...")
    checks.append(check_dependencies())
    
    print("\nChecking environment...")
    check_env_file()
    
    print("\nChecking database...")
    checks.append(check_database())
    
    print("\nChecking frontend...")
    checks.append(check_frontend())
    
    print("\n" + "=" * 60)
    if all(checks):
        print("[SUCCESS] All critical checks passed!")
        print("You can now run: START_APP.bat")
    else:
        print("[WARNING] Some checks failed - see above for details")
        print("Fix the issues and run this script again")
    print("=" * 60)

if __name__ == "__main__":
    main()
