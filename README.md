# A Music-Downloader with CLI
This programm will first get the metadata of various songs from metadata provider like musicbrainz, and then search for download links on pages like bandcamp. Then it will download the song and edit the metadata according.

## Metadata

First the metadata has to be downloaded. The best api to do so is undeniably [Musicbrainz](musicbrainz.org/). This is a result of them being a website with a large Database spanning over all Genres.

### Musicbrainz

![Musicbrainz Data Scheme](https://wiki.musicbrainz.org/-/images/9/9e/pymb3-model-core.png)

To fetch from [Musicbrainz](musicbrainz.org/) we first have to know what to fetch. A good start is to get an input querry, which can be just put into the MB-Api. It then returns a list of possible artists, releases and recordings.

Then we can output them in the Terminal and ask for further input. Following can be inputed afterwards:

- `q` to quit
- `ok` to download
- `..` for previous options 
- `.` for current options
- `an integer` for this element

If the following chosen element is an artist, its discography + a couple tracks are outputed, if a release is chosen, the artists + tracklist + release is outputted, If a track is chosen its artists and releases are shown.

**TO DO**

- Schow always the whole tracklist of an release if it is chosen
- Show always the whole discography of an artist if it is chosen

Up to now it doesn't if the discography or tracklist is chosen.

### Metadata to fetch

I orient on which metadata to download on the keys in `mutagen.EasyID3` . Following I fatch and thus tag the MP3 with:
- title
- artist
- albumartist
- tracknumber
- albumsort can sort albums cronological
- titlesort is just set to the tracknumber to sort by track order to sort correctly
- isrc
- musicbrainz_artistid
- musicbrainz_albumid
- musicbrainz_albumartistid
- musicbrainz_albumstatus
- language
- musicbrainz_albumtype
- releasecountry
- barcode

#### albumsort/titlesort

Those Tags are for the musicplayer to not sort for Example the albums of a band alphabetically, but in another way. I set it just to chronological order

#### isrc

This is the **international standart release code**. With this a track can be identified 100% percicely all of the time, if it is known and the website has a search api for that. Obviously this will get important later.

---

## Download

Now that the metadata is downloaded and cached, download sources need to be sound, because one can't listen to metadata. Granted it would be amazing if that would be possible. 

### Musify

The quickest source to get download links from is to my knowledge [musify](https://musify.club/). Its a russian music downloading page, where many many songs are available to stream and to download. Due to me not wanting to stress the server to much, I abuse a handy feature nearly every page where you can search suff has. The autocomplete api for the search input. Those always are quite limited in the number of results it returns, but it is optimized to be quick. Thus with the http header `Connection` set to `keep-alive` the bottelneck defently is not at the speed of those requests.

For musify the endpoint is following: [https://musify.club/search/suggestions?term={title}](https://musify.club/search/suggestions?term=LornaShore) If the http headers are set correctly, then searching for example for "Lorna Shore" yields following result:

```json
[
    {
        "id":"Lorna Shore",
        "label":"Lorna Shore",
        "value":"Lorna Shore",
        "category":"Исполнители",
        "image":"https://39s.musify.club/img/68/9561484/25159224.jpg",
        "url":"/artist/lorna-shore-59611"       
    },
    {"id":"Immortal","label":"Lorna Shore - Immortal (2020)","value":"Immortal","category":"Релизы","image":"https://39s-a.musify.club/img/70/20335517/52174338.jpg","url":"/release/lorna-shore-immortal-2020-1241300"},
    {"id":"Immortal","label":"Lorna Shore - Immortal","value":"Immortal","category":"Треки","image":"","url":"/track/lorna-shore-immortal-12475071"}
]
```

This is a shortened example for the response the api gives. The results are very Limited, but it is also very efficient to parse. The steps I take are:

- call the api with the querry being the track name
- parse the json response to an object
- look at how different the title and artist are on every element from the category `Треки`, translated roughly to track or release.
- If they match get the download links and cache them.

### Youtube

Herte the **isrc** plays a huge role. You probaply know it, when you search on youtube for a song, and the music videos has a long intro or the first result is a live version. I don't want those in my music collection, only if the tracks are like this in the official release. Well how can you get around that?

Turns out if you search for the **isrc** on youtube the results contain the music, like it is on the official release and some japanese meme videos. The tracks I wan't just have the title of the released track, so one can just compare those two.

For searching, as well as for downloading I use the programm `youtube-dl`, which also has a programming interface for python.

There are two bottlenecks with this approach though:
1. `youtube-dl` is just slow. Actually it has to be, to not get blocked by youtube.
2. Ofthen musicbrainz just doesn't give the isrc for some songs.

**TODO**
- look at how the isrc id derived an try to generate it for the tracks without directly getting it from mb.
<<<<<<< HEAD
=======

**Progress**
- There is a great site whith a huge isrc database [https://isrc.soundexchange.com/](https://isrc.soundexchange.com/).


https://slavart.gamesdrive.net/
https://getmetal.club/
https://newalbumreleases.net/
http://download-soundtracks.com/
https://scnlog.me/
https://intmusic.net/
https://www.pluspremieres.ws/
https://music4newgen.org/
https://takemetal.org/
https://coreradio.ru/
https://alterportal.net/
https://vk.com/mdcore
https://vk.com/mdrock
https://sophiesfloorboard.blogspot.com/
https://funkysouls.org/
https://www.deadpulpit.com/
https://vk.com/filter_rock
https://en.metal-tracker.com/
https://thelastdisaster.org/
https://vk.com/phc
https://free-mp3-download.net/ requires recaptcha  
https://vk.com/filter_rock
https://t.me/ffilternews telegram?
https://justanothermusic.site/index.php requires login
>>>>>>> 63f30bffbae20ec3fc368a6093b28e56f0230318
