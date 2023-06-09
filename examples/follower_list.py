"""
    This script can generate information about a specific user's followers (say usernames, full names etc.)

    1. Install ensta library by running: pip install ensta
    2. Run this script: python3 follower_list.py
"""

# Import Required Libraries
from ensta import Host

# Collect Data
sessionId = input("SessionId: ")
target_username = input("Target username: ")
print("")

# Initialize Host Class (Requires Login With SessionId)
host = Host(sessionId)

# Required Arguments - IDENTIFIER (Either Username or UserId), Count (Number Of Followers To Fetch)
followers = host.follower_list(target_username, 10)

# Iterate Through List
# todo work here and other file in this dir
if followers.success:
    for follower in followers.users:
        print(follower)
# for follower_data in followers["follower_list"]:
#     follower = Follower(follower_data)  # Pass Follower Data To This Class
#
#     print(f"Username: {follower.username}")
