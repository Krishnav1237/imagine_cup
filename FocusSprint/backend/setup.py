"""
Setup script for ADHD Learning Platform Backend
Initializes database, creates test data, and verifies configuration
"""
import sys
import os
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import init_db, get_db, reset_db
from app.core.auth import get_password_hash
from app.models.models import User, ContentItem
from app.config import settings


def setup_database():
    """Initialize database and create tables"""
    print("🗄️  Setting up database...")
    init_db()
    print("✅ Database initialized")


def create_test_user():
    """Create a test user for development"""
    db = next(get_db())
    
    try:
        # Check if test user exists
        existing = db.query(User).filter(User.email == "test@example.com").first()
        
        if existing:
            print("ℹ️  Test user already exists")
            return
        
        # Create test user
        test_user = User(
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="Test User",
            is_active=True,
            default_chunk_length=180,
            preferred_difficulty="medium"
        )
        
        db.add(test_user)
        db.commit()
        
        print("✅ Created test user:")
        print("   Email: test@example.com")
        print("   Password: password123")
    
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        db.rollback()
    finally:
        db.close()


def verify_configuration():
    """Verify all required configuration"""
    print("\n🔍 Verifying configuration...")
    
    issues = []
    
    # Check deployment mode
    print(f"   Mode: {settings.DEPLOYMENT_MODE}")
    
    # Check database
    if settings.DATABASE_URL:
        print(f"   ✅ Database: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'SQLite'}")
    else:
        issues.append("Database URL not configured")
    
    # Check Anthropic API
    if settings.ANTHROPIC_API_KEY:
        print("   ✅ Anthropic API key configured")
    else:
        issues.append("ANTHROPIC_API_KEY not set - AI chunking will fail")
    
    # Check Azure settings (if in Azure mode)
    if settings.is_azure:
        if settings.AZURE_STORAGE_CONNECTION_STRING:
            print("   ✅ Azure Blob Storage configured")
        else:
            issues.append("Azure Storage not configured")
        
        if settings.AZURE_SPEECH_KEY:
            print("   ✅ Azure Speech Services configured")
        else:
            print("   ℹ️  Azure Speech not configured (will use Whisper)")
    
    # Check directories
    upload_dir = Path(settings.UPLOAD_DIR)
    if upload_dir.exists():
        print(f"   ✅ Upload directory: {upload_dir}")
    else:
        print(f"   📁 Creating upload directory: {upload_dir}")
        upload_dir.mkdir(parents=True, exist_ok=True)
    
    if issues:
        print("\n⚠️  Configuration issues:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("\n✅ Configuration looks good!")
    
    return len(issues) == 0


def print_quickstart():
    """Print quick start instructions"""
    print("\n" + "="*60)
    print("🎓 ADHD Learning Platform - Backend Setup Complete!")
    print("="*60)
    print("\n📚 Quick Start:")
    print("   1. Start the server:")
    print("      uvicorn app.main:app --reload")
    print("\n   2. Access the API docs:")
    print("      http://localhost:8000/docs")
    print("\n   3. Login with test account:")
    print("      Email: test@example.com")
    print("      Password: password123")
    print("\n   4. Your Next.js frontend should connect to:")
    print("      http://localhost:8000/api/v1")
    print("\n💡 Tips:")
    print("   - Set ANTHROPIC_API_KEY in .env for AI chunking")
    print("   - Use DEPLOYMENT_MODE=local for development")
    print("   - Check logs for any processing errors")
    print("\n" + "="*60 + "\n")


def main():
    """Main setup function"""
    print("\n🚀 Starting ADHD Learning Platform Setup\n")
    
    # Setup database
    setup_database()
    
    # Create test user
    create_test_user()
    
    # Verify configuration
    config_ok = verify_configuration()
    
    # Print quickstart
    print_quickstart()
    
    if not config_ok:
        print("⚠️  Some configuration issues detected.")
        print("The app will run but some features may not work.")
        print("Check the warnings above and update your .env file.\n")


if __name__ == "__main__":
    main()