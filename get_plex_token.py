#!/usr/bin/env python3
"""
Get Plex Authentication Token
"""

import requests
import getpass

def get_plex_token():
    """Get Plex token using username/password"""
    print("🔑 PLEX TOKEN RETRIEVAL")
    print("="*50)
    print("This will get your Plex authentication token")
    print("Your credentials are only used to get the token, not stored")
    print()
    
    username = input("Plex username/email: ").strip()
    if not username:
        print("❌ Username required")
        return None
    
    password = getpass.getpass("Plex password: ")
    if not password:
        print("❌ Password required")
        return None
    
    headers = {
        'X-Plex-Client-Identifier': 'SubSync-Manager',
        'X-Plex-Product': 'SubSync Manager',
        'X-Plex-Version': '1.0'
    }
    
    try:
        print("🔄 Authenticating with Plex...")
        
        response = requests.post(
            'https://plex.tv/users/sign_in.json',
            headers=headers,
            data={
                'user[login]': username,
                'user[password]': password
            },
            timeout=30
        )
        
        if response.status_code == 201:
            data = response.json()
            token = data['user']['authToken']
            print(f"\n✅ Success! Your Plex token:")
            print(f"🔑 {token}")
            print(f"\n💡 Copy this token to use in the subtitle sync manager")
            return token
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            if response.status_code == 401:
                print("💡 Check your username/password")
            elif response.status_code == 422:
                print("💡 Invalid username/password format")
            return None
            
    except Exception as e:
        print(f"❌ Error getting token: {e}")
        return None

if __name__ == "__main__":
    get_plex_token()