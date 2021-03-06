# pylint: skip-file
from setuptools import setup
from token_utils import __version__

with open("README.md", encoding="utf8") as f:
    README = f.read()

setup(
    name="token-utils",
    version=__version__,
    description="Small utility to work with Python tokens",
    long_description=README,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 1 - Planning",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    url="https://github.com/aroberge/token-utils",
    author="André Roberge",
    author_email="Andre.Roberge@gmail.com",
    py_modules=["token_utils"],
    python_requires=">=3.6",
)
