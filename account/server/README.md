# Robotouille Account Server

This is the Robotouille account management backend server based on OAuth. This server manages user authentication, session tokens, and user profile data.

## Configuration

The server uses a combination of environment variables and YAML configuration. 

1. Create a `.env` file in the root directory with your sensitive credentials:
   ```env
   # Database credentials
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password

   # Security
   JWT_SECRET=your-very-secure-random-secret

   # Google OAuth credentials
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
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
   - Create necessary database tables if they don't exist
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

The server is designed to work with the provided Python OAuth client. See the client documentation for integration details.

Example client usage:
```python
from oauth_client import OAuthManager

oauth = OAuthManager(
    client_id="your-google-client-id",
    client_secret="your-google-client-secret",
    backend_url="http://localhost:8000"
)

def on_login(user):
    print(f"Logged in as {user.name}")

oauth.login(on_success=on_login)
```

## Security Notes

- Store your `.env` file securely and never commit it to version control
- Generate a strong JWT secret (you can use `secrets.token_hex(32)` in Python)
- Keep your Google OAuth credentials secure

## Logging

Logs are stored in the `logs` directory:
- `logs/login.log`: Authentication and user management events