# Migaku Player Converter

This program converts your video files so they become compatible with the Migaku Player (can be opened in the Migaku Browser Extension).

## Download
[Windows Download](https://github.com/migaku-official/migaku-player-converter/releases/download/v0.8.0-alpha/migaku-player-converter.exe)

[Mac Download](https://github.com/migaku-official/migaku-player-converter/releases/download/v0.8.0-alpha/migaku-player-converter-mac.dmg)

[Linux Download](https://github.com/migaku-official/migaku-player-converter/releases/download/v0.8.0-alpha/migaku-player-converter-linux)

## Instructions
* Download the program for your operating system
* Place the program into a folder with files you want to convert
* Execute the program by double clicking it

## Caveats
While the Migaku Player Converter tries to be as performant as possible, in some cases the conversion will still takes a long time.

In particular this will be the case with the HEVC video codec (also called h265).
The reason is that HEVC is not able to be played in the browser and the video has to be completely reencoded to h264 (h264 is compatible with the browser but takes more disk space).

If you want to circumvent this issue try to download only files that *do not* include `HEVC` or `h265` in the description or title (the default is h264).

## Further Info
If subtitle files in your target language are out of sync with your video, check out the sister project [Migaku Subtitle Syncer](https://github.com/migaku-official/migaku-subtitle-syncer/)!
