# Newchat

A simple websockets-based chat server written in about 200 lines of Python.

## Features

* Simple and hackable implementation.
* Automatic replacement of links with images and videos.
* Support for LaTeX formulas (between single $ marks).
* Multiple rooms.
* Efficient and fast.
* Depends only on Python 3, Tornado, SQLAlchemy and Matplotlib

## Cloudchat

Some years I wrote cloudchat (https://github.com/guillemborrell/cloudchat), a chat server based on Google's App Engine. Google decided to discontinue their Channel API, favoring their Firebase database. I was personally against relying on proprietary infrastructure to run a simple chat, so I coded a similar application with simpler requirements.
