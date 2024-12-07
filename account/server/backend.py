from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import logging
import os
import secrets
import jwt
import requests
from functools import wraps
from configuration import Config
from typing import Optional

# Load configuration
config = Config(
    env_file='.env',
    config_file='config.yml'
)

app = Flask(__name__)

# Set up logging
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    level=config.server.log_level,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/login.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_db_connection():
    return psycopg2.connect(
        config.database.url,
        cursor_factory=RealDictCursor
    )

def create_access_token(user_id: int) -> str:
    """Create a JWT access token."""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(minutes=config.security.access_token_expiry_minutes),
        'type': 'access'
    }
    return jwt.encode(payload, config.security.jwt_secret, algorithm=config.security.jwt_algorithm)

def create_refresh_token() -> str:
    """Create a secure refresh token."""
    return secrets.token_urlsafe(64)

def store_refresh_token(conn, user_id: int, token: str, ip_address: str):
    """Store a refresh token in the database."""
    cur = conn.cursor()
    try:
        # Revoke old refresh tokens for this user
        cur.execute(
            """
            UPDATE refresh_tokens 
            SET revoked_at = CURRENT_TIMESTAMP 
            WHERE user_id = %s AND revoked_at IS NULL
            """,
            (user_id,)
        )
        
        # Store new refresh token
        expiry = datetime.utcnow() + timedelta(days=config.security.refresh_token_expiry_days)
        cur.execute(
            """
            INSERT INTO refresh_tokens (user_id, token, expires_at, issuer_ip)
            VALUES (%s, %s, %s, %s)
            """,
            (user_id, token, expiry, ip_address)
        )
    finally:
        cur.close()

def verify_jwt(token: str) -> Optional[int]:
    """Verify a JWT token and return the user_id."""
    try:
        payload = jwt.decode(
            token,
            config.security.jwt_secret,
            algorithms=[config.security.jwt_algorithm]
        )
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_auth(f):
    """Decorator to require JWT authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'status': 'error', 'message': 'No token provided'}), 401
        
        token = auth_header.split(' ')[1]
        user_id = verify_jwt(token)
        
        if not user_id:
            return jsonify({'status': 'error', 'message': 'Invalid token'}), 401
        
        return f(user_id, *args, **kwargs)
    return decorated

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    client_ip = request.remote_addr
    
    if not data or 'access_token' not in data:
        logger.warning(f'Login attempt without access token from {client_ip}')
        return jsonify({
            'status': 'error',
            'message': 'Access token required'
        }), 400
    
    try:
        # Verify the access token with Google
        response = requests.get(
            config.oauth.google_token_info_url,
            params={'access_token': data['access_token']}
        )
        
        if response.status_code != 200:
            logger.warning(f'Invalid access token from {client_ip}')
            return jsonify({
                'status': 'error',
                'message': 'Invalid access token'
            }), 401
        
        token_info = response.json()
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            # Check if user exists
            cur.execute(
                'SELECT * FROM users WHERE google_id = %s',
                (token_info['sub'],)
            )
            user = cur.fetchone()
            
            if user:
                # Update existing user
                cur.execute(
                    '''
                    UPDATE users 
                    SET last_login = %s 
                    WHERE google_id = %s
                    RETURNING *
                    ''',
                    (datetime.now(), token_info['sub'])
                )
                user = cur.fetchone()
                logger.info(f'Successful login for existing user: {user["email"]} from {client_ip}')
            else:
                # Create new user
                cur.execute(
                    '''
                    INSERT INTO users (google_id, email, name, picture, last_login)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING *
                    ''',
                    (token_info['sub'], token_info['email'], 
                     token_info['email'].split('@')[0],
                     token_info.get('picture', ''), datetime.now())
                )
                user = cur.fetchone()
                logger.info(f'New user registered and logged in: {user["email"]} from {client_ip}')
            
            access_token = create_access_token(user['id'])
            refresh_token = create_refresh_token()
            
            store_refresh_token(conn, user['id'], refresh_token, client_ip)
            
            conn.commit()
            
            return jsonify({
                'status': 'success',
                'user': dict(user),
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expires_in': config.security.access_token_expiry_minutes * 60
            })
            
        finally:
            cur.close()
            
    except Exception as e:
        logger.error(f'Error during login: {str(e)}')
        if conn:
            conn.rollback()
        return jsonify({
            'status': 'error',
            'message': 'An error occurred'
        }), 500
        
    finally:
        if conn:
            conn.close()

@app.route('/api/refresh', methods=['POST'])
def refresh():
    data = request.json
    client_ip = request.remote_addr
    
    if not data or 'refresh_token' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Refresh token required'
        }), 400
    
    conn = None
    cur = None
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Verify refresh token
        cur.execute(
            """
            SELECT user_id 
            FROM refresh_tokens 
            WHERE token = %s 
            AND expires_at > CURRENT_TIMESTAMP
            AND revoked_at IS NULL
            """,
            (data['refresh_token'],)
        )
        
        result = cur.fetchone()
        if not result:
            return jsonify({
                'status': 'error',
                'message': 'Invalid or expired refresh token'
            }), 401
        
        user_id = result['user_id']
        
        new_access_token = create_access_token(user_id)
        new_refresh_token = create_refresh_token()
        
        store_refresh_token(conn, user_id, new_refresh_token, client_ip)
        
        # Get user data
        cur.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        user = cur.fetchone()
        
        conn.commit()
        
        return jsonify({
            'status': 'success',
            'user': dict(user),
            'access_token': new_access_token,
            'refresh_token': new_refresh_token,
            'expires_in': config.security.access_token_expiry_minutes * 60
        })
        
    except Exception as e:
        logger.error(f'Error during token refresh: {str(e)}')
        if conn:
            conn.rollback()
        return jsonify({
            'status': 'error',
            'message': 'An error occurred'
        }), 500
        
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.route('/api/update_username', methods=['POST'])
@require_auth
def update_username(user_id):
    data = request.json
    client_ip = request.remote_addr
    
    if not data or 'new_username' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Missing new username'
        }), 400
        
    if not data['new_username'].strip():
        return jsonify({
            'status': 'error',
            'message': 'Username cannot be empty'
        }), 400
    
    conn = None
    cur = None
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(
            '''
            UPDATE users 
            SET name = %s 
            WHERE id = %s
            RETURNING *
            ''',
            (data['new_username'], user_id)
        )
        
        user = cur.fetchone()
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
            
        conn.commit()
        logger.info(f'Username updated for user {user["email"]} to {data["new_username"]} from {client_ip}')
        
        return jsonify({
            'status': 'success',
            'user': dict(user)
        })
        
    except Exception as e:
        logger.error(f'Error updating username: {str(e)}')
        if conn:
            conn.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Error updating username'
        }), 500
        
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Initialize database
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Create tables if they don't exist
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            google_id TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            picture TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS refresh_tokens (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            token TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            revoked_at TIMESTAMP,
            issuer_ip TEXT
        );
    ''')
    
    conn.commit()
    cur.close()
    conn.close()
    
    # Start server
    logger.info('Server started')
    app.run(
        host=config.server.host,
        port=config.server.port,
        debug=config.server.debug
    )