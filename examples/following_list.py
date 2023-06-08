"""
    This script can generate information about a specific user's following (say usernames, full names etc.)

    1. Install ensta library by running: pip install ensta
    2. Run this script: python3 following_list.py
"""

# Import Required Libraries
from ensta import Host
from ensta import Following
from ensta.identifier import IDENTIFIER_USERNAME

# Collect Data
sessionId = input("SessionId: ")
target_username = input("Target username: ")
print("")

# Initialize Host Class (Requires Login With SessionId)
host = Host(sessionId)

# Required Arguments - IDENTIFIER_TYPE, IDENTIFIER (Username or UserId), Number Of Items To Get
followings = host.following_list(IDENTIFIER_USERNAME, target_username, 10)

# Iterate Through List
for following_data in followings["following_list"]:
    following = Following(following_data)  # Pass Following Data To This Class

    print(f"Username: {following.username}")
