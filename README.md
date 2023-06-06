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

sessionid = "12345678:abcdefgh"

host = Host(sessionid)
result = host.follow_username("username")

print(result)
```