# Ensta - Free Instagram API
[![PyPI](https://img.shields.io/pypi/v/ensta)](https://pypi.org/project/ensta)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ensta)]()
[![Downloads](https://static.pepy.tech/badge/ensta)](https://pepy.tech/project/ensta)
[![Twitter Share](https://img.shields.io/twitter/url?style=social&url=https%3A%2F%2Fgithub.com%2Fdiezo%2Fensta)](https://twitter.com/intent/tweet?text=Wow:&url=https%3A%2F%2Fgithub.com%2Fdiezo%2Fensta)

<!-- <img style="border-radius: 10px" src="https://raw.githubusercontent.com/diezo/Ensta/master/assets/logo.png"/> -->

Ensta uses Instagram's Internal Web API for data scraping which makes it a reliable choice over other third-party libraries. Also unlike other libraries, ensta always stays up-to-date.

Both authenticated & anonymous requests are supported.

[<img style="margin-top: 10px" src="https://www.buymeacoffee.com/assets/img/guidelines/download-assets-sm-1.svg" width="160"/>](https://buymeacoffee.com/diezo)

## Installation
Run this command:
```shell
$ pip install ensta --upgrade
```

## Supported Actions
You can do a lot with ensta, here's some code:

<details>

<summary>Proxy Support</summary><br>

```python
from ensta import Host

host = Host(username, password, proxy={"http": "http://1.2.3.4", "https": "https://1.2.3.4"})
```

</details>

<details>

<summary>Username Password Login</summary><br>

```python
from ensta import Host

host = Host(username, password)
```

</details>

<details>

<summary>Upload Posts</summary><br>

```python
from ensta import Host

host = Host(username, password)

host.upload_post(
    photo_path="Picture.jpg",
    caption="Travelling 🌆",
)
```

</details>

<details>

<summary>Upload Reels</summary><br>

```python
from ensta import Host

host = Host(username, password)

host.upload_reel(
    video_path="Video.mp4",
    thumbnail_path="Thumbnail.jpg",
    caption="Enjoying the winter! ⛄"
)
```

</details>

<details>

<summary>Check Username Availability</summary><br>

```python
from ensta import Guest

guest = Guest()

print(guest.username_availability("theusernameiwant"))
```

</details>

<details>

<summary>Fetch Profile Data</summary><br>

```python
from ensta import Host

host = Host(username, password)
profile = host.profile("leomessi")

print(profile.full_name)
print(profile.biography)
print(profile.follower_count)
```

</details>

<details>

<summary>Convert Username to UID, and vice versa.</summary><br>

```python
from ensta import Host

host = Host(username, password)

username = host.get_username(427553890)
uid = host.get_uid("leomessi")

print(username, uid)
```

</details>

<details>

<summary>Follow / Unfollow Users</summary><br>

```python
from ensta import Host

host = Host(username, password)

print(host.follow("leomessi"))
print(host.unfollow("leomessi"))
```

</details>

<details>

<summary>Generate Followers / Followings List</summary><br>

```python
from ensta import Host

host = Host(username, password)

followers = host.followers("leomessi", count=100)  # Want full list? Set count to '0'
followings = host.followings("leomessi", count=100)  # Want full list? Set count to '0'

for user in followers:
    print(user.username)

for user in followings:
    print(user.username)
```

</details>

<details>

<summary>Switch Account Type - Public/Private</summary><br>

```python
from ensta import Host

host = Host(username, password)

print(host.switch_to_public_account())
print(host.switch_to_private_account())
```

</details>

<details>

<summary>Fetch Someone's Posts</summary><br>

```python
from ensta import Host

host = Host(username, password)
posts = host.posts("leomessi", 100)  # Want full list? Set count to '0'

for post in posts:
    print(post.caption_text)
    print(post.like_count)
    
    ...
```

</details>

<details>

<summary>Fetch Data of Individual Post</summary><br>

```python
from ensta import Host

host = Host(username, password)
post = host.post("https://www.instagram.com/p/Czgyw07t_c3/")

print(post.caption_text)
print(post.like_count)

...
```

</details>

<details>

<summary>Like/Unlike Posts</summary><br>

```python
...

post.like()
post.unlike()
```

</details>

<details>

<summary>Edit Biography, Display Name</summary><br>

```python
from ensta import Host

host = Host(username, password)

host.change_display_name("Lionel Messi")
host.change_bio("Athlete")
```

</details>

<details>

<summary>Fetch Your Email, Gender, Birthday, etc.</summary><br>

```python
from ensta import Host

host = Host(username, password)
me = host.private_info()

print(me.email)
print(me.gender)
print(me.birthday)
```

</details>

Any missing feature? Raise an issue.

## Host Mode (Recommended)
Requires login through username & password.

```python
from ensta import Host

host = Host(username, password)
profile = host.profile("leomessi")

print(profile.biography)
```

## Guest Mode
Doesn't require login but has very limited features. Doesn't always work, so Host Mode is recommended.

```python
from ensta import Guest

guest = Guest()
profile = guest.profile("leomessi")

print(profile.biography)
```

## ❤️ Donate
Want this project to keep running? Please consider donating here:

[<img src="https://www.buymeacoffee.com/assets/img/guidelines/download-assets-sm-1.svg" width="150"/>](https://buymeacoffee.com/diezo)

## 👮 Legal
This is a third-party library and not associated with Instagram. We are strictly against any activity that may violate [Instagram's Community Guidelines](https://help.instagram.com/477434105621119/) or [Terms of use](https://help.instagram.com/581066165581870). You are the only one liable for such actions.
