# 🤖 Ensta - Simple Instagram API
This library  lets you use Instagram's Internal Web API through simple functions and classes, that can help developers like you build projects with a few and reliable lines of code.

It supports three two of classes - *Guest* & *Host*.

[!["Buy me a coffee"](https://www.buymeacoffee.com/assets/img/custom_images/purple_img.png)](https://buymeacoffee.com/diezo)

## Installation
To install this library using [Python's PIP](https://pypi.org/project/pip/), run this command in a command-line interface:
```shell
pip install ensta
```

To upgrade to the latest version, run:
```shell
pip install ensta --upgrade
```

## 😶 Guest Mode
This mode doesn't require login and can be used to fetch publicly available data from Instagram's Servers. Following methods are supported till now:
- Check if username is available for registration
- Fetch someone's profile data
- Convert username to userid
- Convert userid to username

Here's an example where an instance of *Guest* Class is created to fetch [Cristiano Ronaldo's](https://www.instagram.com/cristiano/) profile information:

```python
from ensta import Guest

guest = Guest()
profile = guest.profile("cristiano")

if profile is None:
    print("Something went wrong.")
else:
    print(profile.biography)
    print(profile.follower_count)
    print(profile.following_count)
```

## 🧔🏻‍♂️ Host Mode
This mode requires login through [SessionID](https://github.com/diezo/ensta#session-id). The SessionID should be passed as an argument while initializing this class. It can be used to fetch data that requires login. Additionally, users can perform several actions on their profile.

These are the methods supported till now:
- Check authentication status of the user
- Send follow request to an account
- Follow/unfollow accounts
- Fetch someone's follower/following list
- Toggle account privacy - 'Public' or 'Private'

Here's an example where an instance of *Host* Class is created to follow [Cristiano Ronaldo's](https://www.instagram.com/cristiano/) account:

```python
from ensta import Host

sessionid = "123456:abcdefg"  # Place your SessionId here

host = Host(sessionid)
status = host.follow("cristiano")

if status is None:
    print("Something went wrong.")
else:
    if status.following:
        print("Following!")
    
    elif status.follow_requested:
        print("Requested to follow!")
```

## Important
Every function should return **None** on failure. So, it's recommended to an add if statement before using the actual data to avoid TypeError. Here's an example:
```python
from ensta import Guest

guest = Guest()
available = guest.username_availability("cristiano")

if available is None:  # Operation failed
    print("Something went wrong.")
else:
    print(available)
```

## Session ID
When you log in to *instagram.com* in your browser, your browser store your credentials in the form of [Cookies](https://en.wikipedia.org/wiki/HTTP_cookie). The type of cookie that instagram uses to remember your session is 'SessionID'.

In order to use the [Host Class](https://github.com/diezo/ensta#host-mode), you need to pass this cookie as an argument so that Ensta can use it to log into your account. Follow these steps to get your SessionID:
- Visit [Instagram.com](https://instagram.com) and log into your account.
- Once you're logged in, open DevTools (Ctrl + Shift + I).
- Switch to **Application** tab.
- Under *Storage* options, expand the **Cookies** tab, and tap the first item.
- Once done, you will see the list of all cookies.
- Copy value of cookie named 'sessionid' and pass it as an argument whenever you use the **Host Class**.

An alternative way to automatically fetch SessionID is to run the [fetch-sessionid.py](https://github.com/diezo/ensta/blob/master/fetch-sessionid.py) script. Currently, this script can only fetch cookies from Google Chrome, and not any other browser.

## Donate ❤️
If this library has added value to your projects, you may consider supporting me in the development of this library by donating here:

[!["Buy me a coffee"](https://www.buymeacoffee.com/assets/img/custom_images/purple_img.png)](https://buymeacoffee.com/diezo)

## Disclaimer
This is a third-party library, not an official library from Instagram. The use of the library does not promote creation of bot accounts or spamming Instagram Users. You are liable for all the actions you take through this library. Use of such libraries maybe against [Instagram's Community Guidelines](https://help.instagram.com/477434105621119/).