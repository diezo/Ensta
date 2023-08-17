# 🤖 Ensta - Simple Instagram API
[![PyPI](https://img.shields.io/pypi/v/ensta)](https://pypi.org/project/ensta)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ensta)]()
[![Downloads](https://static.pepy.tech/badge/ensta)](https://pepy.tech/project/ensta)
[![Twitter Share](https://img.shields.io/twitter/url?style=social&url=https%3A%2F%2Fgithub.com%2Fdiezo%2Fensta)](https://twitter.com/intent/tweet?text=Wow:&url=https%3A%2F%2Fgithub.com%2Fdiezo%2Fensta)

<img style="border-radius: 10px" src="https://raw.githubusercontent.com/diezo/Ensta/master/assets/logo.png"/>

This package lets you use Instagram's Internal Web API through simple functions and classes. Ensta uses Instagram's Original Web API to scrape data which makes it a reliable choice over other third-party scrapers. This library mainly focuses on Simplicity & Reliability.

Two type of classes are supported - ***Guest & Host***.

[<img style="margin-top: 10px" src="https://www.buymeacoffee.com/assets/img/guidelines/download-assets-sm-1.svg" width="160"/>](https://buymeacoffee.com/diezo)

## Installation
To install this package, run the below command in a terminal window:
```shell
$ pip install ensta --upgrade
```

## 🧔🏻‍♂️ Guest Mode
This mode doesn't require login and can be used to fetch publicly available data from Instagram's Servers.

Here's an example where an instance of *Guest Class* is created to fetch [Cristiano Ronaldo's](https://www.instagram.com/cristiano/) profile information:

```python
from ensta import Guest

guest = Guest()
profile = guest.profile("cristiano")

if profile is not None:
    print(profile.biography)
    print(profile.follower_count)
    print(profile.following_count)
```

## 🧔🏻‍♂️ Host Mode
This mode requires login through *Username* & *Password*.
It can be used to take actions that require login. Additionally, users can update their own profile through this class.

Here's an example where an instance of *Host Class* is created to follow [Cristiano Ronaldo's](https://www.instagram.com/cristiano/) account:

```python
from ensta import Host

host = Host("username", "password")
status = host.follow("cristiano")

print(status)
```

### Code Samples:
1. **Fetch Followers / Followings List**
    ```python
    from ensta import Host

    host = Host("username", "password")
   
    followers = host.followers("cristiano")
    followings = host.followings("cristiano")

    for user in followers: print(user.username)
    for user in followings: print(user.username)
    ```

3. **Follow / Unfollow People**
    ```python
    from ensta import Host
    
    host = Host("username", "password")
   
    print(host.follow("cristiano"))
    print(host.unfollow("cristiano"))
    ```

## ❤️ Support Me
If you'd like to support me in developing Ensta, please consider donating here: 

[<img src="https://www.buymeacoffee.com/assets/img/guidelines/download-assets-sm-1.svg" width="150"/>](https://buymeacoffee.com/diezo)

## Disclaimer
This is a third-party package, and not approved by Instagram. It doesn't promote illegal activities or activities that violate [Instagram's Community Guidelines](https://help.instagram.com/477434105621119/) such as spamming users, creating bot accounts, misusing data etc. You are solely responsible for all the actions you take using this package.
