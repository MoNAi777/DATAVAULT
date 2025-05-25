#!/usr/bin/env python3
"""
DataVault Setup and Test Script
"""

import os
import sys
import subprocess
import time
import requests
import json
from pathlib import Path


def check_requirements():
    """Check if required tools are installed"""
    print("🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ required")
        return False
    print("✅ Python version OK")
    
    # Check Docker
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        print("✅ Docker found")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker not found or not running")
        return False
    
    # Check Docker Compose
    try:
        subprocess.run(["docker-compose", "--version"], check=True, capture_output=True)
        print("✅ Docker Compose found")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker Compose not found")
        return False
    
    return True


def setup_environment():
    """Setup environment variables"""
    print("\n📝 Setting up environment...")
    
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    # Copy from template
    template = Path("backend/env.example")
    if template.exists():
        import shutil
        shutil.copy(template, env_file)
        print("✅ Created .env from template")
        print("⚠️  Please edit .env file with your API keys")
        return True
    else:
        print("❌ Template file not found")
        return False


def test_backend_standalone():
    """Test backend without Docker"""
    print("\n🧪 Testing backend standalone...")
    
    # Change to backend directory
    os.chdir("backend")
    
    try:
        # Install dependencies
        print("📦 Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed")
        
        # Test imports
        print("🔍 Testing imports...")
        test_imports = [
            "fastapi",
            "openai", 
            "chromadb",
            "sqlalchemy",
            "pydantic"
        ]
        
        for module in test_imports:
            try:
                __import__(module)
                print(f"✅ {module}")
            except ImportError as e:
                print(f"❌ {module}: {e}")
                return False
        
        print("✅ All imports successful")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        os.chdir("..")


def start_services():
    """Start Docker services"""
    print("\n🐳 Starting Docker services...")
    
    try:
        # Start services
        subprocess.run(["docker-compose", "up", "-d"], check=True)
        print("✅ Services started")
        
        # Wait for services to be ready
        print("⏳ Waiting for services to start...")
        time.sleep(30)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting services: {e}")
        return False


def test_services():
    """Test if services are responding"""
    print("\n🔗 Testing service endpoints...")
    
    services = [
        ("PostgreSQL", "postgresql://datavault:datavault@localhost:5432/datavault"),
        ("Redis", "redis://localhost:6379"),
        ("ChromaDB", "http://localhost:8000/api/v1/heartbeat"),
        ("MinIO", "http://localhost:9000/minio/health/live"),
        ("Backend API", "http://localhost:8080/health")
    ]
    
    for name, url in services:
        try:
            if url.startswith("http"):
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    print(f"✅ {name}")
                else:
                    print(f"❌ {name}: Status {response.status_code}")
            else:
                print(f"⚠️  {name}: Cannot test non-HTTP service")
        except Exception as e:
            print(f"❌ {name}: {e}")


def test_api_endpoints():
    """Test API functionality"""
    print("\n🚀 Testing API endpoints...")
    
    base_url = "http://localhost:8080"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health endpoint")
        else:
            print(f"❌ Health endpoint: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint: {e}")
        return False
    
    # Test message creation (if OpenAI key is available)
    test_message = {
        "content": "This is a test message about Bitcoin and cryptocurrency",
        "source_type": "test",
        "sender_name": "Test User"
    }
    
    try:
        response = requests.post(f"{base_url}/api/messages/", json=test_message)
        if response.status_code == 200:
            print("✅ Message creation")
            message_data = response.json()
            message_id = message_data.get("id")
            
            # Test message retrieval
            response = requests.get(f"{base_url}/api/messages/{message_id}")
            if response.status_code == 200:
                print("✅ Message retrieval")
            else:
                print(f"❌ Message retrieval: {response.status_code}")
                
        else:
            print(f"⚠️  Message creation: {response.status_code} (may need API keys)")
    except Exception as e:
        print(f"⚠️  Message creation: {e} (may need API keys)")
    
    return True


def main():
    """Main setup and test function"""
    print("🤖 DataVault Setup & Test Script")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements check failed")
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        print("\n❌ Environment setup failed")
        sys.exit(1)
    
    # Test backend standalone
    if not test_backend_standalone():
        print("\n❌ Backend test failed")
        sys.exit(1)
    
    # Ask user if they want to test with Docker
    print("\n" + "=" * 40)
    response = input("🐳 Test with Docker services? (y/N): ").lower()
    
    if response in ['y', 'yes']:
        # Start services
        if not start_services():
            print("\n❌ Service startup failed")
            sys.exit(1)
        
        # Test services
        test_services()
        
        # Test API
        test_api_endpoints()
        
        print("\n" + "=" * 40)
        print("🎉 Setup complete!")
        print("\n📖 Next steps:")
        print("1. Edit .env file with your API keys")
        print("2. Access API docs: http://localhost:8080/docs")
        print("3. Check health: http://localhost:8080/health")
        print("4. Create a Telegram bot for message forwarding")
        print("\n🛑 To stop services: docker-compose down")
    else:
        print("\n✅ Backend setup complete!")
        print("📖 To start services later: docker-compose up -d")


if __name__ == "__main__":
    main() 