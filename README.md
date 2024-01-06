# Ensta - Free Instagram API
[![PyPI](https://img.shields.io/pypi/v/ensta)](https://pypi.org/project/ensta)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ensta)]()
[![Downloads](https://static.pepy.tech/badge/ensta)](https://pepy.tech/project/ensta)
[![Twitter Share](https://img.shields.io/twitter/url?style=social&url=https%3A%2F%2Fgithub.com%2Fdiezo%2Fensta)](https://twitter.com/intent/tweet?text=Wow:&url=https%3A%2F%2Fgithub.com%2Fdiezo%2Fensta)

<!-- <img style="border-radius: 10px" src="https://raw.githubusercontent.com/diezo/Ensta/master/assets/logo.png"/> -->

Ensta uses a combination of Instagram's Web API & Mobile API making it a reliable choice over other third-party libraries. Also unlike other libraries, ensta always stays up-to-date.

Both authenticated & anonymous requests are supported.

[<img style="margin-top: 10px" src="https://www.buymeacoffee.com/assets/img/guidelines/download-assets-sm-1.svg" width="160"/>](https://buymeacoffee.com/diezo)

## 🌟 Just a minute!
Ensta is still in it's early stages and requires your support. Don't forget to give a star. Thank you!

## Installation
```shell
$ pip install ensta
```

## Supported Actions
Tap on the headings to view code:

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

<summary>2FA Login  (TOTP)</summary><br>

```python
from ensta import Host

host = Host(username, password, totp_token=token)
```

</details>

<details>

<summary>Upload Photo (Single Post)</summary><br>

```python
from ensta import Host

host = Host(username, password)

upload = host.get_upload_id("Picture.jpg")

host.upload_photo(upload, caption="Travelling 🌆")
```

</details>

<details>

<summary>Upload Multiple Photos (Single Post)</summary><br>

```python
from ensta import Host

host = Host(username, password)

upload1 = host.get_upload_id("First.jpg")
upload2 = host.get_upload_id("Second.jpg")
upload3 = host.get_upload_id("Third.jpg")

host.upload_photos([upload1, upload2, upload3], caption="Travelling 🌆")
```

</details>

<details>

<summary>Upload Reel</summary><br>

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

<summary>Username to UserID, and vice versa.</summary><br>

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

<summary>Fetch Someone's Feed</summary><br>

```python
from ensta import Host

host = Host(username, password)
posts = host.posts("leomessi", 100)  # Want full list? Set count to '0'

for post in posts:
    print(post.caption_text)
    print(post.like_count)    
```

</details>

<details>

<summary>Add Comment on Posts</summary><br>

```python
from ensta import Host

host = Host(username, password)

post_id = host.get_post_id("https://www.instagram.com/p/Czr2yLmroCQ/")

host.comment("Looks great!", post_id)
```

</details>

<details>

<summary>Like/Unlike Posts</summary><br>

```python
from ensta import Host

host = Host(username, password)

post_id = host.get_post_id("https://www.instagram.com/p/Czr2yLmroCQ/")

host.like(post_id)
host.unlike(post_id)
```

</details>

<details>

<summary>Fetch Post's Likers</summary><br>

```python
from ensta import Host

host = Host(username, password)

post_id = host.get_post_id("https://www.instagram.com/p/Czr2yLmroCQ/")
likers = host.likers(post_id)

for user in likers.users:
    print(user.username)
    print(user.profile_picture_url)
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

## Host Mode
Requires login through username & password.

```python
from ensta import Host

host = Host(username, password)
profile = host.profile("leomessi")

print(profile.biography)
```

## Guest Mode
Doesn't require login, but has limited features.

```python
from ensta import Guest

guest = Guest()
profile = guest.profile("leomessi")

print(profile.biography)
```

## Discord Community
Ask questions, discuss upcoming features and meet other developers.

[<img src="https://i.ibb.co/qdX7F1b/IMG-20240105-115646-modified-modified.png" width="150"/>](https://discord.com/invite/pU4knSwmQe)

## Legal
This is a third party library and not associated with Instagram. We're strictly against spam. You are liable for all the actions you take.
