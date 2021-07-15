# chordTabsToPrintables

This program converts source (guitar) tablature to printable formats

First it separates the input into metadata and [sections]

Then it tries to separate section data into lyric lines and non-lyric lines

Lastly it exports it to the chosen format

Currently it supports exporting to .txt and .png

Converting to .txt is useful to clean up the source file or as an input for other programs. It can also add metadata which makes parsing these files much easier

Converting to .png will try to minimise the amount of pages required (to prevent page flips and with limits on how much whitespace we allow). Then it will increase the font size to fill these pages as much as possible.


When the program is started for the first time it will create a ``config.ini`` file which can edited to change the behaviour of the program. For example, you might want to force the program to limit the amount of pages, regardless of whitespace.


Run with 'python3 main.py'

By default it will try to parse all supported filetypes found in the current (sub)directory and convert them to A4 sized PNG files


Detailed config info: TBD

Example output:
![hc-12-1](https://user-images.githubusercontent.com/9502378/125768042-f21af6e0-2c83-4fb5-a546-19e5c97011fd.png)
![hc-12-2](https://user-images.githubusercontent.com/9502378/125768049-5b2373c0-8470-4049-b195-d1227ed68659.png)


