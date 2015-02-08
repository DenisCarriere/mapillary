#!/usr/bin/python
# coding: utf8

from .upload import manual_upload
from .upload import get_hashes
from .geotag import Geotag


def upload(path, **kwargs):
    manual_upload(path, **kwargs)


def geotag(path, path_gpx, **kwargs):
    """GeoTag

    :param ``path``: Image File Path
    :param ``gpx``: GPX File Path
    :param ``bearing``: Bearing/Direction offset (default=0)
    :param ``time``: Time offset in Seconds (default=0)
    """
    return Geotag(path, path_gpx, **kwargs)


def hashes(email, password):
    return get_hashes(email, password)
