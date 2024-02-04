# Ensta - Free Instagram API
[![PyPI](https://img.shields.io/pypi/v/ensta)](https://pypi.org/project/ensta)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ensta)]()
[![Downloads](https://static.pepy.tech/badge/ensta)](https://pepy.tech/project/ensta)

<!-- ![Logo](https://raw.githubusercontent.com/diezo/Ensta/master/assets/image.jpg)  -->

Ensta uses a combination of Instagram's Web API & Mobile API making it a reliable choice over other third-party libraries. Also unlike other libraries, ensta always stays up-to-date.

Both authenticated & non-authenticated requests are supported.

[<img style="margin-top: 10px" src="https://raw.githubusercontent.com/diezo/Ensta/master/assets/coffee.svg" width="160"/>](https://buymeacoffee.com/diezo)

## Installation
Python [**3.10**](https://www.python.org/downloads/) or later is required.

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

host = Host(username, password)  # Email can also be used
```

</details>

<details>

<summary>SessionData Login</summary><br>

```python
from ensta import SessionHost

# "session_data" is stored in "ensta-session.txt" file by default.
# you can also get it using "host.session_data"
host = SessionHost(session_data)
```

</details>

<details>

<summary>2FA Login</summary><br>

**Authenticator App**

```python
from ensta import Host

# The key you got from Instagram when setting up your Authenticator App
key = "R65I7XTTHNHTQ2NKMQL36NCWKNUPBSDG"

host = Host(
    username,  # or email
    password,
    totp_token=key
)
```

**SMS Based**

No need to configure anything. Ensta will automatically ask for SMS OTP in the runtime.

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

<summary>Change Profile Picture</summary><br>

```python
from ensta import Mobile

mobile = Mobile(username, password)

mobile.change_profile_picture("image.jpg")
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

Any missing feature? Please raise an issue.

## Basic Usage

<details>

<summary><b>Host Class</b> (Authenticated)</summary>

Requires login through username & password.

```python
from ensta import Host

host = Host(username, password)
profile = host.profile("leomessi")

print(profile.biography)
```

</details>

<details>

<summary><b>Guest Class</b> (Non-Authenticated)</summary>

Doesn't require login, but has limited features.

```python
from ensta import Guest

guest = Guest()
profile = guest.profile("leomessi")

print(profile.biography)
```

</details>

[Learn to use ensta](https://github.com/diezo/Ensta/wiki/Getting-Started-With-Ensta)

## Discord Community
Ask questions, discuss upcoming features and meet other developers.

[<img src="https://i.ibb.co/qdX7F1b/IMG-20240105-115646-modified-modified.png" width="150"/>](https://discord.com/invite/pU4knSwmQe)

## Support Me
If you wish to support my work, please consider visiting this link:

[<img style="margin-top: 10px" src="https://raw.githubusercontent.com/diezo/Ensta/master/assets/coffee.svg" width="160"/>](https://buymeacoffee.com/diezo)

## Contributors
[![Contributors](https://contrib.rocks/image?anon=1&repo=diezo/ensta&)](https://github.com/diezo/ensta/graphs/contributors)

## Projects using Ensta
- [**Margot Bot**](https://instagram.com/enstabott): An Instagram Bot that changes it's biography every day to reflect the current weekday. (IST Timezone)
- [**Instagram REST API**](https://github.com/olgud/ensta-rest): A flask app that uses Ensta to deliver a third-party REST API for Instagram.

## Legal
This is a third party library and not associated with Instagram. We're strictly against spam. You are liable for all the actions you take.
