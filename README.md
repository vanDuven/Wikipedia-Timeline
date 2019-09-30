# History Timeline through Wikipedia

Scripts to extract infoboxes and visualise dates from wikipedia.

Made using Python Standard Library (3.7.1). 

Currently support only the english wikipedia.

* [wikitojson.py](wikitojson.py):

Script with user input to extract wikipedia infoboxes and links from a wikipedia xml file to a json file. See [examples](/examples)

* [timeline.py](timeline.py):

Thinker script to extract dates (
by using finddate.<n></n>py) from the created json file 
(by using wikitojson.<n></n>py) and visualise it on a created timeline. Can also try to search dates in the text itself (from the xml file or url), which is useful if a page has no infobox.

* [finddate.py](finddate.py):

Returns a list with dates from a string and classifies whether the dates are periods 
(example: 1204–1261). Its build with wikipedia xml format in mind. (supports the [Hijri calendar](https://en.wikipedia.org/wiki/Islamic_calendar))

## Getting wikipedia xml data

The wikitojson.<n></n>py search through a single xml file.
The best way to get the data is through [torrenting a wikipedia dump file](https://meta.wikimedia.org/wiki/Data_dump_torrents#English_Wikipedia).

timeline.<n></n>py can scrap the en.wikipedia xml export from a single url.
It can also scrap every page which was linked in the given requested page, with a 1 second delay between every url to reduce wikipedia's server load.

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE)