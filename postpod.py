#!/usr/bin/python3
import sys
import os
import datetime
from getpass import getpass

import pysftp
import yaml
from pydub import AudioSegment
from pydub.exceptions import PydubException
from pysftp import ConnectionException

"""
Set the base directory (used for importing and exporting of files) and load the default values.
These can be easily changed in the files settings.yml and credentials.yml. 
"""

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
defaults = yaml.safe_load(open(os.path.join(BASE_DIR, 'settings.yml')))
credentials = yaml.safe_load(open(os.path.join(BASE_DIR, 'credentials.yml')))


def convert(infile):
    """
    Takes the path to a file to be converted and tagged.
    It assumes infile was passed to the program either via CLI parameters or via an interactive prompt.
    Conversion and tagging is done using pydub (which uses ffmpeg)
    :param infile:
    :return:
    """
    while not infile:
        infile = input("Enter filename to be converted. Must be a full system path.\n")
    if os.path.exists(infile):
        """
        Specify input and output format for the file and create a new AudioSegment using pydub.
        """
        in_format = defaults['in_format']
        out_format = defaults['out_format']
        bitrate = defaults['bitrate']
        try:
            audio = AudioSegment.from_file(infile, in_format)
        except PydubException as e:
            print("Couldn't import file: ", e)
            exit()

        outfile = input("What should the file be exported as?" + "\n" +
                        "(Note that the output format is set to " + out_format + ")\n")

        """
        Specify the ID3 tags that shall be used for the exported audio file.
        """
        id3_title = input("Please enter the episode title.\n")  # this is never set by default

        if defaults['album']:
            print("Default album title is", defaults['album'])
            album_input = input("Press Enter to use the default or enter another name:\n")
            id3_album = album_input if album_input else defaults['album']  # I feel dirty.
        else:
            id3_album = input("Please enter the album title.\n")

        if defaults['artist']:
            print("Default artist is", defaults['artist'])
            artist_input = input("Press Enter to use the default or enter another name:\n")
            id3_artist = artist_input if artist_input else defaults['artist']
        else:
            id3_artist = input("Please enter the album artist.\n")

        if defaults['genre']:
            print("Default genre is", defaults['genre'])
            genre_input = input("Press Enter to use the default or enter another name:\n")
            id3_genre = genre_input if genre_input else defaults['genre']
        else:
            id3_genre = input("Please enter the genre.\n")

        id3_cover = (os.path.join(BASE_DIR, defaults['cover']))
        if os.path.exists(id3_cover):
            print("Default cover file found.")
        else:
            print("No cover file specified.")
            id3_cover = ''

        # get current year
        id3_year = datetime.date.year

        # create the export directory if it doesn't exist
        if not os.path.exists(os.path.join(BASE_DIR, 'export')):
            os.makedirs(os.path.join(BASE_DIR, 'export'))

        # build string for file handle
        export_path = os.path.join(BASE_DIR, 'export/'+outfile)

        try:
            if id3_cover:
                file_handle = audio.export(export_path,
                                           format=out_format,
                                           bitrate=bitrate,
                                           tags={
                                               "title": id3_title,
                                               "artist": id3_artist,
                                               "album": id3_album,
                                               "genre": id3_genre,
                                               "year": id3_year,
                                                },
                                           cover=id3_cover
                                           )
            else:
                file_handle = audio.export(export_path,
                                           format=out_format,
                                           bitrate=bitrate,
                                           tags={
                                               "title": id3_title,
                                               "artist": id3_artist,
                                               "album": id3_album,
                                               "genre": id3_genre,
                                               "year": id3_year,
                                           })
            print("export successful!")
            return export_path

        except PydubException as e:
            print("Export failed: ", e)
    else:
        print("No file found at the specified path. Exiting.")
        exit()


def upload(file):
    """
    Uploads a given file to a directory via SFTP. The directory is read from the defaults file (if exists).
    Otherwise, the user is prompted for a directory.
    :return:
    """
    if not credentials['sftp_host']:
        sftp_host = input("Please enter the server hostname or IP:\n")
    else:
        sftp_host = credentials['sftp_host']

    if not credentials['sftp_port']:
        sftp_port = input("Please enter the port number (usually 22)\n")
    else:
        sftp_port = credentials['sftp_port']

    if not credentials['sftp_user']:
        sftp_user = input("SFTP username:\n")
    else:
        sftp_user = credentials['sftp_user']

    if not credentials['sftp_pass']:
        sftp_pass = getpass(prompt="SFTP password:\n")
    else:
        sftp_pass = credentials['sftp_pass']

    if defaults['upload_dir']:
        print("Upload directory is ", defaults['upload_dir'])
        dir_input = input("Press Enter to use the default or enter another path:\n")
        upload_dir = dir_input if dir_input else defaults['upload_dir']
    else:
        upload_dir = input("Please enter the destination directory on the server.\n")

    try:
        with pysftp.Connection(sftp_host, username=sftp_user, password=sftp_pass, port=sftp_port) as sftp:
            with sftp.cd(upload_dir):  # temporarily chdir to upload directory
                sftp.put(file)  # upload file to remote
        sftp.close()
        print("Successfully uploaded " + file)
    except ConnectionException as e:
        print("Upload failed: ", e)


def main():
    """
    Read CLI parameters and call the approriate functions.
    At least the input file must be given.
    :return:
    """
    # read CLI parameters
    if len(sys.argv) < 2:
        print("Not enough arguments given!")  #TODO use argparse for CLI parameters
    else:
        print("Input file:" + sys.argv[1])
        file = convert(sys.argv[1])
        upload(file)

    #TODO idea: pass "--no-<function>" to not perform this action, i.e. --no-upload


if __name__ == "__main__":
    # execute only if run as a script
    main()
