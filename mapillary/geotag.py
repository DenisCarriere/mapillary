#!/usr/bin/python
# coding: utf8

from upload import create_file_list
import exifread
import math
import pexif
import re
import datetime
import time
from bs4 import BeautifulSoup
from geojson import FeatureCollection, Feature, LineString, Point
import json


def utc_to_localtime(utc_time):
    utc_offset_timedelta = datetime.datetime.utcnow() - datetime.datetime.now()
    return utc_time - utc_offset_timedelta


def get_lat_lng_time(path):
    '''
    Read location and time stamps from a track in a GPX file.

    Returns a list of tuples (time, lat, lng).

    GPX stores time in UTC, assume your camera used the local
    timezone and convert accordingly.
    '''
    soup = BeautifulSoup(open(path))
    points = []
    last = None
    for item in soup.find_all('trkpt'):
        t = utc_to_localtime(convert_time(item.time.text))
        t = time.mktime(t.timetuple())
        if last:
            # Ignore bad GPX data
            time_offset = abs(last - t)
            if time_offset < 15:
                points.append([t, float(item['lat']), float(item['lon']), float(item.ele.text)])
        last = t
    points.sort()
    return points


def convert_time(t):
    """Converts String into Datetime object"""

    expression = r'\d+'
    pattern = re.compile(expression)
    match = pattern.findall(t)
    if match:
        year, month, day, hour, minute, second = match[0:6]
        t = datetime.datetime(int(year),
                              int(month),
                              int(day),
                              int(hour),
                              int(minute),
                              int(round(float(second), 0)))
        return t


def get_datetime_tag(tags):
    for tag in [
        'Image DateTime',
        'EXIF DateTimeOriginal',
        'EXIF DateTimeDigitized'
    ]:
        time = str(tags.get(tag))
        if time:
            return convert_time(time)


def compute_bearing(start_lat, start_lng, end_lat, end_lng):
    '''
    Get the compass bearing from start to end.

    Formula from
    http://www.movable-type.co.uk/scripts/latlong.html
    '''
    # make sure everything is in radians
    start_lat = math.radians(start_lat)
    start_lng = math.radians(start_lng)
    end_lat = math.radians(end_lat)
    end_lng = math.radians(end_lng)

    dLng = end_lng - start_lng

    dPhi = math.log(
        math.tan(end_lat / 2.0 + math.pi / 4.0) /
        math.tan(start_lat / 2.0 + math.pi / 4.0)
    )
    if abs(dLng) > math.pi:
        if dLng > 0.0:
            dLng = -(2.0 * math.pi - dLng)
        else:
            dLng = (2.0 * math.pi + dLng)

    y = math.sin(dLng)*math.cos(end_lat)
    x = math.cos(start_lat) * math.sin(end_lat) - math.sin(start_lat) *\
        math.cos(end_lat) * math.cos(dLng)
    bearing = (math.degrees(math.atan2(y, x)) + 360.0) % 360.0

    return bearing


def interpolate_lat_lng(points, timestamp):
    '''
    Return interpolated lat, lng and compass bearing for time t.

    Points is a list of tuples (time, lat, lng, elevation).
    '''

    t = time.mktime(timestamp.timetuple())

    # find the enclosing points in sorted list
    if (t < points[0][0]) or (t >= points[-1][0]):
        return None, None, None, None
        raise ValueError("Time t not in scope of gpx file.")

    for i, point in enumerate(points):
        if t < point[0]:
            if i > 0:
                before = points[i-1]
            else:
                before = points[i]
            after = points[i]
            break

    # time diff
    dt_before = t - before[0]
    dt_after = after[0] - t

    # simple linear interpolation
    lat = (before[1] * dt_after + after[1]*dt_before) / (dt_before + dt_after)
    lng = (before[2] * dt_after + after[2]*dt_before) / (dt_before + dt_after)

    bearing = compute_bearing(before[1], before[2], after[1], after[2])

    if before[3] is not None:
        elevation = (before[3] * dt_after + after[3] * dt_before) /\
                    (dt_before + dt_after)
    else:
        elevation = None

    return lat, lng, bearing, elevation


def add_exif_using_timestamp(filename, points, offset_bearing=0, offset_time=0):
    '''
    Find lat, lng and bearing of filename and write to EXIF.
    '''
    # Read EXIF tags from file
    with open(filename, 'rb') as f:
        try:
            tags = exifread.process_file(f)
        except:
            print filename

    # Get timestamp and offset time with seconds
    timestamp = get_datetime_tag(tags) \
        - datetime.timedelta(seconds=offset_time)

    # Get Coordinates from timestamp & GPX
    lat, lng, bearing, altitude = interpolate_lat_lng(points, timestamp)

    if bool(lat and lng):
        # Add Geo EXIF to file
        img = pexif.JpegFile.fromFile(filename)

        # Offset Bearing
        bearing = (bearing + offset_bearing) % 360

        # Define Lat & Lng
        img.set_geo(lat, lng)
        img.set_altitude(altitude)
        img.set_direction(bearing)
        img.set_bearing(bearing)

        # Overwrite Save File
        img.writeFile(filename)
        print('Saving file: %s' % filename)
    else:
        print('ERROR: %s' % filename)


def save_geojson_gpx(path_gpx):
    # Parse all GPX points
    gpx = get_lat_lng_time(path_gpx)

    # Save as GeoJSON
    geom_line = []
    geom_point = []

    for item in gpx:
        geom_line.append((item[2], item[1]))
        properties = {'timestamp': item[0], 'lat': item[1], 'lng': item[2]}
        geom_point.append(Feature(geometry=Point((item[2], item[1])), properties=properties))

    # LineString
    with open("/home/denis/GIS/Mapillary/GPX_Line.geojson", 'w') as f:
        fc = Feature(geometry=LineString(geom_line))
        f.write(json.dumps(fc, indent=2))

    with open("/home/denis/GIS/Mapillary/GPX_Point.geojson", 'w') as f:
        fc = FeatureCollection(geom_point)
        f.write(json.dumps(fc, indent=2))

class Geotag(object):
    def __init__(self, path, path_gpx, **kwargs):
        # Optional Parameters
        offset_time = kwargs.get('time', 0)
        offset_bearing = kwargs.get('bearing', 0)

        # Parse all GPX points
        gpx = get_lat_lng_time(path_gpx)

        # Add EXIF to each indiviual file
        for filepath in create_file_list(path):
            add_exif_using_timestamp(filepath, gpx, offset_bearing, offset_time)


if __name__ == '__main__':
    path = '/home/denis/GIS/Mapillary/Orleans_2/'
    path_gpx = '/home/denis/GIS/Mapillary/Orleans_2.gpx'
    #save_geojson_gpx(path_gpx)
    gpx = get_lat_lng_time(path_gpx)
    Geotag(path, path_gpx)
