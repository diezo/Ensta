# 🤖 Ensta - Simple Instagram API
This package lets you use Instagram's Internal Web API through simple functions and classes, that can help developers like you build your dream projects with very few and reliable lines of code.

It supports three types of classes - *Guest*, *Host*, *Stream*.

[!["Buy me a coffee"](https://www.buymeacoffee.com/assets/img/custom_images/purple_img.png)](https://buymeacoffee.com/diezo)

## Installation
It's recommended to install this package using [Python's PIP](https://pypi.org/project/pip/), as the GitHub versions may be unstable and may require testing before being used in production.

To install this library, run this command in a terminal window:
```shell
pip install ensta
```

To upgrade the installed version of this library, run:
```shell
pip install ensta --upgrade
```

## Guest Mode
This mode doesn't require login and can be used to fetch publicly available data from Instagram's Servers. Following methods are supported till now:
- Check if username is available
- Fetch someone's profile information
- Convert username to userid
- Convert userid to username

Here's an example where an instance of *Guest* is created to fetch [Cristiano Ronaldo's](https://www.instagram.com/cristiano/) profile information:

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

## Host Mode
This mode requires the user to login through their [SessionID](https://github.com/diezo/ensta#session-id). SessionID shall be passed as an argument while initializing this class. It can be used to fetch data that's available only when the user is logged in. Additionally, the user can perform several actions on their profile.

Methods supported till now are listed below:
- Check authentication status of the user
- Follow someone's account
- Unfollow someone's account
- Get someone's follower list of specified size
- Get someone's following list of specified size
- Toggle account privacy - 'Private' or 'Public'

Here's an example where an instance of *Host* is created to follow [Cristiano Ronaldo's](https://www.instagram.com/cristiano/) profile:

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

## Stream Mode
This mode pulls data at realtime, so the program can process it simultaneously. It requires login through [SessionID](https://github.com/diezo/ensta#session-id).

In a situation where you might need to fetch someone's entire follower list, this mode comes handy.

These are the methods supported till now:
- Fetch someone's follower list
- Fetch someone's following list

Here's an example where an instance of *Stream* is created to fetch [Cristiano Ronaldo's](https://www.instagram.com/cristiano/) first 100 followers:

```python
from ensta import Stream

sessionid = "123456:abcdefg"  # Place your SessionId here

stream = Stream(sessionid)
followers = stream.followers("cristiano")

for user in followers:
    if user is None:
        print("Something went wrong.")
        break

    print(user.username)
    print(user.full_name)
```

## Considerations
Here are some key points to consider when using this library in production:
- You can use *Guest*, *Host* & *Stream* classes simultaneously, and create multiple instances of the same class when required.
- Functions should return *None* on failure. So, add clauses for the same.

- Some functions take Identifier as an argument while others take Username. These are the key differences between the two:
  - The argument **Identifier** means you can pass either Username or UserID.
  - The argument **Username** means you must pass the Username only, and not the UserID.

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