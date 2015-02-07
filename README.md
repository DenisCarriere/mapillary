# Mapillary: Python API

## Install

Latest version from **Github Repo**

```bash
$ git clone https://github.com/DenisCarriere/mapillary.git
$ cd mapillary_tools
$ python setup.py install
```

Stable version from **PyPi**

```bash
$ pip install mapillary
```

## How to use

### Manual Uploads

The Standard manual upload method requires your Mapillary credential

```bash
$ mapillary upload <File Path> -u <Username> -e <your@email.com> -p <Password>
```

Using environment variables you can send your Mapillary credentials safely.

1. Connect the the following URL for to retrieve the **Hashes**.

- http://api.mapillary.com/v1/u/uploadhashes

2. Export env variables or edit `~/.bashrc`

```bash
    $ export $MAPILLARY_PERMISSION_HASH=<permission_hash>
    $ export $MAPILLARY_SIGNATURE_HASH=<signature_hash>
    $ upload_with_authentication <File Path>
```

3. Use the Mapillary `upload` command with your `Username`.

```bash
$ mapillary upload <File Path> -u <Username>
```

### Successful Upload

A typical successful upload will look like the following:

```bash
$ mapillary upload -i GoPro -u deniscarriere

[SUCCESS] Mapillary connection established.
Uploading sequence 3e41e334-3a50-4e41-8206-dae2a4d24e5a.
Uploading: G0047731.JPG
Uploading: G0047747.JPG
 Uploading: G0047736.JPG
Uploading: G0047742.JPG
Success: G0047736.JPG
...
Success: G0047768.JPG
Success: G0047751.JPG
===
Finalizing upload will submit all successful uploads and ignore all failed.
If all files were marked as successful, everything is fine, just press 'y'.
Finalize upload? [y/n]: y
Upload a DONE file to tell the backend that the sequence is all uploaded and ready to submit.
Uploading: DONE
Success: DONE
Done uploading.
```