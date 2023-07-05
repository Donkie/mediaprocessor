# Media Processor
A basic app that performs some basic media processing tasks recursively on a library of media files.

Things it does:
- Fixes subtitle/audio tracks without language set in MKV files

Example command line usage:
```bash
cd /path/to/media/library
docker run -i -v .:/data ghcr.io/donkie/mediaprocessor:latest /data
```
