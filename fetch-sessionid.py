# Libraries
import browser_cookie3
from urllib.parse import unquote

# Colors
colors = {
    "OK": "\033[92m",
    "FAIL": "\033[91m",
    "END": "\033[0m"
}

# Extract Cookies
cookies = browser_cookie3.chrome(domain_name=".instagram.com")
sessionId = ""

# Find SessionId
for item in cookies:
    if item.name == "sessionid":
        sessionId = unquote(item.value).strip()

# Validate SessionId
if sessionId != "":
    print(f"{colors['OK']}Session ID: {colors['END']}{sessionId}")
else:
    print(f"{colors['FAIL']}SessionId not found. Make sure you've logged into instagram.com in Chrome Browser.{colors['END']}")
