#!/usr/bin/python
# coding: utf8

import argparse
import os
import sys
from .upload import retrieve_hashes
from .upload import manual_upload


def cli():
    '''
    Use from command line as: mapillary <command>

    You need to set the environment variables MAPILLARY_USERNAME,
    MAPILLARY_PERMISSION_HASH and MAPILLARY_SIGNATURE_HASH to your
    unique values.
    '''
    parser = argparse.ArgumentParser(description="Mapillary Python API.")
    parser.add_argument('command', type=str, nargs="*", help="Command")
    parser.add_argument('-i', '--input', type=str, help='Input: File Path')
    parser.add_argument('-o', '--out', type=str, help='Output: File Path')
    parser.add_argument('-e', '--email', help="Login: Mapillary email")
    parser.add_argument('-u', '--username', help="Login: Mapillary username")
    parser.add_argument('-p', '--password', help="Login: Mapillary password")
    args = parser.parse_args()

    if 'upload' in args.command:
        if not args.input:
            print('[ERROR] Please include a <File Path>')
            print('$ mapillary upload <File Path> -u <Username>')
            sys.exit()

        if not args.username:
            print('[ERROR] Please include a <Username>')
            print('$ mapillary upload <File Path> -u <Username>')
            sys.exit()

        # Verify Credentials
        if bool(args.email and args.password):
            content = retrieve_hashes(args.email, args.password)
            permission = content['permission_hash']
            signature = content['signature_hash']

        elif bool(('MAPILLARY_PERMISSION_HASH' in os.environ) and ('MAPILLARY_SIGNATURE_HASH' in os.environ)):
            permission = content['MAPILLARY_PERMISSION_HASH']
            signature = content['MAPILLARY_SIGNATURE_HASH']
        else:
            print('[ERROR] Please include both <Password> & <Email>')
            print('$ mapillary upload <File Path> -u <Username> -e <your@email.com> -p <Password>')
            sys.exit()

        manual_upload(args.input, username=args.username, signature=signature, permission=permission)
    else:
        print('')
        print('        Mapillary API            ')
        print('=================================')
        print('Please include a command (upload)')
        print('Examples:')
        print('$ mapillary upload <File Path> -u <Username> -e <your@email.com> -p <Password>')
        print('--------------END----------------')
        print('')
        sys.exit()
