#!/usr/bin/python
# coding: utf8

from .upload import manual_upload


def upload(path, **kwargs):
    manual_upload(path, **kwargs)
