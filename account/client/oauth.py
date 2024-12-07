import os
import json
import webbrowser
import requests
import threading
from flask import Flask, request
from requests_oauthlib import OAuth2Session
from pathlib import Path
from appdirs import user_data_dir
from queue import Queue
from dataclasses import dataclass
from typing import Optional, Dict, Callable
from enum import Enum, auto

class LoginStatus(Enum):
    """Enum representing the current status of the login process."""
    NOT_STARTED = auto()
    IN_PROGRESS = auto()
    SUCCESS = auto()
    FAILED = auto()

@dataclass
class UserInfo:
    """Data class to store user information."""
    id: int
    name: str
    email: str
    picture: Optional[str] = None

@dataclass
class PendingCallback:
    """Data class to store a callback and its arguments."""
    func: Callable
    args: tuple
    kwargs: dict

class OAuthManager:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        backend_url: str,
        app_name: str = "PoRTaL",
        app_author: str = "Robotouille",
        port: int = 5000
    ):
        """
        Initialize the OAuth manager.
        
        Args:
            client_id: Google OAuth client ID
            client_secret: Google OAuth client secret
            backend_url: URL of the authentication backend server
            app_name: Name of the application (for storing credentials)
            app_author: Author of the application (for storing credentials)
            port: Port to run the temporary OAuth server on
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.backend_url = backend_url
        self.redirect_uri = f'http://localhost:{port}/auth/google/callback'
        self.port = port
        
        # OAuth endpoints
        self.auth_base_url = 'https://accounts.google.com/o/oauth2/auth'
        self.token_url = 'https://oauth2.googleapis.com/token'
        self.scope = [
            'https://www.googleapis.com/auth/userinfo.profile',
            'https://www.googleapis.com/auth/userinfo.email',
            'openid'
        ]
        
        # Setup storage
        self.app_dir = user_data_dir(app_name, app_author)
        self.user_file = os.path.join(self.app_dir, "user_data.json")
        Path(self.app_dir).mkdir(parents=True, exist_ok=True)
        
        # State
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.user: Optional[UserInfo] = None
        self._auth_success = threading.Event()
        self._auth_error: Optional[str] = None
        self._login_callback: Optional[Callable[[UserInfo], None]] = None
        self._logout_callback: Optional[Callable[[], None]] = None
        self._server_thread: Optional[threading.Thread] = None
        
        # Flask app for handling OAuth callback
        self.app = Flask(__name__)
        self._setup_routes()

        # Login status
        self.login_status = LoginStatus.NOT_STARTED
        self.login_error: Optional[str] = None

        # Queue for callbacks that should run on main thread
        self._callback_queue: Queue[PendingCallback] = Queue()

    def _queue_callback(self, callback: Callable, *args, **kwargs):
        """Queue a callback to be executed on the main thread."""
        if callback:
            self._callback_queue.put(PendingCallback(callback, args, kwargs))

    def process_callbacks(self):
        """
        Process any pending callbacks. Should be called regularly from the main thread. This ensures thread safety.
        """
        while not self._callback_queue.empty():
            try:
                pending = self._callback_queue.get_nowait()
                pending.func(*pending.args, **pending.kwargs)
            except Exception as e:
                print(f"Error in callback: {e}")
        
    def _setup_routes(self):
        """Setup Flask routes for OAuth callback."""
        @self.app.route('/auth/google/callback')
        def callback():
            try:
                oauth = OAuth2Session(
                    self.client_id,
                    state=self.app.oauth_state,
                    redirect_uri=self.redirect_uri
                )
                token = oauth.fetch_token(
                    self.token_url,
                    client_secret=self.client_secret,
                    authorization_response=request.url
                )
                
                # Exchange token with backend
                response = requests.post(
                    f"{self.backend_url}/api/login",
                    json={'access_token': token['access_token']}
                )
                response.raise_for_status()
                result = response.json()
                
                # Store tokens and user info
                self.access_token = result['access_token']
                self.refresh_token = result['refresh_token']
                self._update_user(result['user'])
                self._save_user_data()
                
                # Trigger callback if set
                if self._login_callback and self.user:
                    self._queue_callback(self._login_callback, self.user)
                
                self._auth_success.set()
                return "Login successful! You may close this window."
                
            except Exception as e:
                self._auth_error = str(e)
                self._auth_success.set()
                return "Login failed. You may close this window."
                
        @self.app.route('/shutdown')
        def shutdown():
            """Route to shutdown the Flask server."""
            shutdown_func = request.environ.get('werkzeug.server.shutdown')
            if shutdown_func:
                shutdown_func()
                return 'Server shutting down...'
            else:
                return 'Server cannot be shutdown.'
    
    def _save_user_data(self):
        """Save user data and tokens to file."""
        if not all([self.user, self.access_token, self.refresh_token]):
            return
            
        data = {
            'user': {
                'id': self.user.id,
                'name': self.user.name,
                'email': self.user.email,
                'picture': self.user.picture
            },
            'access_token': self.access_token,
            'refresh_token': self.refresh_token
        }
        
        with open(self.user_file, 'w') as f:
            json.dump(data, f)
    
    def _update_user(self, user_data: Dict):
        """Update user info from dictionary."""
        self.user = UserInfo(
            id=user_data['id'],
            name=user_data['name'],
            email=user_data['email'],
            picture=user_data.get('picture')
        )
    
    def _shutdown_server(self):
        """Shutdown the local Flask server."""
        if self._server_thread and self._server_thread.is_alive():
            try:
                requests.get(f'http://localhost:{self.port}/shutdown')
            except:
                pass  # Server might already be down
        self._server_thread = None
    
    def load_stored_credentials(self) -> bool:
        """
        Load stored user credentials if available.
        
        Returns:
            bool: True if credentials were loaded successfully
        """
        try:
            if os.path.exists(self.user_file):
                with open(self.user_file, 'r') as f:
                    data = json.load(f)
                    self._update_user(data['user'])
                    self.access_token = data['access_token']
                    self.refresh_token = data['refresh_token']
                    return self.refresh_tokens()
        except Exception:
            pass
        return False
    
    def refresh_tokens(self) -> bool:
        """
        Refresh access and refresh tokens.
        
        Returns:
            bool: True if refresh was successful
        """
        if not self.refresh_token:
            return False
            
        try:
            response = requests.post(
                f"{self.backend_url}/api/refresh",
                json={'refresh_token': self.refresh_token}
            )
            
            if response.status_code == 200:
                result = response.json()
                self.access_token = result['access_token']
                self.refresh_token = result['refresh_token']
                self._update_user(result['user'])
                self._save_user_data()
                return True
            else:
                self.logout()
                return False
                
        except Exception:
            return False
    
    def login(
        self,
        on_success: Optional[Callable[[UserInfo], None]] = None,
        on_logout: Optional[Callable[[], None]] = None
    ):
        """
        Start OAuth login process (non-blocking).
        
        Args:
            on_success: Callback function when login succeeds
            on_logout: Callback function when user logs out
        """
        if self.login_status == LoginStatus.IN_PROGRESS:
            return
            
        # Clean up any existing server
        self._shutdown_server()
        
        self._login_callback = on_success
        self._logout_callback = on_logout
        self._auth_success.clear()
        self._auth_error = None
        self.login_status = LoginStatus.IN_PROGRESS
        self.login_error = None
        
        # Start login process in separate thread
        threading.Thread(
            target=self._login_process,
            daemon=True
        ).start()
    
    def _login_process(self):
        """Internal method to handle the login process."""
        try:
            # Start local server
            self._server_thread = threading.Thread(
                target=lambda: self.app.run(port=self.port),
                daemon=True
            )
            self._server_thread.start()
            
            oauth = OAuth2Session(
                self.client_id,
                redirect_uri=self.redirect_uri,
                scope=self.scope
            )
            authorization_url, state = oauth.authorization_url(
                self.auth_base_url,
                access_type="offline",
                prompt="select_account"
            )
            self.app.oauth_state = state
            
            webbrowser.open_new(authorization_url)
            
            self._auth_success.wait()
            
            # Clean up server
            self._shutdown_server()
            
            if self._auth_error:
                self.login_status = LoginStatus.FAILED
                self.login_error = self._auth_error
            else:
                self.login_status = LoginStatus.SUCCESS
                
        except Exception as e:
            self.login_status = LoginStatus.FAILED
            self.login_error = str(e)
            self._shutdown_server()
    
    def get_login_status(self) -> tuple[LoginStatus, Optional[str]]:
        """
        Get current login status and error message if any.
        
        Returns:
            Tuple of (LoginStatus, Optional[error_message])
        """
        return self.login_status, self.login_error
    
    def logout(self):
        """Log out the current user."""
        try:
            os.remove(self.user_file)
        except:
            pass
        
        self.user = None
        self.access_token = None
        self.refresh_token = None
        
        if self._logout_callback:
            self._queue_callback(self._logout_callback)
    
    def update_username(self, new_username: str) -> bool:
        """
        Update the user's username.
        
        Args:
            new_username: New username to set
            
        Returns:
            bool: True if update was successful
        """
        if not self.access_token or not self.user:
            return False
            
        try:
            response = requests.post(
                f"{self.backend_url}/api/update_username",
                headers={'Authorization': f'Bearer {self.access_token}'},
                json={'new_username': new_username}
            )
            
            if response.status_code == 200:
                result = response.json()
                self._update_user(result['user'])
                self._save_user_data()
                return True
            elif response.status_code == 401:
                # Currently lacking valid credentials
                if self.refresh_tokens():
                    return self.update_username(new_username)
                else:
                    self.logout()
            return False
            
        except Exception:
            return False
    
    def get_user(self) -> Optional[UserInfo]:
        """
        Get current user information.
        
        Returns:
            UserInfo if logged in, None otherwise
        """
        return self.user
    
    def is_logged_in(self) -> bool:
        """
        Check if user is currently logged in.
        
        Returns:
            bool: True if user is logged in
        """
        return bool(self.user and self.access_token)
    
    def __del__(self):
        """Ensure server is shutdown when object is destroyed."""
        self._shutdown_server()