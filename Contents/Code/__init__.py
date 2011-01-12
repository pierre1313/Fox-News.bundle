import re

###################################################################################################

PLUGIN_PREFIX  = '/video/foxnews'
BASE_URL       = 'http://video.foxnews.com'
RSS_FEED       = '%s/v/feed/playlist/%%s.xml' % BASE_URL
RSS_NS         = {'mvn':'http://maven.net/mcr/4.1', 'media':'http://search.yahoo.com/mrss/'}

# Default artwork and icon(s)
ART_DEFAULT    = 'art-default.png'
ICON_DEFAULT   = 'icon-default.png'

###################################################################################################

def Start():
  Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, 'FOX News', ICON_DEFAULT, ART_DEFAULT)

  Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
  Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')

  # Set the default MediaContainer attributes
  MediaContainer.title1    = 'FOX News'
  MediaContainer.viewGroup = 'List'
  MediaContainer.art       = R(ART_DEFAULT)

  DirectoryItem.thumb      = R(ICON_DEFAULT)

  # Set the default cache time
  HTTP.CacheTime = 1800

###################################################################################################

def MainMenu():
  dir = MediaContainer()

  i = 0
  frontpage = HTML.ElementFromURL(BASE_URL, errors='ignore')
  for category in frontpage.xpath('//span[@class="arrow-up"]'):
    title = category.xpath('./a')[0].text.strip()
    i = i + 1
    dir.Append(Function(DirectoryItem(Category, title=title), i=i))

  return dir

###################################################################################################

def Category(sender, i):
  Log(i)
  dir = MediaContainer(title2=sender.itemTitle)

  frontpage = HTML.ElementFromURL(BASE_URL, errors='ignore')
  for sub in frontpage.xpath('//div[@id="playlist-2"]/ul[' + str(i) + ']/li'):
    title = sub.xpath('./a')[0].text.strip()
    playlist_id = sub.xpath('./a')[0].get('href').split('=')[1]
    dir.Append(Function(DirectoryItem(Playlist, title=title), playlist_id=playlist_id))

  return dir

###################################################################################################

def Playlist(sender, playlist_id):
  dir = MediaContainer(viewGroup='InfoList', title2=sender.itemTitle)

  Log( RSS_FEED % playlist_id )
  playlist = XML.ElementFromURL(RSS_FEED % (playlist_id), errors='ignore').xpath('/rss/channel/item')

  for item in playlist:
    title       = item.xpath('./title')[0].text.strip()
    title       = re.sub('&amp;', '&', title)
    description = item.xpath('.//media:description', namespaces=RSS_NS)[0].text
    duration    = item.xpath('./media:content/mvn:duration', namespaces=RSS_NS)[0].text
    duration    = int(duration) * 1000
    date        = item.xpath('./media:content/mvn:airDate', namespaces=RSS_NS)[0].text
    date        = Datetime.ParseDate(date).strftime('%a %b %d, %Y')
    thumb_url   = item.xpath('./media:content/media:thumbnail', namespaces=RSS_NS)[0].text
    url         = item.xpath('./media:content', namespaces=RSS_NS)[0].get('url')

    dir.Append(VideoItem(url, title=title, subtitle=date, duration=duration, summary=description, thumb=Function(Thumb, url=thumb_url)))

  return dir

###################################################################################################

def Thumb(url):
  try:
    data = HTTP.Request(url, cacheTime=CACHE_1MONTH).content
    return DataObject(data, 'image/jpeg')
  except:
    return Redirect(R(ICON_DEFAULT))
