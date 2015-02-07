#!/usr/bin/python
# coding: utf8

import os
import requests
import exifread
import urllib2
import urllib
import mimetypes
import socket
import threading
import uuid
import sys
from Queue import Queue
import time
import random
import string

'''
Script for uploading images taken with other cameras than
the Mapillary iOS or Android apps.

Intended use is for when you have used an action camera such as a GoPro
or Garmin VIRB, or any other camera where the location is included in the image EXIF.

The following EXIF tags are required:
-GPSLongitude
-GPSLatitude
-(GPSDateStamp and GPSTimeStamp) or DateTimeOriginal or DateTimeDigitized or DateTime
-Orientation

Before uploading put all images that belong together in a sequence, in a
specific folder, for example using 'time_split.py'. All images in a session
will be considered part of a single sequence.

NB: DO NOT USE THIS SCRIPT ON IMAGE FILES FROM THE MAPILLARY APPS,
USE UPLOAD.PY INSTEAD.

(assumes Python 2.x, for Python 3.x you need to change some module names)
'''

MAPILLARY_UPLOAD_URL = "https://d22zcsn13kp53w.cloudfront.net/"
PERMISSION_HASH = "eyJleHBpcmF0aW9uIjoiMjAyMC0wMS0wMVQwMDowMDowMFoiLCJj" +\
    "b25kaXRpb25zIjpbeyJidWNrZXQiOiJtYXBpbGxhcnkudXBsb2Fkcy5pbWFnZXMifS" +\
    "xbInN0YXJ0cy13aXRoIiwiJGtleSIsIiJdLHsiYWNsIjoicHJpdmF0ZSJ9LFsic3Rh" +\
    "cnRzLXdpdGgiLCIkQ29udGVudC1UeXBlIiwiIl0sWyJjb250ZW50LWxlbmd0aC1yYW" +\
    "5nZSIsMCwxMDQ4NTc2MF1dfQ=="
SIGNATURE_HASH = "foNqRicU/vySm8/qU82kGESiQhY="
BOUNDARY_CHARS = string.digits + string.ascii_letters
MAX_ATTEMPTS = 4
NUMBER_THREADS = 4
MOVE_FILES = False
UPLOAD_PARAMS = {
    "url": MAPILLARY_UPLOAD_URL,
    "permission": PERMISSION_HASH,
    "signature": SIGNATURE_HASH,
    "move_files": True
}


def create_dirs():
    if not os.path.exists("success"):
        os.mkdir("success")
    if not os.path.exists("failed"):
        os.mkdir("failed")


def verify_exif(filename):
    '''
    Check that image file has the required EXIF fields.

    Incompatible files will be ignored server side.
    '''
    # required tags in IFD name convention
    required_exif = [["GPS GPSLongitude", "EXIF GPS GPSLongitude"],
                     ["GPS GPSLatitude", "EXIF GPS GPSLatitude"],
                     ["EXIF DateTimeOriginal",
                      "EXIF DateTimeDigitized",
                      "Image DateTime",
                      "GPS GPSDate",
                      "EXIF GPS GPSDate"],
                     ["Image Orientation"]]
    description_tag = "Image ImageDescription"

    with open(filename, 'rb') as f:
        tags = exifread.process_file(f)

    # make sure no Mapillary tags
    if description_tag in tags:
        if "MAPSequenceUUID" in tags[description_tag].values:
            print("File contains Mapillary EXIF tags, use upload.py instead.")
            return False

    # make sure all required tags are there
    for rexif in required_exif:
        vflag = False
        for subrexif in rexif:
            if subrexif in tags:
                vflag = True
        if not vflag:
            print("Missing required EXIF tag: {0}".format(rexif[0]))
            return False

    return True


def retrieve_hashes(email, password):
    # Connect to Mapillary for Permission & Signature Hash
    payload = {'email': email, 'password': password}
    session = requests.Session()
    session.post('https://api.mapillary.com/v1/u/loginform', data=payload)
    r = session.get('http://api.mapillary.com/v1/u/uploadhashes')

    try:
        content = r.json()
        status = content.get('status')
    except:
        print '[ERROR] Please confirm your Mapillary email/password'
        print '--email:', email
        print '--password:', password
        exit()

    if status == 200:
        print '[SUCCESS] Mapillary connection established.'
        return content


class UploadThread(threading.Thread):
    def __init__(self, queue, params):
        threading.Thread.__init__(self)
        self.q = queue
        self.params = params

    def run(self):
        while True:
            # fetch file from the queue and upload
            filepath = self.q.get()
            if filepath is None:
                self.q.task_done()
                break
            else:
                upload_file(filepath, **self.params)
                self.q.task_done()


