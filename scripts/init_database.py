#!/usr/bin/env python3
"""
Initialize the Pain Point Discovery Engine database.

This script creates the SQLite database with all necessary tables
for the CRAWL phase.
"""

import sqlite3
import os
from datetime import datetime


def get_db_path():
    """Get database path from environment or use default."""
    return os.getenv('DATABASE_PATH', 'data/ppde.db')


def init_database():
    """Initialize the database with all tables."""

    db_path = get_db_path()

    # Ensure data directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Connect to database (creates file if doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"Initializing database at: {db_path}")

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Table 1: Tweets - Raw collected data
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tweets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tweet_id TEXT UNIQUE NOT NULL,
            text TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            author_username TEXT,
            author_followers INTEGER,
            likes INTEGER DEFAULT 0,
            retweets INTEGER DEFAULT 0,
            replies INTEGER DEFAULT 0,
            engagement_score INTEGER,
            collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Indexes for tweets
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tweets_created_at ON tweets(created_at);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tweets_engagement ON tweets(engagement_score);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tweets_collected_at ON tweets(collected_at);")

    print("✓ Created tweets table")

    # Table 2: Pain Analysis - Extracted features
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pain_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tweet_id INTEGER NOT NULL,
            frustration_score INTEGER,
            budget_signal_score INTEGER,
            products_mentioned TEXT,
            pain_keywords TEXT,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (tweet_id) REFERENCES tweets(id) ON DELETE CASCADE
        );
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pain_tweet ON pain_analysis(tweet_id);")

    print("✓ Created pain_analysis table")

    # Table 3: Opportunities - Aggregated pain points
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            score INTEGER NOT NULL,
            tweet_count INTEGER DEFAULT 0,
            first_seen TIMESTAMP,
            last_seen TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_opportunities_score ON opportunities(score);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_opportunities_created ON opportunities(created_at);")

    print("✓ Created opportunities table")

    # Table 4: Opportunity Tweets - Many-to-many relationship
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS opportunity_tweets (
            opportunity_id INTEGER NOT NULL,
            tweet_id INTEGER NOT NULL,
            PRIMARY KEY (opportunity_id, tweet_id),
            FOREIGN KEY (opportunity_id) REFERENCES opportunities(id) ON DELETE CASCADE,
            FOREIGN KEY (tweet_id) REFERENCES tweets(id) ON DELETE CASCADE
        );
    """)

    print("✓ Created opportunity_tweets table")

    # Table 5: Users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            email_verified BOOLEAN DEFAULT 0
        );
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")

    print("✓ Created users table")

    # Table 6: Email Preferences
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_preferences (
            user_id INTEGER PRIMARY KEY,
            enabled BOOLEAN DEFAULT 1,
            frequency TEXT DEFAULT 'daily',
            min_score INTEGER DEFAULT 60,
            last_sent TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)

    print("✓ Created email_preferences table")

    # Table 7: Watchlist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS watchlist (
            user_id INTEGER NOT NULL,
            opportunity_id INTEGER NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            PRIMARY KEY (user_id, opportunity_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (opportunity_id) REFERENCES opportunities(id) ON DELETE CASCADE
        );
    """)

    print("✓ Created watchlist table")

    # Commit changes
    conn.commit()

    # Verify tables were created
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    print(f"\n✓ Database initialized successfully!")
    print(f"✓ Created {len(tables)} tables: {', '.join([t[0] for t in tables])}")
    print(f"✓ Location: {db_path}")

    conn.close()


def add_sample_data():
    """Add sample data for testing."""

    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("\nAdding sample data...")

    # Sample tweet
    cursor.execute("""
        INSERT OR IGNORE INTO tweets
        (tweet_id, text, created_at, author_username, author_followers, likes, retweets, replies, engagement_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        '1234567890',
        'I\'m paying $99/mo for Airtable and it STILL doesn\'t do what I need! Why is there no simple database for small teams???',
        datetime.now().isoformat(),
        'sample_user',
        4200,
        45,
        12,
        8,
        69  # 45 + (12 * 2)
    ))

    tweet_rowid = cursor.lastrowid

    # Sample pain analysis
    cursor.execute("""
        INSERT INTO pain_analysis
        (tweet_id, frustration_score, budget_signal_score, products_mentioned, pain_keywords)
        VALUES (?, ?, ?, ?, ?)
    """, (
        tweet_rowid,
        8,  # High frustration
        45,  # Has budget signals
        '["Airtable"]',
        '["STILL", "Why is there no", "$99/mo"]'
    ))

    # Sample opportunity
    cursor.execute("""
        INSERT INTO opportunities
        (title, description, score, tweet_count, first_seen, last_seen)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        'Simple database for small teams',
        'Users frustrated with complex/expensive database tools like Airtable for basic team needs',
        73,  # High score
        1,
        datetime.now().isoformat(),
        datetime.now().isoformat()
    ))

    opportunity_id = cursor.lastrowid

    # Link tweet to opportunity
    cursor.execute("""
        INSERT INTO opportunity_tweets (opportunity_id, tweet_id)
        VALUES (?, ?)
    """, (opportunity_id, tweet_rowid))

    conn.commit()
    print("✓ Added sample data")

    # Show what we created
    cursor.execute("SELECT * FROM tweets;")
    print(f"✓ Tweets: {len(cursor.fetchall())} records")

    cursor.execute("SELECT * FROM opportunities;")
    print(f"✓ Opportunities: {len(cursor.fetchall())} records")

    conn.close()


def show_schema():
    """Display the database schema."""

    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("\n" + "="*60)
    print("DATABASE SCHEMA")
    print("="*60)

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = cursor.fetchall()

    for (table_name,) in tables:
        print(f"\n{table_name}:")
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        for col in columns:
            col_id, name, type_, notnull, default, pk = col
            pk_marker = " [PK]" if pk else ""
            null_marker = " NOT NULL" if notnull else ""
            default_marker = f" DEFAULT {default}" if default else ""
            print(f"  - {name}: {type_}{pk_marker}{null_marker}{default_marker}")

    print("\n" + "="*60)

    conn.close()


if __name__ == "__main__":
    import sys

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    print("Pain Point Discovery Engine - Database Initialization")
    print("="*60)

    # Check if we should add sample data
    add_samples = '--with-samples' in sys.argv or '-s' in sys.argv
    show_schema_flag = '--show-schema' in sys.argv

    # Initialize database
    init_database()

    # Add sample data if requested
    if add_samples:
        add_sample_data()

    # Show schema if requested
    if show_schema_flag:
        show_schema()

    print("\n✓ Done!")
    print("\nUsage:")
    print("  python scripts/init_database.py              # Create empty database")
    print("  python scripts/init_database.py --with-samples   # Create with sample data")
    print("  python scripts/init_database.py --show-schema    # Show schema after creation")
