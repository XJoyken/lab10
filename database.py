import psycopg2
import json

db_params = {
    'dbname': 'snake_game',
    'user': 'postgres',
    'password': 'reshetka3435684',
    'host': 'localhost',
    'port': '5432'
}

def connect_db():
    try:
        conn = psycopg2.connect(**db_params)
        return conn
    except Exception as e:
        print(f"Connection error: {e}")
        return None

def create_tables():
    conn = connect_db()
    if conn is None:
        return
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_score (
                score_id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(user_id),
                level INTEGER NOT NULL,
                score INTEGER NOT NULL,
                snake_length INTEGER NOT NULL,
                snake_state JSONB,
                fruit_state JSONB,
                direction VARCHAR(10),
                saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        print("Tables created or already exist.")
    except Exception as e:
        print(f"Table creation error: {e}")
    finally:
        cur.close()
        conn.close()

def get_or_create_user(username):
    conn = connect_db()
    if conn is None:
        return None, None
    try:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        if user:
            user_id = user[0]
            cur.execute("SELECT level, score, snake_length FROM user_score WHERE user_id = %s ORDER BY saved_at DESC LIMIT 1", (user_id,))
            score_data = cur.fetchone()
            if score_data:
                print(f"Welcome back, {username}! Current level: {score_data[0]}, score: {score_data[1]}, snake length: {score_data[2]}")
                return user_id, score_data
            print(f"Welcome back, {username}! Starting at level 1.")
            return user_id, None
        cur.execute("INSERT INTO users (username) VALUES (%s) RETURNING user_id", (username,))
        user_id = cur.fetchone()[0]
        conn.commit()
        print(f"New user created: {username}. Starting at level 1.")
        return user_id, None
    except Exception as e:
        print(f"User error: {e}")
        conn.rollback()
        return None, None
    finally:
        cur.close()
        conn.close()

def save_game_state(user_id, level, score, snake, fruit, direction):
    conn = connect_db()
    if conn is None:
        return
    try:
        cur = conn.cursor()
        snake_json = json.dumps(snake)
        fruit_json = json.dumps(fruit)
        snake_length = len(snake)
        cur.execute("""
            INSERT INTO user_score (user_id, level, score, snake_length, snake_state, fruit_state, direction)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, level, score, snake_length, snake_json, fruit_json, direction))
        conn.commit()
        print("Game state saved.")
    except Exception as e:
        print(f"Save error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()