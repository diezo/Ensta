# Ensta - Free Instagram API
[![PyPI](https://img.shields.io/pypi/v/ensta)](https://pypi.org/project/ensta)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ensta)]()
[![Downloads](https://static.pepy.tech/badge/ensta)](https://pepy.tech/project/ensta)
[![Twitter Share](https://img.shields.io/twitter/url?style=social&url=https%3A%2F%2Fgithub.com%2Fdiezo%2Fensta)](https://twitter.com/intent/tweet?text=Wow:&url=https%3A%2F%2Fgithub.com%2Fdiezo%2Fensta)

<!-- <img style="border-radius: 10px" src="https://raw.githubusercontent.com/diezo/Ensta/master/assets/logo.png"/> -->

Ensta uses Instagram's Internal Web API for data scraping which makes it a reliable choice over other third-party libraries. Also unlike other libraries, ensta always remains up-to-date.

Two type of classes are supported - ***Guest & Host***.

[<img style="margin-top: 10px" src="https://www.buymeacoffee.com/assets/img/guidelines/download-assets-sm-1.svg" width="160"/>](https://buymeacoffee.com/diezo)

## Installation
Run this command:
```shell
$ pip install ensta --upgrade
```

## Supported Actions
You can do a lot with ensta, here's a list:

- Username/Password & SessionID login
- Check Username Availability
- Fetch Profile Data
- Convert Username to UID, and vice versa.
- Follow/Unfollow Users
- Generate Followers/Followings List
- Change Account Type - Public/Private
- Generate Posts List
- Fetch Post Data
- Like/Unlike Post
- Edit Biography & Display Name
- Fetch your Email, Gender, Date of birth, etc.

Any missing feature? Raise an issue.

## 🧔🏻‍♂️ Host Mode
Requires login through Username/Password or SessionId. Can fetch data that requires login. Can update your profile info.

Example:

```python
from ensta import Host

host = Host(username, password)

print(host.follow("leomessi"))
print(host.unfollow("leomessi"))
print(host.profile("leomessi"))
```

## 🧔🏻‍♂️ Guest Mode
Doesn't require login but is limited to certain actions.

Example:

```python
from ensta import Guest

guest = Guest()
print(guest.profile("leomessi"))
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
