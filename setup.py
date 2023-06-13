from distutils.core import setup
from pathlib import Path

long_description = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")

setup(
    name="ensta",
    packages=["ensta", "ensta.lib", "ensta.containers"],
    version="1.8",
    license="MIT",
    description="🔥 Fastest & Simplest Python Package For Instagram Automation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Deepak Soni",
    author_email="lonelycube@proton.me",
    url="https://github.com/diezo/ensta",
    download_url="https://github.com/diezo/ensta/archive/refs/tags/v1.7.tar.gz",
    keywords=["instagram", "web", "private", "api", "scraper", "easy", "download", "upload"],
    install_requires=["requests"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10"
    ]
)
