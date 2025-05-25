# aula-dk-pic-dl-givtrah
This script downloads images in albums, posts and messages from aula.dk.

## Description
This is a fork of https://github.com/elnigno/aula-dk-picture-download

This downloads all media you have access to on aula.dk (pictures or movies) in both galleries, posts and messages.

## At least the following changes have been made compared to the original:

Nixified & now uses uv as python package manager

*nix like options instead of the long windows-like options

Now stores all files as: outputdir/YYYY-MM-DD_gallery_folder/YYYY-MM-DD_filename.jpg 
(gallery_folder can also be message/post headings - note that this double dates the files as sometimes gallery albums are WAY older than the files in it)

The option to only download images with certain tags has not been implemented, an option to supply the session cookie manually has also not been implemented. Manual Api change not implemented.

Currently uses Aula API version 21 (easy to change). 

Tested on various versions of Linux including Nix OS

For it to work, you must first **log into aula.dk with your browser**.

Accepted parameters:

- `-d CUTOFFDATE` Only download images that have been posted on or after this date (format: "YYYY-MM-DD"). Beware: This uses the post/message/album creation date, NOT the picture upload date!
- `-o OUTPUTFOLDER` Download images in this folder (format: "folder", can be relative path)

## Usage Example
```bash
python .\aula_dk_dl-givtrah.py -d "2023-02-19" -o "output_folder"
```

## Known issues

The script might crash if you login with unilogin and attempt to download images from messages marked as sensitive. The issue does not occur when logging in with MitID, so use that if possible. 
