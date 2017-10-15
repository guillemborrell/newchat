#!/usr/bin/env python

from setuptools import setup

setup(name="newchat",
      version="0.1",
      description="A simple chat that uses websockets",
      author="Guillem Borrell",
      author_email="guillemborrell@gmail.com",
      packages=["newchat"],
      include_package_data=True,
      install_requires=["tornado", "sqlalchemy"],
      entry_points={
          'console_scripts': ['newchat=newchat.server:main']
      }
)
