#!/usr/bin/python
# coding: utf8

from .upload import manual_upload
from .upload import get_hashes


def upload(path, **kwargs):
    manual_upload(path, **kwargs)


def hashes(email, password):
    return get_hashes(email, password)
