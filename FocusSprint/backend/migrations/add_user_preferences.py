"""
Database migration: Add user preferences columns.

This migration adds:
- preferences (JSON) - Stores all user preferences
- onboarding_completed (Boolean) - Tracks onboarding status

Run with: alembic upgrade head
Or manually execute the SQL below.
"""

# For Alembic migration
def upgrade():
    """Add user preferences columns."""
    from alembic import op
    import sqlalchemy as sa
    
    # Add preferences JSON column
    op.add_column('users', sa.Column('preferences', sa.JSON(), nullable=True))
    
    # Add onboarding_completed boolean column
    op.add_column('users', sa.Column('onboarding_completed', sa.Boolean(), default=False))
    
    # Set default values for existing users
    op.execute("UPDATE users SET preferences = '{}' WHERE preferences IS NULL")
    op.execute("UPDATE users SET onboarding_completed = false WHERE onboarding_completed IS NULL")


def downgrade():
    """Remove user preferences columns."""
    from alembic import op
    
    op.drop_column('users', 'preferences')
    op.drop_column('users', 'onboarding_completed')


# ============ Manual SQL Migration ============
# If not using Alembic, run this SQL directly:

MANUAL_SQL = """
-- Add preferences column (JSON/JSONB for PostgreSQL, TEXT for SQLite)
ALTER TABLE users ADD COLUMN preferences TEXT DEFAULT '{}';

-- Add onboarding_completed column
ALTER TABLE users ADD COLUMN onboarding_completed BOOLEAN DEFAULT FALSE;

-- Update existing users
UPDATE users SET preferences = '{}' WHERE preferences IS NULL;
UPDATE users SET onboarding_completed = FALSE WHERE onboarding_completed IS NULL;
"""

# For SQLite specifically (which the app uses locally):
SQLITE_SQL = """
-- SQLite version
ALTER TABLE users ADD COLUMN preferences TEXT DEFAULT '{}';
ALTER TABLE users ADD COLUMN onboarding_completed INTEGER DEFAULT 0;
"""

if __name__ == "__main__":
    print("=== Database Migration: User Preferences ===")
    print("\nFor SQLite (local development):")
    print(SQLITE_SQL)
    print("\nFor PostgreSQL (production):")
    print(MANUAL_SQL)
