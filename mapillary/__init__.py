#!/usr/bin/python
# coding: utf8

"""
Mapillary: Useful tools
=======================
Making the Upload with Authentication process easier with only Email & Password authentication.

Install
-------
$ python setup.py install

How to use
----------
$ mapillary upload <File Path> -e <your@email.com> -p <Password> -u <Username>

Using Environment Variables
---------------------------
Connect the the following URL for Hashes
http://api.mapillary.com/v1/u/uploadhashes

**Exporting env Variables**

$ export $MAPILLARY_PERMISSION_HASH=<permission_hash>
$ export $MAPILLARY_SIGNATURE_HASH=<signature_hash>
"""

__title__ = 'mapillary'
__author__ = 'Denis Carriere'
__author_email__ = 'carriere.denis@gmail.com'
__version__ = '0.0.2'
__license__ = 'MIT'


from .api import upload, geotag, hashes
