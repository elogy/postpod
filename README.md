# PostPod

## About
PostPod is a small Python 3 script to automate the post-production process of podcast episodes. A wav file passed as a parameter is converted to mp3 (or any other desired format), tagged and can then be uploaded to an SFTP server. 
Conversion and tagging is done via [PyDub](https://github.com/jiaaro/pydub), uploading is done via [pysftp](https://bitbucket.org/dundeemt/pysftp)

## Installation
Install the necessary requirements via pip: 
```bash
cd <checkout directory>
pip install -r requirements.txt
```

Then, set your desired default audio settings and ID3 tags inside `settings.yml`:
```yml
# audio settings
in_format: wav
out_format: mp3
bitrate: 192k

# default ID3 tags
album: My Podcast
artist: Someone
genre: Podcast
url: http://url.example
cover: 'static/cover.png' # replace this file with your own cover

# Upload directory for FTP.
upload_dir: '/path/to/remote/directory'
```

If you with, put the credentials for SFTP inside the file `credentials.yml`. If you don't want to put your credentials as plain text into a file, just leave the values blank:

```yml
sftp_host: hostname.com
sftp_port: 22
sftp_user: 
sftp_pass: 

```
The script will then ask for your username and password. 

## Usage
Point the script to the wav file exported from your favourite DAW. Conversion, tagging and uploading is done semi-automatically 
(The script will assume the default settings, but asks if you want to apply or change these).

```bash
python3 postpod.py /path/to/wav-file.wav
```

The converted and tagged files are stored inside the `export` folder within the `postpod` directory. 
