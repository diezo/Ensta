from ensta import Guest, Host

sessionid = "<Replace with your session id>"

guest = Guest()  # Doesn't require login
host = Host(sessionid)  # Requires login through sessionid

print(guest.profile("cristiano"))  # Prints user's profile information
print(host.follow("cristiano"))  # Follows the username or uid mentioned
