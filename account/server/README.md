# Robotouille Account Server

This is the Robotouille account management backend server based on OAuth. This server manages user authentication, session tokens, and user profile data.

## Configuration

The server uses a combination of environment variables and YAML configuration. 

1. Create a `.env` file in the root directory with your sensitive credentials:
   ```env
   # Database credentials
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_NAME=your_db_name

   # Google OAuth credentials
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret

   # Security
   JWT_SECRET=your-secure-jwt-secret
   ```

2. Optionally customize `config.yml` (default values shown):
   ```yaml
   database:
     host: localhost
     port: 5432
     database: oauth_db

   security:
     jwt_algorithm: HS256
     access_token_expiry_minutes: 60
     refresh_token_expiry_days: 30

   server:
     host: 0.0.0.0
     port: 8000
     debug: false
     log_level: INFO
   ```

## Database Setup

This server uses PostgreSQL as its database. After installing and starting Postgres on your machine, follow these steps to set up the database for Robotouille.

1. Create the `.env` file in your project directory with your database credentials:
```env
DB_USER=oauth_user
DB_PASSWORD=your_secure_password

# Other required credentials
JWT_SECRET=your-very-secure-random-secret
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

2. Run the setup script:
```bash
python setup_db.py
```

## Getting Google OAuth Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google OAuth2 API
4. Go to Credentials
5. Create OAuth 2.0 Client ID
   - Application type: Web application
   - Authorized redirect URIs: Add `http://localhost:5000/auth/google/callback`
6. Copy the Client ID and Client Secret to your `.env` file

## Running the Server

1. Start the server:
   ```bash
   python backend.py
   ```

2. The server will:
   - Start listening on configured host:port (default: localhost:8000)
   - Create a logs directory and begin logging

## API Endpoints

### POST /api/login
Authenticates a user with a Google OAuth token.
```json
{
    "access_token": "google-oauth-access-token"
}
```

### POST /api/refresh
Refreshes an expired access token using a refresh token.
```json
{
    "refresh_token": "your-refresh-token"
}
```

### POST /api/update_username
Updates a user's username (requires authentication).
```json
{
    "new_username": "desired-username"
}
```

## Client Integration

The server is designed to work with the provided Python OAuth client. The client uses a callback-based system for handling authentication events.

### Basic Usage
```python
from oauth_client import OAuthManager, UserInfo

oauth = OAuthManager(
    client_id="your-google-client-id",
    client_secret="your-google-client-secret",
    backend_url="http://localhost:8000"
)

# Define callback handlers
def on_login_success(user: UserInfo):
    print(f"Logged in as {user.name}")
    print(f"Email: {user.email}")

def on_logout():
    print("User logged out")

# Start login process with callbacks
oauth.login(on_success=on_login_success, on_logout=on_logout)
```

### Callback System

The OAuth client uses an event-based callback system that runs callbacks on the main thread to ensure thread safety.

#### Available Callbacks

1. **Login Success Callback**
   - Triggered when login completes successfully
   - Receives a `UserInfo` object with user details
   ```python
   def on_login_success(user: UserInfo):
       """
       Args:
           user: UserInfo object containing:
               - id: int
               - name: str
               - email: str
               - picture: Optional[str]
       """
       print(f"Logged in as {user.name}")
   ```

2. **Logout Callback**
   - Triggered when user logs out or tokens become invalid
   - Receives no arguments
   ```python
   def on_logout():
       """Called when user logs out or session expires"""
       print("Session ended")
   ```

#### Processing Callbacks

If you're using the client in a GUI application or any environment with an event loop, you need to regularly process callbacks:

```python
# In your main event loop
while True:
    # Process any pending callbacks
    oauth.process_callbacks()
    
    # Your other application logic
    ...
```

### Token Management

The client automatically handles token refresh and persistence. If a token expires:

1. The client will attempt to refresh it automatically
2. If refresh fails, the `on_logout` callback will be triggered
3. If refresh succeeds, the session continues without interruption

Call `refresh_tokens` to update the client to the latest user information.

## Security Notes

- Store your `.env` file securely and never commit it to version control
- Generate a strong JWT secret (you can use `secrets.token_hex(32)` in Python)
- Keep your Google OAuth credentials secure

## Logging

Logs are stored in the `logs` directory:
- `logs/login.log`: Authentication and user management events