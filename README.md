# Ensta - Simple Instagram API
[![PyPI](https://img.shields.io/pypi/v/ensta)](https://pypi.org/project/ensta)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ensta)]()
[![Downloads](https://static.pepy.tech/badge/ensta)](https://pepy.tech/project/ensta)

![Logo](https://raw.githubusercontent.com/diezo/Ensta/master/assets/image.jpg)

Ensta is a simple, reliable and up-to-date python package for Instagram API.

Both **authenticated** and **anonymous** requests are supported.

[<img style="margin-top: 10px" src="https://raw.githubusercontent.com/diezo/Ensta/master/assets/coffee.svg" width="180"/>](https://buymeacoffee.com/sonii)
<!--
## <img src="https://raw.githubusercontent.com/diezo/Ensta/master/assets/colorful-instagram-icon-vintage-style-art-vector-illustration_836950-30.jpg" width="23"> Account Creator
Download an Instagram [**Account Creator**](https://sonii.gumroad.com/l/account-creator/EARLY20) written in Python.

- Auto-generates **DuckDuckGo Private Email Addresses**.
- Auto-fetches OTP from **ProtonMail Inbox**.
- Auto-updates Profile Picture to an **AI-Generated Human Face**.
- Sets a random **AI-Generated Biography** on account creation.

Creator should only be used for legitimate purposes. [**Discord**](https://discordapp.com/users/1183040947035062382)
-->

## Installation
Read the [**pre-requisites**](https://github.com/diezo/Ensta/wiki/Pre%E2%80%90requisites) here.

    pip install ensta

## Example
Fetching profile info by username:
```python
from ensta import Mobile

mobile = Mobile(username, password)

profile = mobile.profile("leomessi")

print(profile.full_name)
print(profile.biography)
print(profile.profile_pic_url)
```

## Features
These features use the **Mobile API**.

<details>

<summary>Using Proxies</summary><!--github-line-break--><br>

When to use a proxy:
- You're being rate limited.
- Ensta is not working because your Home IP is flagged.
- You're deploying Ensta to the cloud. (Instagram blocks requests from IPs of cloud providers, so a proxy must be used)

```python
from ensta import Mobile

mobile = Mobile(
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

<summary>Username-Password Login</summary><!--github-line-break--><br>

Username is recommended to sign in. However, email can also be used.

```python
from ensta import Mobile

# Recommended
mobile = Mobile(username, password)

# This also works
mobile = Mobile(email, password)
```

</details>

<details>

<summary>Change Profile Picture</summary><!--github-line-break--><br>

```python
from ensta import Mobile

mobile = Mobile(username, password)

mobile.change_profile_picture("image.jpg")
```

</details>

<details>

<summary>Fetch Profile Information</summary><!--github-line-break--><br>

```python
from ensta import Mobile

mobile = Mobile(username, password)

profile = mobile.profile("leomessi")

print(profile.full_name)
print(profile.biography)
print(profile.follower_count)
```

</details>

<details>

<summary>Follow/Unfollow Account</summary><!--github-line-break--><br>

```python
from ensta import Mobile

mobile = Mobile(username, password)

mobile.follow("leomessi")
mobile.unfollow("leomessi")
```

</details>

<details>

<summary>Change Biography</summary><!--github-line-break--><br>

```python
from ensta import Mobile

mobile = Mobile(username, password)

mobile.change_biography("New bio here.")
```

</details>

<details>

<summary>Switch to Private/Public Account</summary><!--github-line-break--><br>

```python
from ensta import Mobile

mobile = Mobile(username, password)

mobile.switch_to_private_account()
mobile.switch_to_public_account()
```

</details>

<details>

<summary>Username to UserID / UserID to Username</summary><!--github-line-break--><br>

```python
from ensta import Mobile

mobile = Mobile(username, password)

mobile.username_to_userid("leomessi")
mobile.userid_to_username("12345678")
```

</details>

<details>

<summary>Like/Unlike Post</summary><!--github-line-break--><br>

```python
from ensta import Mobile

mobile = Mobile(username, password)

mobile.like(media_id)
mobile.unlike(media_id)
```

</details>

<details>

<summary>Fetch Followers/Followings</summary><!--github-line-break--><br>

```python
from ensta import Mobile

mobile = Mobile(username, password)

followers = mobile.followers("leomessi")
followings = mobile.followings("leomessi")

for user in followers.list:
    print(user.full_name)

for user in followings.list:
    print(user.full_name)

# Fetching next chunk
followers = mobile.followers(
    "leomessi",
    next_cursor=followers.next_cursor
)
```

</details>

<details>

<summary>Add Comment to Post</summary><!--github-line-break--><br>

```python
from ensta import Mobile

mobile = Mobile(username, password)

mobile.comment("Hello", media_id)
```

</details>

<details>

<summary>Upload Photo</summary><!--github-line-break--><br>

```python
from ensta import Mobile

mobile = Mobile(username, password)

mobile.upload_photo(
    upload_id=upload_id,
    caption="Hello"
)
```

</details>

<details>

<summary>Upload Sidecar (Multiple Photos)</summary><!--github-line-break--><br>

```python
from ensta import Mobile
from ensta.structures import SidecarChild

mobile = Mobile(username, password)

mobile.upload_sidecar(
    children=[
        SidecarChild(uploda_id),
        SidecarChild(uploda_id),
        SidecarChild(uploda_id)
    ],
    caption="Hello"
)
```

</details>

<details>

<summary>Fetch Private Information (Yours)</summary><!--github-line-break--><br>

```python
from ensta import Mobile

mobile = Mobile(username, password)

account = mobile.private_info()

print(account.email)
print(account.account_type)
print(account.phone_number)
```

</details>

<details>

<summary>Update Display Name</summary><!--github-line-break--><br>

```python
from ensta import Mobile

mobile = Mobile(username, password)

mobile.update_display_name("Lionel Messi")
```

</details>

<details>

<summary>Block/Unblock User</summary><!--github-line-break--><br>

```python
from ensta import Mobile

mobile = Mobile(username, password)

mobile.block(123456789)  # Use UserID
mobile.unblock(123456789)  # Use UserID
```

</details>

<details>

<summary>Upload Story (Photo)</summary>

```python
from ensta import Mobile

mobile = Mobile(username, password)

upload_id = mobile.get_upload_id("image.jpg")

mobile.upload_story(upload_id)
```

</details>

<details>

<summary>Upload Story (Photo) + Link Sticker</summary>

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

<summary>Send Message (Picture)</summary>

```python
from ensta import Mobile

mobile = Mobile(username, password)  # Or use email
direct = mobile.direct()

media_id = direct.fb_upload_image("image.jpg")

direct.send_photo(media_id, thread_id)
```

</details>

<details>

<summary>Add Biography Link</summary>

```python
from ensta import Mobile

mobile = Mobile(username, password)  # Or use email

link_id = mobile.add_bio_link(
    url="https://github.com/diezo",
    title="Diezo's GitHub"
)
```

</details>

<details>

<summary>Add Multiple Biography Links</summary>

```python
from ensta import Mobile
from ensta.structures import BioLink

mobile = Mobile(username, password)  # Or use email

link_ids = mobile.add_bio_links([
    BioLink(url="https://example.com", title="Link 1"),
    BioLink(url="https://example.com", title="Link 2"),
    BioLink(url="https://example.com", title="Link 3")
])
```

</details>

<details>

<summary>Remove Biography Link</summary>

```python
from ensta import Mobile

mobile = Mobile(username, password)  # Or use email

mobile.remove_bio_link(link_id)
```

</details>

<details>

<summary>Remove Multiple Biography Links</summary>

```python
from ensta import Mobile

mobile = Mobile(username, password)  # Or use email

mobile.remove_bio_links([
    link_id_1,
    link_id_2,
    link_id_3
])
```

</details>

<details>

<summary>Clear All Biography Links</summary>

```python
from ensta import Mobile

mobile = Mobile(username, password)  # Or use email

mobile.clear_bio_links()
```

</details>

### Deprecated Features (Web API)
Features still using the **Web API**:

<details>

<summary>Upload Reel</summary><!--github-line-break--><br>

```python
from ensta import Web

host = Web(username, password)

video_id = host.upload_video_for_reel("Video.mp4", thumbnail="Thumbnail.jpg")

host.pub_reel(
    video_id,
    caption="Enjoying the winter! ⛄"
)
```

</details>

<details>

<summary>Fetch Web Profile Data</summary><!--github-line-break--><br>

```python
from ensta import Web

host = Web(username, password)
profile = host.profile("leomessi")

print(profile.full_name)
print(profile.biography)
print(profile.follower_count)
```

</details>

<details>

<summary>Fetch Someone's Feed</summary><!--github-line-break--><br>

```python
from ensta import Web

host = Web(username, password)
posts = host.posts("leomessi", 100)  # Want full list? Set count to '0'

for post in posts:
    print(post.caption_text)
    print(post.like_count)    
```

</details>

<details>

<summary>Fetch Post's Likers</summary><!--github-line-break--><br>

```python
from ensta import Web

host = Web(username, password)

post_id = host.get_post_id("https://www.instagram.com/p/Czr2yLmroCQ/")
likers = host.likers(post_id)

for user in likers.users:
    print(user.username)
    print(user.profile_picture_url)
```

</details>

They'll be migrated to the **Mobile API** soon.

## Supported Classes

> [!IMPORTANT]
> The **Web Class** is deprecated and it's features are being migrated to the **Mobile Class**. It'll be removed from Ensta upon completion.

<details>

<br>

<summary><b>Mobile Class</b> (Authenticated)</summary>

Requires login, and has the most features.

```python
from ensta import Mobile

mobile = Mobile(username, password)
profile = mobile.profile("leomessi")

print(profile.full_name)
print(profile.biography)
print(profile.profile_pic_url)
```

</details>

<details>

<br>

<summary><b>Guest Class</b> (Non-Authenticated)</summary>

Doesn't require login, but has limited features.

```python
from ensta import Guest

guest = Guest()
profile = guest.profile("leomessi")

print(profile.biography)
```

</details>

<details>

<br>

<summary><b>Web Class</b> (Authenticated) <i>(Deprecated)</i></summary>

```python
from ensta import Web

host = Web(username, password)
profile = host.profile("leomessi")

print(profile.biography)
```

</details>

## Discord Community
Ask questions, discuss upcoming features and meet other developers.

[<img src="https://i.ibb.co/qdX7F1b/IMG-20240105-115646-modified-modified.png" width="150"/>](https://discord.com/invite/pU4knSwmQe)

## Buy Me A Coffee
Support me in the development of this project.

[<img src="https://raw.githubusercontent.com/diezo/Ensta/master/assets/coffee.svg" width="170"/>](https://buymeacoffee.com/sonii)

## Contributors
[![Contributors](https://contrib.rocks/image?anon=1&repo=diezo/ensta&)](https://github.com/diezo/ensta/graphs/contributors)

## Disclaimer
This is a third party library and not associated with Instagram. We're strictly against spam. You are liable for all the actions you take.
