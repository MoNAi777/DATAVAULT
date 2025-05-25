#!/usr/bin/env python3
"""
Basic test script for DataVault backend
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test basic imports"""
    print("🔍 Testing imports...")
    
    try:
        import fastapi
        print("✅ FastAPI")
    except ImportError as e:
        print(f"❌ FastAPI: {e}")
        return False
    
    try:
        from config.settings import settings
        print("✅ Settings")
    except ImportError as e:
        print(f"❌ Settings: {e}")
        return False
    
    try:
        from app.schemas.message import MessageCreate, MessageResponse
        print("✅ Schemas")
    except ImportError as e:
        print(f"❌ Schemas: {e}")
        return False
    
    try:
        from app.models.message import Message
        print("✅ Models")
    except ImportError as e:
        print(f"❌ Models: {e}")
        return False
    
    return True

def test_settings():
    """Test settings configuration"""
    print("\n⚙️ Testing settings...")
    
    try:
        from config.settings import settings
        
        print(f"App name: {settings.app_name}")
        print(f"Version: {settings.app_version}")
        print(f"Debug: {settings.debug}")
        
        # Check if API keys are set
        if settings.openai_api_key:
            print("✅ OpenAI API key configured")
        else:
            print("⚠️ OpenAI API key not set")
        
        if settings.telegram_bot_token:
            print("✅ Telegram bot token configured")
        else:
            print("⚠️ Telegram bot token not set")
        
        return True
    except Exception as e:
        print(f"❌ Settings error: {e}")
        return False

def test_fastapi_app():
    """Test FastAPI app creation"""
    print("\n🚀 Testing FastAPI app...")
    
    try:
        from app.main import app
        print("✅ FastAPI app created")
        
        # Check routes
        routes = [route.path for route in app.routes]
        print(f"Available routes: {len(routes)}")
        
        if "/health" in routes:
            print("✅ Health endpoint found")
        else:
            print("❌ Health endpoint missing")
        
        return True
    except Exception as e:
        print(f"❌ FastAPI app error: {e}")
        return False

def test_database_models():
    """Test database model creation"""
    print("\n💾 Testing database models...")
    
    try:
        from app.models.message import Message
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        # Create in-memory SQLite database for testing
        engine = create_engine("sqlite:///:memory:")
        Message.metadata.create_all(engine)
        
        print("✅ Database models created")
        return True
    except Exception as e:
        print(f"❌ Database models error: {e}")
        return False

def main():
    """Run all tests"""
    print("🤖 DataVault Basic Test Suite")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_settings,
        test_fastapi_app,
        test_database_models
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 40)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend is ready.")
        return True
    else:
        print("❌ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 