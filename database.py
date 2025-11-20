import sqlite3
import os
from config import DB_PATH

class Database:
    def __init__(self):
        self.db_path = DB_PATH
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                telegram_id INTEGER UNIQUE,
                phone_number TEXT,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                language TEXT DEFAULT 'en',
                is_subscribed INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Movies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_id TEXT UNIQUE,
                title TEXT,
                description TEXT,
                genre TEXT,
                year INTEGER,
                file_id TEXT,
                file_type TEXT,
                added_by INTEGER,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                views INTEGER DEFAULT 0
            )
        ''')
        
        # Watched movies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS watched_movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                movie_id TEXT,
                watched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (movie_id) REFERENCES movies (movie_id)
            )
        ''')
        
        # Watch later table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS watch_later (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                movie_id TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (movie_id) REFERENCES movies (movie_id)
            )
        ''')
        
        # User subscriptions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, telegram_id, phone_number=None, username=None, first_name=None, last_name=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (telegram_id, phone_number, username, first_name, last_name)
                VALUES (?, ?, ?, ?, ?)
            ''', (telegram_id, phone_number, username, first_name, last_name))
            conn.commit()
        except Exception as e:
            print(f"Error adding user: {e}")
        finally:
            conn.close()
    
    def get_user(self, telegram_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
        user = cursor.fetchone()
        conn.close()
        return user
    
    def update_language(self, telegram_id, language):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE users SET language = ? WHERE telegram_id = ?', (language, telegram_id))
        conn.commit()
        conn.close()
    
    def update_subscription_status(self, telegram_id, status):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE users SET is_subscribed = ? WHERE telegram_id = ?', (status, telegram_id))
        conn.commit()
        conn.close()
    
    def add_movie(self, movie_id, title, description, genre, year, file_id, file_type, added_by):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO movies (movie_id, title, description, genre, year, file_id, file_type, added_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (movie_id, title, description, genre, year, file_id, file_type, added_by))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding movie: {e}")
            return False
        finally:
            conn.close()
    
    def get_movie_by_id(self, movie_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM movies WHERE movie_id = ?', (movie_id,))
        movie = cursor.fetchone()
        conn.close()
        return movie
    
    def get_all_movies(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM movies ORDER BY added_at DESC')
        movies = cursor.fetchall()
        conn.close()
        return movies
    
    def search_movies(self, query):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM movies 
            WHERE title LIKE ? OR description LIKE ? OR genre LIKE ?
        ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
        movies = cursor.fetchall()
        conn.close()
        return movies
    
    def add_to_watched(self, user_id, movie_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if already watched
        cursor.execute('''
            SELECT id FROM watched_movies WHERE user_id = ? AND movie_id = ?
        ''', (user_id, movie_id))
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO watched_movies (user_id, movie_id)
                VALUES (?, ?)
            ''', (user_id, movie_id))
            conn.commit()
        
        # Update movie views
        cursor.execute('UPDATE movies SET views = views + 1 WHERE movie_id = ?', (movie_id,))
        conn.commit()
        conn.close()
    
    def add_to_watch_later(self, user_id, movie_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if already in watch later
        cursor.execute('''
            SELECT id FROM watch_later WHERE user_id = ? AND movie_id = ?
        ''', (user_id, movie_id))
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO watch_later (user_id, movie_id)
                VALUES (?, ?)
            ''', (user_id, movie_id))
            conn.commit()
        conn.close()
    
    def remove_from_watch_later(self, user_id, movie_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM watch_later WHERE user_id = ? AND movie_id = ?
        ''', (user_id, movie_id))
        conn.commit()
        conn.close()
    
    def get_watch_later(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT m.* FROM movies m
            JOIN watch_later wl ON m.movie_id = wl.movie_id
            WHERE wl.user_id = ?
            ORDER BY wl.added_at DESC
        ''', (user_id,))
        movies = cursor.fetchall()
        conn.close()
        return movies
    
    def get_watched_movies(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT m.* FROM movies m
            JOIN watched_movies wm ON m.movie_id = wm.movie_id
            WHERE wm.user_id = ?
            ORDER BY wm.watched_at DESC
        ''', (user_id,))
        movies = cursor.fetchall()
        conn.close()
        return movies
    
    def get_user_stats(self, telegram_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get user info
        cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
        user = cursor.fetchone()
        
        # Get movie counts
        cursor.execute('SELECT COUNT(*) FROM watched_movies WHERE user_id = ?', (user[0],))
        watched_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM watch_later WHERE user_id = ?', (user[0],))
        watch_later_count = cursor.fetchone()[0]
        
        conn.close()
        return {
            'user': user,
            'watched_count': watched_count,
            'watch_later_count': watch_later_count
        }
    
    def get_all_users(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        conn.close()
        return users
    
    def get_movies_count(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM movies')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def delete_movie(self, movie_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM movies WHERE movie_id = ?', (movie_id,))
        conn.commit()
        conn.close()
