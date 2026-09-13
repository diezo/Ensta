"""Browser identity headers shared by the web (www.instagram.com) clients.

Instagram validates that the ``user-agent`` and the ``sec-ch-ua*`` client
hints describe the same browser. The values below must therefore be kept in
sync with each other; bump ``CHROME_MAJOR`` to move to a newer Chrome.
"""

CHROME_MAJOR: str = "140"

USER_AGENT: str = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    f"(KHTML, like Gecko) Chrome/{CHROME_MAJOR}.0.0.0 Safari/537.36"
)

# Instagram's public web app id. Unchanged for years, so it is safe to embed.
IG_APP_ID: str = "936619743392459"

# Current value sent by the Instagram web app.
ASBD_ID: str = "198387"


# Persisted GraphQL query id for the profile timeline ("PolarisProfilePostsQuery"),
# as used by the Instagram web app for logged-in viewers. Instagram retires
# these occasionally (7898261790222653 stopped working in 2026); when it does,
# the request answers with an "execution error" payload instead of the timeline
# connection and the exception says so.
PROFILE_POSTS_DOC_ID: str = "34579740524958711"
PROFILE_POSTS_FRIENDLY_NAME: str = "PolarisProfilePostsQuery"
PROFILE_POSTS_CONNECTION: str = "xdt_api__v1__feed__user_timeline_graphql_connection"


def client_hints() -> dict[str, str]:
    """Return the ``sec-ch-ua*`` client hint headers matching ``USER_AGENT``."""

    brands = (
        f'"Chromium";v="{CHROME_MAJOR}", "Not=A?Brand";v="24", "Google Chrome";v="{CHROME_MAJOR}"'
    )
    full_brands = (
        f'"Chromium";v="{CHROME_MAJOR}.0.0.0", "Not=A?Brand";v="24.0.0.0", '
        f'"Google Chrome";v="{CHROME_MAJOR}.0.0.0"'
    )
    return {
        "sec-ch-ua": brands,
        "sec-ch-ua-full-version-list": full_brands,
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-model": '""',
        "sec-ch-ua-platform": '"macOS"',
        "sec-ch-ua-platform-version": '"14.0.0"',
    }


def api_headers(csrf_token: str, www_claim: str, referer: str) -> dict[str, str]:
    """Return the header set the Instagram web app sends to ``/api/v1/`` endpoints."""

    return {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "sec-ch-prefers-color-scheme": "dark",
        **client_hints(),
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "viewport-width": "1475",
        "x-asbd-id": ASBD_ID,
        "x-csrftoken": csrf_token,
        "x-ig-app-id": IG_APP_ID,
        "x-ig-www-claim": www_claim,
        "x-requested-with": "XMLHttpRequest",
        "Referer": referer,
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }


def csrf_token_from(session, fallback: str) -> str:
    """Return the csrftoken Instagram set on this session, preferring the
    instagram.com-scoped cookie over any placeholder set without a domain.

    ``RequestsCookieJar.get`` raises ``CookieConflictError`` once both exist,
    which happens after the first real Instagram response."""

    placeholder = None
    for cookie in session.cookies:
        if cookie.name != "csrftoken":
            continue
        if "instagram.com" in (cookie.domain or ""):
            return cookie.value
        placeholder = cookie.value
    return placeholder or fallback


def describe_response(response) -> str:
    """Short, loggable description of an unexpected Instagram response."""

    body = response.text[:200].replace("\n", " ")
    return f"HTTP {response.status_code} from {response.url}: {body!r}"
