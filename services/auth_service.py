import os
import firebase_admin
from firebase_admin import credentials, auth
from typing import Optional
import json

class AuthService:
    def __init__(self):
        """Initialize Firebase Admin SDK for authentication"""
        self.use_firebase = False
        
        try:
            # Check if Firebase app is already initialized
            firebase_admin.get_app()
            self.use_firebase = True
        except ValueError:
            # Check if Firebase credentials are available
            if self._has_firebase_config():
                try:
                    # Initialize Firebase with service account
                    cred_dict = {
                        "type": "service_account",
                        "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                        "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                        "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
                        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                        "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                        "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
                        "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
                        "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
                        "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL")
                    }
                    
                    cred = credentials.Certificate(cred_dict)
                    firebase_admin.initialize_app(cred)
                    self.use_firebase = True
                    print("Firebase authentication initialized successfully")
                except Exception as e:
                    print(f"Firebase initialization failed: {e}")
                    print("Falling back to simple authentication")
            else:
                print("Firebase configuration not found. Using simple authentication.")
    
    def _has_firebase_config(self) -> bool:
        """Check if Firebase configuration is available"""
        required_configs = [
            "FIREBASE_PROJECT_ID",
            "FIREBASE_PRIVATE_KEY_ID", 
            "FIREBASE_PRIVATE_KEY",
            "FIREBASE_CLIENT_EMAIL",
            "FIREBASE_CLIENT_ID"
        ]
        
        return all(os.getenv(config) for config in required_configs)
    
    def signup(self, email: str, password: str) -> bool:
        """
        Create a new user account
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            True if successful, False otherwise
        """
        if self.use_firebase:
            try:
                # Create user in Firebase
                user_record = auth.create_user(
                    email=email,
                    password=password,
                    email_verified=False
                )
                
                print(f"Successfully created user: {user_record.uid}")
                return True
                
            except Exception as e:
                print(f"Error creating user: {e}")
                return False
        else:
            # Use simple authentication
            return self._simple_auth.signup(email, password)
    
    def login(self, email: str, password: str) -> bool:
        """
        Authenticate a user
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            True if successful, False otherwise
        """
        if self.use_firebase:
            try:
                # For demo purposes, we'll use a simplified approach
                # In production, you'd use Firebase Auth REST API
                users = auth.list_users()
                
                for user in users.users:
                    if user.email == email:
                        # In a real app, you'd verify the password via Firebase Auth
                        # For demo, we'll just check if the user exists
                        return True
                
                return False
                
            except Exception as e:
                print(f"Error during login: {e}")
                return False
        else:
            # Use simple authentication
            return self._simple_auth.login(email, password)
    
    def get_user_by_email(self, email: str) -> Optional[dict]:
        """
        Get user information by email
        
        Args:
            email: User's email address
            
        Returns:
            User record or None if not found
        """
        if self.use_firebase:
            try:
                users = auth.list_users()
                
                for user in users.users:
                    if user.email == email:
                        return {
                            "uid": user.uid,
                            "email": user.email,
                            "email_verified": user.email_verified,
                            "disabled": user.disabled
                        }
                
                return None
                
            except Exception as e:
                print(f"Error getting user: {e}")
                return None
        else:
            # Use simple authentication
            return self._simple_auth.get_user_by_email(email)
    
    def delete_user(self, uid: str) -> bool:
        """
        Delete a user account
        
        Args:
            uid: User's unique ID
            
        Returns:
            True if successful, False otherwise
        """
        if self.use_firebase:
            try:
                auth.delete_user(uid)
                print(f"Successfully deleted user: {uid}")
                return True
                
            except Exception as e:
                print(f"Error deleting user: {e}")
                return False
        else:
            # Simple auth doesn't support user deletion
            return False
    
    def update_user_email(self, uid: str, new_email: str) -> bool:
        """
        Update user's email address
        
        Args:
            uid: User's unique ID
            new_email: New email address
            
        Returns:
            True if successful, False otherwise
        """
        if self.use_firebase:
            try:
                auth.update_user(
                    uid,
                    email=new_email
                )
                print(f"Successfully updated email for user: {uid}")
                return True
                
            except Exception as e:
                print(f"Error updating user email: {e}")
                return False
        else:
            # Simple auth doesn't support email updates
            return False
    
    def list_users(self) -> list:
        """
        List all users (for admin purposes)
        
        Returns:
            List of user records
        """
        if self.use_firebase:
            try:
                users = auth.list_users()
                user_list = []
                
                for user in users.users:
                    user_list.append({
                        "uid": user.uid,
                        "email": user.email,
                        "email_verified": user.email_verified,
                        "disabled": user.disabled
                    })
                
                return user_list
                
            except Exception as e:
                print(f"Error listing users: {e}")
                return []
        else:
            # Use simple authentication
            return list(self._simple_auth.users.values())

# Simple in-memory authentication for demo purposes
class SimpleAuthService:
    def __init__(self):
        """Simple in-memory authentication for demo purposes"""
        self.users = {
            "demo@example.com": {
                "password": "demo123",
                "email": "demo@example.com"
            }
        }
    
    def signup(self, email: str, password: str) -> bool:
        """Create a new user account"""
        if email in self.users:
            return False
        
        self.users[email] = {
            "password": password,
            "email": email
        }
        return True
    
    def login(self, email: str, password: str) -> bool:
        """Authenticate a user"""
        if email in self.users and self.users[email]["password"] == password:
            return True
        return False
    
    def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user information by email"""
        if email in self.users:
            return self.users[email]
        return None

# Initialize simple auth service for fallback
_simple_auth = SimpleAuthService()
