#!/usr/bin/env python3
"""
Setup script for the AI-Powered Blog Writer Research Agent

This script helps set up the development environment and installs dependencies.
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"[*] {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"[+] {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[-] {description} failed:")
        print(f"   Error: {e.stderr}")
        return False


def main():
    """Main setup function."""
    print("Setting up AI-Powered Blog Writer System")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("[-] Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"[+] Python version: {sys.version}")
    
    # Create virtual environment
    if not Path("venv").exists():
        if not run_command("python -m venv venv", "Creating virtual environment"):
            sys.exit(1)
    else:
        print("[+] Virtual environment already exists")
    
    # Activate virtual environment and install dependencies
    if sys.platform == "win32":
        activate_script = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
    else:
        activate_script = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
    
    # Install dependencies
    if not run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip"):
        sys.exit(1)
    
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies"):
        sys.exit(1)
    
    # Create .env file if it doesn't exist
    if not Path(".env").exists():
        if Path(".env.example").exists():
            run_command("cp .env.example .env", "Creating .env file from template")
            print("[!] Please edit .env file and add your API keys")
        else:
            print("[!] No .env.example found, please create .env file manually")
    else:
        print("[+] .env file already exists")
    
    print("\n[+] Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file and add your API keys:")
    print("   BRAVE_API_KEY=your_brave_api_key")
    print("   GROQ_API_KEY=your_groq_api_key")
    print("   PEXELS_API_KEY=your_pexels_api_key")
    print("\n2. Activate the virtual environment:")
    if sys.platform == "win32":
        print("   .\\venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("\n3. Start the backend server:")
    print("   cd backend && python main.py")
    print("\n4. Start the frontend (in another terminal):")
    print("   cd frontend && npm install && npm run dev")
    
    print("\n[*] API Key Resources:")
    print("   Brave Search: https://brave.com/search/api/")
    print("   Groq: https://console.groq.com/keys")
    print("   Pexels: https://www.pexels.com/api/")


if __name__ == "__main__":
    main()
