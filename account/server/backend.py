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
from models import User, RefreshToken, BlogPost, Comment
from extensions import db

# Load configuration
config = Config(
    env_file='.env',
    config_file='config.yml'
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.database.url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

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

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/auth/google/callback')
def google_callback():
    # Extract the authorization code from the request args
    code = request.args.get('code')
    if not code:
        return "Missing code", 400

    # Exchange the code for an access token
    token_response = requests.post(
        'https://oauth2.googleapis.com/token',
        data={
            'code': code,
            'client_id': YOUR_CLIENT_ID,
            'client_secret': YOUR_CLIENT_SECRET,
            'redirect_uri': 'http://localhost:8000/auth/google/callback',
            'grant_type': 'authorization_code'
        }
    ).json()

    # token_response will contain the access_token, expires_in, etc.
    return jsonify(token_response)

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


### BLOG POSTS ###

@app.route('/api/blogposts', methods=['POST'])
@require_auth
def create_blog_post(user_id):
    data = request.json
    client_ip = request.remote_addr
    
    if not data or 'title' not in data or 'content' not in data:
        return jsonify({
            'status': 'error', ''
            'message': 'Missing required fields'
        }), 400
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'status': 'error', 
                'message': 'User not found'
            }), 404
        
        post = BlogPost(
            author_id=user_id,
            title=data['title'],
            content=data['content']
        )
        db.session.add(post)
        db.session.commit()
        
        logger.info(f'New blog post created by {user.email} from {client_ip}')
        
        return jsonify({
            'status': 'success', 
            'post': post.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f'Error creating blog post: {str(e)}')
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Error creating blog post'
        }), 500
    

@app.route('/api/blogposts/<int:post_id>', methods=['DELETE'])
@require_auth
def delete_blog_post(user_id, post_id):
    try:
        post = BlogPost.query.get(post_id)
        if not post:
            return jsonify({'status': 'error', 'message': 'Blog post not found'}), 404
        
        if post.author_id != user_id:
            return jsonify({'status': 'error', 'message': 'Forbidden'}), 403
        
        db.session.delete(post)
        db.session.commit()
        logger.info(f'User (ID: {user_id}) deleted blog post (ID: {post_id})')
        
        return jsonify({'status': 'success', 'message': 'Blog post deleted'})
    except Exception as e:
        logger.error(f'Error deleting blog post: {str(e)}')
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Error deleting blog post'}), 500


@app.route('/api/comments', methods=['POST'])
@require_auth
def create_comment(user_id):
    data = request.json
    if not data or 'blog_post_id' not in data or 'content' not in data:
        return jsonify({'status': 'error', 'message': 'Missing blog_post_id or content'}), 400
    
    blog_post_id = data['blog_post_id']
    content = data['content'].strip()
    if not content:
        return jsonify({'status': 'error', 'message': 'Content cannot be empty'}), 400
    
    try:
        blog_post = BlogPost.query.get(blog_post_id)
        if not blog_post:
            return jsonify({'status': 'error', 'message': 'Blog post not found'}), 404
        
        new_comment = Comment(author_id=user_id, blog_post_id=blog_post_id, content=content)
        db.session.add(new_comment)
        db.session.commit()
        
        logger.info(f'User (ID: {user_id}) created comment (ID: {new_comment.id}) on post (ID: {blog_post_id})')
        
        return jsonify({
            'status': 'success',
            'comment': {
                'id': new_comment.id,
                'blog_post_id': new_comment.blog_post_id,
                'content': new_comment.content,
                'created_at': new_comment.created_at.isoformat()
            }
        }), 201
    except Exception as e:
        logger.error(f'Error creating comment: {str(e)}')
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Error creating comment'}), 500


@app.route('/api/comments/<int:comment_id>', methods=['DELETE'])
@require_auth
def delete_comment(user_id, comment_id):
    try:
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify({'status': 'error', 'message': 'Comment not found'}), 404
        
        if comment.author_id != user_id:
            return jsonify({'status': 'error', 'message': 'Forbidden'}), 403
        
        db.session.delete(comment)
        db.session.commit()
        
        logger.info(f'User (ID: {user_id}) deleted comment (ID: {comment_id})')
        return jsonify({'status': 'success', 'message': 'Comment deleted'})
    except Exception as e:
        logger.error(f'Error deleting comment: {str(e)}')
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Error deleting comment'}), 500


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