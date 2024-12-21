from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import logging
import os
import secrets
import jwt
import requests
from functools import wraps
from configuration import Config
from typing import Optional
from sqlalchemy.sql import func

# Load configuration
config = Config(
    env_file='.env',
    config_file='config.yml'
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.database.url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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

# Models
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    picture = db.Column(db.String)
    stars = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=func.now())
    last_login = db.Column(db.DateTime)
    
    refresh_tokens = db.relationship('RefreshToken', backref='user', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'picture': self.picture,
            'stars': self.stars,
            'level': self.level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class RefreshToken(db.Model):
    __tablename__ = 'refresh_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String, unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    expires_at = db.Column(db.DateTime, nullable=False)
    revoked_at = db.Column(db.DateTime)
    issuer_ip = db.Column(db.String)

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

def store_refresh_token(user_id: int, token: str, ip_address: str):
    """Store a refresh token in the database."""
    # Revoke old refresh tokens for this user
    RefreshToken.query.filter_by(
        user_id=user_id,
        revoked_at=None
    ).update({'revoked_at': datetime.utcnow()})
    
    # Create new refresh token
    expiry = datetime.utcnow() + timedelta(days=config.security.refresh_token_expiry_days)
    new_token = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expiry,
        issuer_ip=ip_address
    )
    db.session.add(new_token)

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
        
        # Check if user exists
        user = User.query.filter_by(google_id=token_info['sub']).first()
        
        if user:
            # Update existing user
            user.last_login = datetime.now()
            logger.info(f'Successful login for existing user: {user.email} from {client_ip}')
        else:
            # Create new user
            user = User(
                google_id=token_info['sub'],
                email=token_info['email'],
                name=token_info['email'].split('@')[0],
                last_login=datetime.now()
            )
            db.session.add(user)
            logger.info(f'New user registered and logged in: {user.email} from {client_ip}')
        
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token()
        
        store_refresh_token(user.id, refresh_token, client_ip)
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': config.security.access_token_expiry_minutes * 60
        })
            
    except Exception as e:
        logger.error(f'Error during login: {str(e)}')
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'An error occurred'
        }), 500

@app.route('/api/refresh', methods=['POST'])
def refresh():
    data = request.json
    client_ip = request.remote_addr
    
    if not data or 'refresh_token' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Refresh token required'
        }), 400
    
    try:
        # Verify refresh token
        token = RefreshToken.query.filter_by(
            token=data['refresh_token'],
            revoked_at=None
        ).filter(
            RefreshToken.expires_at > datetime.utcnow()
        ).first()
        
        if not token:
            return jsonify({
                'status': 'error',
                'message': 'Invalid or expired refresh token'
            }), 401
        
        user = User.query.get(token.user_id)
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
        
        new_access_token = create_access_token(user.id)
        new_refresh_token = create_refresh_token()
        
        store_refresh_token(user.id, new_refresh_token, client_ip)
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'user': user.to_dict(),
            'access_token': new_access_token,
            'refresh_token': new_refresh_token,
            'expires_in': config.security.access_token_expiry_minutes * 60
        })
        
    except Exception as e:
        logger.error(f'Error during token refresh: {str(e)}')
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'An error occurred'
        }), 500

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
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
        
        user.name = data['new_username']
        db.session.commit()
        
        logger.info(f'Username updated for user {user.email} to {data["new_username"]} from {client_ip}')
        
        return jsonify({
            'status': 'success',
            'user': user.to_dict()
        })
        
    except Exception as e:
        logger.error(f'Error updating username: {str(e)}')
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Error updating username'
        }), 500

@app.route('/api/update_picture', methods=['POST'])
@require_auth
def update_picture(user_id):
    data = request.json
    client_ip = request.remote_addr
    
    if not data or 'new_picture' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Missing new picture'
        }), 400
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
        
        user.picture = data['new_picture']
        db.session.commit()
        
        logger.info(f'Picture updated for user {user.email} from {client_ip}')
        
        return jsonify({
            'status': 'success',
            'user': user.to_dict()
        })
        
    except Exception as e:
        logger.error(f'Error updating picture: {str(e)}')
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Error updating picture'
        }), 500

if __name__ == '__main__':
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Start server
    logger.info('Server started')
    app.run(
        host=config.server.host,
        port=config.server.port,
        debug=config.server.debug
    )