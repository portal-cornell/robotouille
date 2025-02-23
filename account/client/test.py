import os
import time
import sys
import argparse
from oauth import OAuthManager, LoginStatus, UserInfo
from datetime import datetime

def parse_arguments():
    parser = argparse.ArgumentParser(description='OAuth Client Test Script')
    parser.add_argument(
        '--client-id',
        required=True,
        help='Google OAuth client ID'
    )
    parser.add_argument(
        '--client-secret',
        required=True,
        help='Google OAuth client secret'
    )
    parser.add_argument(
        '--backend-url',
        default='http://localhost:8000',
        help='Backend server URL (default: http://localhost:8000)'
    )
    return parser.parse_args()

def print_status(message, success=True):
    """Print a status message with color and timestamp."""
    color = '\033[92m' if success else '\033[91m'  # Green or Red
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {color}{message}\033[0m")

# Track callback invocations
callback_history = {
    'login': 0,
    'logout': 0
}

def on_login_success(user: UserInfo):
    """Callback for successful login."""
    callback_history['login'] += 1
    print_status(f"\n[Callback #{callback_history['login']}] Login successful!")
    print_status("Callback received user info:")
    print(f"  User ID: {user.id}")
    print(f"  Name: {user.name}")
    print(f"  Email: {user.email}")
    print(f"  Level: {user.level}")
    print(f"  Stars: {user.stars}")

def on_logout():
    """Callback for logout."""
    callback_history['logout'] += 1
    print_status(f"\n[Callback #{callback_history['logout']}] Logged out successfully!")

def print_callback_status():
    """Print current callback statistics."""
    print_status("\nCallback Statistics:")
    print(f"  Login callbacks triggered: {callback_history['login']}")
    print(f"  Logout callbacks triggered: {callback_history['logout']}")

def main():
    args = parse_arguments()
    
    oauth = OAuthManager(
        client_id=args.client_id,
        client_secret=args.client_secret,
        backend_url=args.backend_url
    )
    
    print_status("OAuth manager initialized")
    print_status(f"Using backend URL: {args.backend_url}")
    
    if oauth.load_stored_credentials():
        print_status("Found stored credentials")
        user = oauth.get_user()
        status, error = oauth.get_login_status()
        print_status(f"Login status: {status.name}")
        print_status(f"Logged in as: {user.name} ({user.email})")
        print_status(f"Progress: Level {user.level} with {user.stars} stars")
        if error:
            print_status(f"Warning: {error}", success=False)
    else:
        print_status("No stored credentials found", success=False)
        status, error = oauth.get_login_status()
        print_status(f"Login status: {status.name}")
        if error:
            print_status(f"Error: {error}", success=False)
    
    while True:
        print("\nAvailable commands:")
        print("1. Login")
        print("2. Check login status")
        print("3. Get user info")
        print("4. Update username")
        print("5. Logout")
        print("6. Check callback history")
        print("7. Force token refresh")
        print("8. Exit")
        
        choice = input("\nEnter command number: ").strip()
        
        if choice == '1':
            print_status("\nStarting login process...")
            oauth.login(on_success=on_login_success, on_logout=on_logout)
            
            # Wait for login to complete or fail
            while True:
                oauth.process_callbacks()  # Process any pending callbacks
                status, error = oauth.get_login_status()
                if status == LoginStatus.IN_PROGRESS:
                    print("Waiting for login to complete...", end='\r')
                    time.sleep(0.5)
                elif status == LoginStatus.FAILED:
                    print_status(f"\nLogin failed: {error}", success=False)
                    break
                elif status == LoginStatus.SUCCESS:
                    # Callback will handle success message
                    break
        
        elif choice == '2':
            status, error = oauth.get_login_status()
            print_status(f"\nCurrent login status: {status.name}")
            if error:
                print_status(f"Error: {error}", success=False)
        
        elif choice == '3':
            user = oauth.get_user()
            if user:
                print_status("\nCurrent user info:")
                print(f"User ID: {user.id}")
                print(f"Name: {user.name}")
                print(f"Email: {user.email}")
                print(f"Level: {user.level}")
                print(f"Stars: {user.stars}")
            else:
                print_status("No user logged in", success=False)
        
        elif choice == '4':
            if not oauth.is_logged_in():
                print_status("Must be logged in to update username", success=False)
                continue
                
            new_username = input("Enter new username: ").strip()
            if new_username:
                if oauth.update_username(new_username):
                    print_status("Username updated successfully!")
                else:
                    print_status("Failed to update username", success=False)
        
        elif choice == '5':
            if oauth.is_logged_in():
                print_status("Initiating logout...")
                oauth.logout()
                # Process any pending callbacks
                oauth.process_callbacks()
            else:
                print_status("Not logged in", success=False)
        
        elif choice == '6':
            print_callback_status()
        
        elif choice == '7':
            if oauth.is_logged_in():
                print_status("Forcing token refresh...")
                if oauth.refresh_tokens():
                    print_status("Token refresh successful!")
                else:
                    print_status("Token refresh failed", success=False)
            else:
                print_status("Must be logged in to refresh tokens", success=False)
        
        elif choice == '8':
            print_status("\nExiting...")
            sys.exit(0)
        
        else:
            print_status("Invalid command", success=False)
        
        # Process any pending callbacks after each command
        oauth.process_callbacks()

if __name__ == "__main__":
    print_status("\nOAuth Client Test Script")
    
    try:
        main()
    except KeyboardInterrupt:
        print_status("\nExiting...")
    except argparse.ArgumentError as e:
        print_status(f"\nArgument Error: {e}", success=False)
        print("Usage example:")
        print("python test.py --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET")
        sys.exit(1)
    except Exception as e:
        print_status(f"\nError: {e}", success=False)
        sys.exit(1)