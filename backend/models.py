"""
Database models for Pain Point Discovery Engine.

This module provides Python classes for interacting with the SQLite database.
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from contextlib import contextmanager


def get_db_path():
    """Get database path from environment or use default."""
    return os.getenv('DATABASE_PATH', 'data/ppde.db')


@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    try:
        yield conn
    finally:
        conn.close()


class Tweet:
    """Model for tweets table."""

    @staticmethod
    def create(tweet_id: str, text: str, created_at: str, author_username: str = None,
               author_followers: int = 0, likes: int = 0, retweets: int = 0,
               replies: int = 0) -> int:
        """Create a new tweet record."""

        engagement_score = likes + (retweets * 2)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tweets
                (tweet_id, text, created_at, author_username, author_followers,
                 likes, retweets, replies, engagement_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (tweet_id, text, created_at, author_username, author_followers,
                  likes, retweets, replies, engagement_score))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def get_by_id(tweet_id: int) -> Optional[Dict]:
        """Get tweet by internal ID."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tweets WHERE id = ?", (tweet_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def get_by_tweet_id(tweet_id: str) -> Optional[Dict]:
        """Get tweet by Twitter's tweet_id."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tweets WHERE tweet_id = ?", (tweet_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def exists(tweet_id: str) -> bool:
        """Check if tweet already exists."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM tweets WHERE tweet_id = ?", (tweet_id,))
            return cursor.fetchone() is not None

    @staticmethod
    def get_recent(limit: int = 100) -> List[Dict]:
        """Get most recent tweets."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM tweets
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def count_today() -> int:
        """Count tweets collected today."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM tweets
                WHERE DATE(collected_at) = DATE('now')
            """)
            return cursor.fetchone()['count']


class PainAnalysis:
    """Model for pain_analysis table."""

    @staticmethod
    def create(tweet_id: int, frustration_score: int, budget_signal_score: int,
               products_mentioned: List[str] = None, pain_keywords: List[str] = None) -> int:
        """Create a pain analysis record."""

        products_json = json.dumps(products_mentioned or [])
        keywords_json = json.dumps(pain_keywords or [])

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO pain_analysis
                (tweet_id, frustration_score, budget_signal_score, products_mentioned, pain_keywords)
                VALUES (?, ?, ?, ?, ?)
            """, (tweet_id, frustration_score, budget_signal_score, products_json, keywords_json))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def get_by_tweet(tweet_id: int) -> Optional[Dict]:
        """Get pain analysis for a tweet."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pain_analysis WHERE tweet_id = ?", (tweet_id,))
            row = cursor.fetchone()
            if row:
                result = dict(row)
                result['products_mentioned'] = json.loads(result['products_mentioned'])
                result['pain_keywords'] = json.loads(result['pain_keywords'])
                return result
            return None


class Opportunity:
    """Model for opportunities table."""

    @staticmethod
    def create(title: str, description: str, score: int,
               first_seen: str = None, last_seen: str = None) -> int:
        """Create a new opportunity."""

        first_seen = first_seen or datetime.now().isoformat()
        last_seen = last_seen or datetime.now().isoformat()

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO opportunities
                (title, description, score, tweet_count, first_seen, last_seen)
                VALUES (?, ?, ?, 0, ?, ?)
            """, (title, description, score, first_seen, last_seen))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def get_by_id(opportunity_id: int) -> Optional[Dict]:
        """Get opportunity by ID."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM opportunities WHERE id = ?", (opportunity_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def get_top_opportunities(limit: int = 10, min_score: int = 40,
                               days: int = 1) -> List[Dict]:
        """Get top opportunities from recent days."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM opportunities
                WHERE score >= ?
                AND DATE(created_at) >= DATE('now', '-' || ? || ' days')
                ORDER BY score DESC, tweet_count DESC
                LIMIT ?
            """, (min_score, days, limit))
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def add_tweet(opportunity_id: int, tweet_id: int):
        """Link a tweet to an opportunity."""
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Add to junction table
            cursor.execute("""
                INSERT OR IGNORE INTO opportunity_tweets (opportunity_id, tweet_id)
                VALUES (?, ?)
            """, (opportunity_id, tweet_id))

            # Update tweet count
            cursor.execute("""
                UPDATE opportunities
                SET tweet_count = (
                    SELECT COUNT(*) FROM opportunity_tweets
                    WHERE opportunity_id = ?
                )
                WHERE id = ?
            """, (opportunity_id, opportunity_id))

            conn.commit()

    @staticmethod
    def get_tweets(opportunity_id: int) -> List[Dict]:
        """Get all tweets for an opportunity."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.* FROM tweets t
                JOIN opportunity_tweets ot ON t.id = ot.tweet_id
                WHERE ot.opportunity_id = ?
                ORDER BY t.engagement_score DESC
            """, (opportunity_id,))
            return [dict(row) for row in cursor.fetchall()]


class User:
    """Model for users table."""

    @staticmethod
    def create(email: str, password_hash: str) -> int:
        """Create a new user."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (email, password_hash)
                VALUES (?, ?)
            """, (email, password_hash))
            conn.commit()

            # Create default email preferences
            user_id = cursor.lastrowid
            cursor.execute("""
                INSERT INTO email_preferences (user_id)
                VALUES (?)
            """, (user_id,))
            conn.commit()

            return user_id

    @staticmethod
    def get_by_email(email: str) -> Optional[Dict]:
        """Get user by email."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def get_by_id(user_id: int) -> Optional[Dict]:
        """Get user by ID."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def update_last_login(user_id: int):
        """Update last login timestamp."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users
                SET last_login = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (user_id,))
            conn.commit()


