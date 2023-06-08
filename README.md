# Ensta
This package lets you use Instagram's Internal API (Web API) through simple methods and classes.

It supports two type of classes - "Guest" and "Host"

[!["Buy me a coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://buymeacoffee.com/diezo)

## Installation
Open a terminal window and run this command:
```shell
pip install ensta
```

## Guest Mode
It doesn't require any type of login and can be used to fetch publicly available data like Profile Information, Username Availability etc.

```python
from ensta import Guest

guest = Guest()
biography = guest.get_biography("username")

print(biography)
```

## Host Mode
It requires login and can be used to manage your account or fetch information not available without logging in.

```python
from ensta import Host

sessionid = "12345678:abcdefgh"  # Copy SessionId from cookies

host = Host(sessionid)
result = host.follow_username("username")

print(result)
```

## Session ID
To get your instagram SessionId, run the [**fetch-sessionid.py**](https://github.com/diezo/ensta/blob/master/fetch-sessionid.py) script.

Alternatively, you can follow these steps if the above method didn't work for you:
- Open [instagram.com](https://instagram.com) in your browser
- Open DevTools (Ctrl + Shift + I)
- Go to **Application** tab
- Expand **Cookies** tab, and click on the first item
- Here you will find your Instagram User's current sessionid.
- Copy it and pass it as an argument whenever you are using the [**Host Class**](https://github.com/diezo/ensta#host-mode).

## Examples

### 1. Check if username is available

```python
from ensta import Guest

guest = Guest()
availability = guest.username_availability("cristiano89724")

print(availability)
```

Result:
```json
{"success": true, "available": true, "suggestions": ["cristiano89724", "cristiano897241", "cristiano8972441", "cristiano89724367", "cristiano897242760", "cristiano897244", "cristiano8972491", "cristiano89724386", "cristiano897244070", "cristiano8972438", "cristiano89724834"]}
```

<br></br>

### 2. Get Biography

```python
from ensta import Guest

guest = Guest()
biography = guest.get_biography("cristiano")

print(biography)
```

Result:
```json
{"success": true, "biography": "Join my NFT journey on @Binance. Click the link below to get started."}
```

<br></br>

### 3. Is Account Verified?

```python
from ensta import Guest

guest = Guest()
verified = guest.is_account_verified("cristiano")

print(verified)
```

Result:
```json
{"success": true, "verified": true}
```