def encode_multipart(fields, files, boundary=None):
    """
    Encode dict of form fields and dict of files as multipart/form-data.
    Return tuple of (body_string, headers_dict). Each value in files is
    a dict with required keys 'filename' and 'content', and optional
    'mimetype' (if not specified, tries to guess mime type or uses
    'application/octet-stream').

    From MIT licensed recipe at
    http://code.activestate.com/recipes/578668-encode-multipart-form-data-for-uploading-files-via/
    """
    def escape_quote(s):
        return s.replace('"', '\\"')

    if boundary is None:
        boundary = ''.join(random.choice(BOUNDARY_CHARS) for i in range(30))
    lines = []

    for name, value in fields.items():
        lines.extend((
            '--{0}'.format(boundary),
            'Content-Disposition: form-data; name="{0}"'.format(escape_quote(name)),
            '',
            str(value),
        ))

    for name, value in files.items():
        filename = value['filename']
        if 'mimetype' in value:
            mimetype = value['mimetype']
        else:
            mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        lines.extend((
            '--{0}'.format(boundary),
            'Content-Disposition: form-data; name="{0}"; filename="{1}"'.format(
                    escape_quote(name), escape_quote(filename)),
            'Content-Type: {0}'.format(mimetype),
            '',
            value['content'],
        ))

    lines.extend((
        '--{0}--'.format(boundary),
        '',
    ))
    body = '\r\n'.join(lines)

    headers = {
        'Content-Type': 'multipart/form-data; boundary={0}'.format(boundary),
        'Content-Length': str(len(body)),
    }
    return (body, headers)


def upload_file(filepath, url, permission, signature, key=None, move_files=True):
        '''
        Upload file at filepath.

        Move to subfolders 'success'/'failed' on completion if move_files is True.
        '''

        filename = os.path.basename(filepath)
        print("Uploading: {0}".format(filename))

        # add S3 'path' if given
        if key is None:
            s3_key = filename
        else:
            s3_key = key + filename

        parameters = {
            "key": s3_key,
            "AWSAccessKeyId": "AKIAI2X3BJAT2W75HILA",
            "acl": "private",
            "policy": permission,
            "signature": signature,
            "Content-Type": "image/jpeg"
        }

        with open(filepath, "rb") as f:
            encoded_string = f.read()

        data, headers = encode_multipart(parameters, {'file': {'filename': filename, 'content': encoded_string}})

        for attempt in range(MAX_ATTEMPTS):
            try:
                request = urllib2.Request(url, data=data, headers=headers)
                response = urllib2.urlopen(request)

                if response.getcode() == 204:
                    if move_files:
                        os.rename(filepath, "success/"+filename)
                    print("Success: {0}".format(filename))
                else:
                    if move_files:
                        os.rename(filepath, "failed/"+filename)
                    print("Failed: {0}".format(filename))
                break  # attempts

            except urllib2.HTTPError as e:
                print("HTTP error: {0} on {1}".format(e, filename))
            except urllib2.URLError as e:
                print("URL error: {0} on {1}".format(e, filename))
            except socket.timeout as e:
                # Specific timeout handling for Python 2.7
                print("Timeout error: {0} (retrying)".format(filename))


def upload_done_file(params):
    print("Upload a DONE file to tell the backend that the sequence is all uploaded and ready to submit.")
    if not os.path.exists('DONE'):
        open("DONE", 'a').close()
    #upload
    upload_file("DONE", **params)
    #remove
    os.remove("DONE")


def manual_upload(path, username, signature, permission):
    MAPILLARY_UPLOAD_URL = "https://s3-eu-west-1.amazonaws.com/mapillary.uploads.manual.images"
    MAPILLARY_SIGNATURE_HASH = signature
    MAPILLARY_PERMISSION_HASH = permission
    MAPILLARY_USERNAME = username

    # if no success/failed folders, create them
    create_dirs()

    if path.lower().endswith(".jpg"):
        # single file
        file_list = [path]
    else:
        # folder(s)
        file_list = []
        for root, sub_folders, files in os.walk(path):
            file_list += [os.path.join(root, filename) for filename in files if filename.lower().endswith(".jpg")]

    # generate a sequence UUID
    sequence_id = uuid.uuid4()

    # S3 bucket
    s3_bucket = MAPILLARY_USERNAME + "/" + str(sequence_id) + "/"
    print("Uploading sequence {0}.".format(sequence_id))

    # set upload parameters
    params = {
        "url": MAPILLARY_UPLOAD_URL,
        "key": s3_bucket,
        "permission": MAPILLARY_PERMISSION_HASH,
        "signature": MAPILLARY_SIGNATURE_HASH,
        "move_files": MOVE_FILES
    }

    # create upload queue with all files
    q = Queue()
    for filepath in file_list:
        if verify_exif(filepath):
            q.put(filepath)
        else:
            print("Skipping: {0}".format(filepath))

    # create uploader threads with permission parameters
    uploaders = [UploadThread(q, params) for i in range(NUMBER_THREADS)]

    # start uploaders as daemon threads that can be stopped (ctrl-c)
    try:
        for uploader in uploaders:
            uploader.daemon = True
            uploader.start()

        for uploader in uploaders:
            uploaders[i].join(1)

        while q.unfinished_tasks:
            time.sleep(1)
        q.join()
    except (KeyboardInterrupt, SystemExit):
        print("\nBREAK: Stopping upload.")
        sys.exit()

    # ask user if finalize upload to check that everything went fine
    print("===\nFinalizing upload will submit all successful uploads and ignore all failed.\nIf all files were marked as successful, everything is fine, just press 'y'.")

    # ask 3 times if input is unclear
    for i in range(3):
        proceed = raw_input("Finalize upload? [y/n]: ")
        if proceed in ["y", "Y", "yes", "Yes"]:
            # upload an empty DONE file
            upload_done_file(params)
            print("Done uploading.")
            break
        elif proceed in ["n", "N", "no", "No"]:
            print("Aborted. No files were submitted. Try again if you had failures.")
            break
        else:
            if i == 2:
                print("Aborted. No files were submitted. Try again if you had failures.")
            else:
                print('Please answer y or n. Try again.')

if __name__ == '__main__':
    pass
