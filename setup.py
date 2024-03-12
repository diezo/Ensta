from distutils.core import setup
from pathlib import Path

version = "5.2.9"
long_description = (Path(__file__).parent / "README.md").read_text(encoding="utf-8").replace(
    "[!IMPORTANT]",
    "**Important:**"
)

setup(
    name="ensta",
    python_requires=">=3.10",
    packages=[
        "ensta",
        "ensta.lib",
        "ensta.containers",
        "ensta.structures",
        "ensta.parser"
    ],
    version=version,
    license="MIT",
    description="🔥 Fastest & Simplest Python Package For Instagram Automation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Deepak Soni",
    author_email="sonniiii@outlook.com",
    url="https://github.com/diezo/ensta",
    download_url=f"https://github.com/diezo/ensta/archive/refs/tags/v{version}.tar.gz",
    keywords=[
        "instagram-client",
        "instagram",
        "api-wrapper",
        "instagram-scraper",
        "instagram-api",
        "instagram-sdk",
        "instagram-photos",
        "instagram-api-python",
        "instabot",
        "instagram-stories",
        "instagram-bot",
        "instapy",
        "instagram-downloader",
        "instagram-account",
        "instagram-crawler",
        "instagram-private-api",
        "igtv",
        "instagram-automation",
        "reels",
        "instagram-feed"
    ],
    install_requires=[
        "requests",
        "moviepy",
        "pillow",
        "cryptography",
        "pyotp",
        "ntplib",
        "pyquery"
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10"
    ]
)
