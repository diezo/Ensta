# Ensta - Simple Instagram API
[![PyPI](https://img.shields.io/pypi/v/ensta)](https://pypi.org/project/ensta)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ensta)]()
[![Downloads](https://static.pepy.tech/badge/ensta/month)](https://pepy.tech/project/ensta)

![Instagram](https://img.shields.io/badge/Instagram-%23E4405F.svg?style=for-the-badge&logo=Instagram&logoColor=white)

<!-- ![Logo](https://raw.githubusercontent.com/diezo/Ensta/master/assets/image.jpg)  -->

Ensta uses a combination of Instagram's Web API & Mobile API making it a reliable choice over other third-party libraries. Also unlike other libraries, ensta always stays up-to-date.

Both authenticated & non-authenticated requests are supported.

[<img style="margin-top: 10px" src="https://raw.githubusercontent.com/diezo/Ensta/master/assets/coffee.svg" width="160"/>](https://buymeacoffee.com/sonii)

## Installation
Python [**3.10**](https://www.python.org/downloads/) or later is required.

```shell
$ pip install ensta
```

## Example
An example using the Host Class:
```python
from ensta import Host

# Login
host = Host(username, password)

# Fetch someone's profile
profile = host.profile("leomessi")

# Print profile info
print(profile.biography)
print(profile.is_private)
print(profile.profile_picture_url_hd)
```

## Bypass IP Restrictions
If you're being rate limited when using Ensta on your home network or Ensta doesn't work when you deploy your app to the cloud, you should consider using a reputed proxy. Here's how to do that:
1. Visit [abcproxy](https://www.abcproxy.com/?code=O4H3OC0O) and apply coupon ```O4H3OC0O``` for additional discount.
2. Buy a residential SOCKS5 proxy there.
3. Configure Ensta to use that proxy. See the [**Features**](https://github.com/diezo/ensta?tab=readme-ov-file#features) section.

## Features
Tap on the headings to view code:

<details>

<summary>Using Proxies</summary><br>

When you should use a proxy:
- You're being rate limited when using the **Guest Class**.
- Ensta is not working because your Home IP is flagged.
- You're deploying Ensta to the cloud. (Instagram blocks requests from IPs of cloud providers, so a proxy must be used)

```python
from ensta import Host

host = Host(
    username,
    password,
    proxy={
        "http": "socks5://username:password@host:port",
        "https": "socks5://username:password@host:port"
    }
)
```

Ensta uses the same proxy settings as the **requests** module.

</details>

<details>

<summary>Username-Password Login</summary><br>

We recommend using your email address to sign in. But if you have multiple accounts created on the same email address, you may consider using your username instead.

```python
from ensta import Host

# Recommended
host = Host(email, password)

# This also works
host = Host(username, password)
```

</details>

<details>

<summary>SessionData Login</summary><br>

Ensta will automatically save your login session in a file named ```ensta-session.json``` and reuse it until it expires.

But, if you wish to load a session manually, you can use the **SessionHost Class** instead of **Host Class** by passing your session data (which is stored inside ```ensta-session.json```) as a string.

```python
from ensta import SessionHost

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

**SMS Based:** Ensta will prompt you for the OTP in the runtime.

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

<details>

<summary>Block/Unblock User</summary><br>

```python
from ensta import Mobile

mobile = Mobile(username, password)

mobile.block(123456789)  # Use UserID
mobile.unblock(123456789)  # Use UserID
```

</details>

### Stories
<details>

<summary>Upload Story (Picture)</summary>

```python
from ensta import Mobile

mobile = Mobile(username, password)

upload_id = mobile.get_upload_id("image.jpg")

mobile.upload_story(upload_id)
```

</details>

<details>

<summary>Upload Story (Picture) + Link Sticker</summary>

```python
from ensta import Mobile
from ensta.structures import StoryLink

mobile = Mobile(username, password)

upload_id = mobile.get_upload_id("image.jpg")

mobile.upload_story(upload_id, entities=[
    StoryLink(title="Google", url="https://google.com")
])
```

</details>

### Direct Messaging
<details>

<summary>Send Message (Text)</summary>

```python
from ensta import Mobile

mobile = Mobile(username, password)  # Or use email
direct = mobile.direct()

direct.send_text("Hello", thread_id)
```

</details>

<details>

<summary>Send Photo</summary>

```python
from ensta import Mobile

mobile = Mobile(username, password)  # Or use email
direct = mobile.direct()

media_id = direct.fb_upload_image("image.jpg")

direct.send_photo(media_id, thread_id)
```

</details>

Any missing feature? Please raise an issue.

## Supported Classes

<details>

<br>

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

<br>

<summary><b>Guest Class</b> (Non-Authenticated)</summary>

Doesn't require login, but has limited features. See [this](https://github.com/diezo/Ensta?tab=readme-ov-file#bypass-ip-restrictions) if this class isn't working.

```python
from ensta import Guest

guest = Guest()
profile = guest.profile("leomessi")

print(profile.biography)
```

</details>

<details>

<br>

<summary><b>Mobile Class</b> (New)</summary>

Same as **Host Class** but uses the Mobile API. We're working on adding more features to this class.

```python
from ensta import Mobile

mobile = Mobile(username, password)

mobile.follow("leomessi")
```

</details>

[**Learn to use ensta**](https://github.com/diezo/Ensta/wiki/Getting-Started-With-Ensta)

## Discord Community
Ask questions, discuss upcoming features and meet other developers.

[<img src="https://i.ibb.co/qdX7F1b/IMG-20240105-115646-modified-modified.png" width="150"/>](https://discord.com/invite/pU4knSwmQe)

## Donate ❤️
If this library has added value to your projects, you may consider supporting me in the development of this library by donating here:

[<img src="https://www.buymeacoffee.com/assets/img/guidelines/download-assets-sm-1.svg" width="150"/>](https://buymeacoffee.com/sonii)

## Contributors
[![Contributors](https://contrib.rocks/image?anon=1&repo=diezo/ensta&)](https://github.com/diezo/ensta/graphs/contributors)

## Legal
This is a third party library and not associated with Instagram. We're strictly against spam. You are liable for all the actions you take.
