#!/usr/bin/python
# coding: utf8

import argparse
import sys
import mapillary


def cli():
    '''
    Use from command line as: mapillary <command>

    You need to set the environment variables MAPILLARY_USERNAME,
    MAPILLARY_PERMISSION_HASH and MAPILLARY_SIGNATURE_HASH to your
    unique values.
    '''
    parser = argparse.ArgumentParser(description="Mapillary Python API.")
    parser.add_argument('command', type=str, nargs="*", help="Command")
    parser.add_argument('input', type=str, help='Input: File Path')
    parser.add_argument('-o', '--out', type=str, help='Output: File Path')
    parser.add_argument('-e', '--email', help="Login: Mapillary email")
    parser.add_argument('-u', '--username', help="Login: Mapillary username")
    parser.add_argument('-p', '--password', help="Login: Mapillary password")
    parser.add_argument('-g', '--gpx', type=str, help='GPX Track: File Path')
    parser.add_argument('-b', '--bearing', type=str,
                        help='GPX Offset: Image Bearing/Direction')
    parser.add_argument('-t', '--time', type=str,
                        help='GPX Offset: Time in Seconds')
    args = parser.parse_args()

    if 'upload' in args.command:
        if not args.input:
            print('[ERROR] Please include a <File Path>\n'
                  '$ mapillary upload "<File Path>"" -u "<Username>"')
            sys.exit()

        if not args.username:
            print('[ERROR] Please include a <Username>\n'
                  '$ mapillary upload "<File Path>"" -u "<Username>"')
            sys.exit()

        # Run core method
        mapillary.upload(
            args.input,
            username=args.username,
            email=args.email,
            password=args.password)

    if 'geotag' in args.command:
        if not args.input:
            print('[ERROR] Please include a <File Path>\n'
                  '$ mapillary geotag "<File Path>"" -g "<GPX File Path>"')
            sys.exit()
        if not args.gpx:
            print('[ERROR] Please include a <GPX File Path>\n'
                  '$ mapillary geotag "<File Path>"" -g "<GPX File Path>"')
            sys.exit()

        # Optional Parameters
        kwargs = {}
        if args.bearing:
            try:
                kwargs['bearing'] = int(args.bearing)
            except ValueError:
                print('[ERROR] Image Bearing/Direction must be an <Integer>\n'
                      '$ mapillary geotag "<File Path>"" -g "<GPX File Path>" -b 90')
                sys.exit()
        if args.time:
            try:
                kwargs['time'] = int(args.time)
            except ValueError:
                print('[ERROR] Time Offset must be an <Integer>:Seconds \n'
                      '$ mapillary geotag "<File Path>"" -g "<GPX File Path>" -t 2')
                sys.exit()

        # Run core method
        mapillary.geotag(
            args.input,
            args.gpx,
            **kwargs)

    elif not args.command:
        print('\n'
              '        Mapillary API            \n'
              '=================================\n'
              'Please include a command <upload, geotag>\n'
              'Examples:\n'
              '$ mapillary upload "<File Path>" -u "<Username>" \\\n'
              '> -e "<your@email.com>" -p "<Password>"\n'
              '--------------END----------------\n')
        sys.exit()