class Watchlist:
    """Model for watchlist table."""

    @staticmethod
    def add(user_id: int, opportunity_id: int, notes: str = None):
        """Add opportunity to user's watchlist."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO watchlist (user_id, opportunity_id, notes)
                VALUES (?, ?, ?)
            """, (user_id, opportunity_id, notes))
            conn.commit()

    @staticmethod
    def remove(user_id: int, opportunity_id: int):
        """Remove opportunity from watchlist."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM watchlist
                WHERE user_id = ? AND opportunity_id = ?
            """, (user_id, opportunity_id))
            conn.commit()

    @staticmethod
    def get_for_user(user_id: int) -> List[Dict]:
        """Get all watchlist items for a user."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT o.*, w.added_at, w.notes
                FROM opportunities o
                JOIN watchlist w ON o.id = w.opportunity_id
                WHERE w.user_id = ?
                ORDER BY w.added_at DESC
            """, (user_id,))
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def is_saved(user_id: int, opportunity_id: int) -> bool:
        """Check if opportunity is in user's watchlist."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 1 FROM watchlist
                WHERE user_id = ? AND opportunity_id = ?
            """, (user_id, opportunity_id))
            return cursor.fetchone() is not None


class EmailPreferences:
    """Model for email_preferences table."""

    @staticmethod
    def get(user_id: int) -> Optional[Dict]:
        """Get email preferences for user."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM email_preferences WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def update(user_id: int, enabled: bool = None, frequency: str = None,
               min_score: int = None):
        """Update email preferences."""
        with get_db_connection() as conn:
            cursor = conn.cursor()

            updates = []
            params = []

            if enabled is not None:
                updates.append("enabled = ?")
                params.append(1 if enabled else 0)

            if frequency is not None:
                updates.append("frequency = ?")
                params.append(frequency)

            if min_score is not None:
                updates.append("min_score = ?")
                params.append(min_score)

            if updates:
                params.append(user_id)
                query = f"UPDATE email_preferences SET {', '.join(updates)} WHERE user_id = ?"
                cursor.execute(query, params)
                conn.commit()

    @staticmethod
    def mark_sent(user_id: int):
        """Mark digest as sent for user."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE email_preferences
                SET last_sent = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (user_id,))
            conn.commit()

    @staticmethod
    def get_users_for_digest() -> List[Dict]:
        """Get all users who should receive daily digest."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.*, ep.*
                FROM users u
                JOIN email_preferences ep ON u.id = ep.user_id
                WHERE ep.enabled = 1
                AND ep.frequency = 'daily'
                AND (ep.last_sent IS NULL OR DATE(ep.last_sent) < DATE('now'))
            """)
            return [dict(row) for row in cursor.fetchall()]
