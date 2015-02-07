# Mapillary: Python API

A big thanks to the guys at [@Mapillary] for publishing many great [Python tools for Mapillary].

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
$ mapillary upload "<File Path>" -u "<Username>" -e "<your@email.com>" -p "<Password>"
```

Using environment variables you can send your Mapillary credentials safely.

1. Connect the the following URL for to retrieve the **Hashes**.

 http://api.mapillary.com/v1/u/uploadhashes

2. Export env variables `MAPILLARY_PERMISSION_HASH` & `MAPILLARY_SIGNATURE_HASH`, you can edit `~/.bashrc` to store them to your terminal.

3. Use the Mapillary `upload` command with your `Username`.

```bash
$ export $MAPILLARY_PERMISSION_HASH=<permission_hash>
$ export $MAPILLARY_SIGNATURE_HASH=<signature_hash>
$ mapillary upload "<File Path>" -u "<Username>"
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

### Command Line Interface

```bash
$ mapillary -h
```

|    Parameter       |     Description     |
|:-------------------|:--------------------|
| `command`          | Mapillary API       |
| `-i`, `--input`    | Input: File Path    |
| `-o`, `--out`      | Output: File Path   |
| `-e`, `--email`    | Mapillary: email    |
| `-u`, `--username` | Mapillary: username |
| `-p`, `--password` | Mapillary: password |
| `-h`, `--help`     | Help File           |

[Python tools for Mapillary]: https://github.com/mapillary/mapillary_tools/tree/master/python
[@Mapillary]: https://twitter.com/mapillary