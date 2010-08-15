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

  Plugin.AddViewGroup('Category', viewMode='List', mediaType='items')
  Plugin.AddViewGroup('Details', viewMode='InfoList', mediaType='items')

  # Set the default MediaContainer attributes
  MediaContainer.title1    = 'FOX News'
  MediaContainer.viewGroup = 'Category'
  MediaContainer.art       = R(ART_DEFAULT)

  # Set the default cache time
  HTTP.SetCacheTime(CACHE_1HOUR)

###################################################################################################

def MainMenu():
  dir = MediaContainer()

  c = HTML.ElementFromURL(BASE_URL, errors='ignore').xpath('/html/body//div[@id="playlist"]/ul/li')
  for category in c:
    item = category.xpath('./a')
    if len(item) == 1:
      title = item[0].text.strip()
      id = re.search('playlist_id=([0-9]+)', item[0].get('href')).group(1)
      dir.Append(Function(DirectoryItem(Playlist, title=title, thumb=R(ICON_DEFAULT)), title=title, id=id))
    else:
      item = category.xpath('./span/a')
      if len(item) == 1:
        title = item[0].text.strip()
        dir.Append(Function(DirectoryItem(Category, title=title, thumb=R(ICON_DEFAULT)), title=title))

  return dir

###################################################################################################

def Category(sender, title):
  dir = MediaContainer(title2=title)

  c = HTML.ElementFromURL(BASE_URL, errors='ignore').xpath('/html/body//div[@id="playlist"]/ul/li/span/a[text()="' + title + '"]/../../ul/li/a')
  for category in c:
    title = category.text.strip()
    id = re.search('playlist_id=([0-9]+)', category.get('href')).group(1)
    dir.Append(Function(DirectoryItem(Playlist, title=title, thumb=R(ICON_DEFAULT)), title=title, id=id))

  return dir

###################################################################################################

def Playlist(sender, title, id):
  dir = MediaContainer(viewGroup='Details', title2=title)

  Log( RSS_FEED % id )
  i = XML.ElementFromURL(RSS_FEED % id, errors='ignore').xpath('/rss/channel/item')

  for item in i:
    title       = item.xpath('./title')[0].text.strip()
    title       = re.sub('&amp;', '&', title)
    description = item.xpath('.//media:description', namespaces=RSS_NS)[0].text
    duration    = item.xpath('./media:content/mvn:duration', namespaces=RSS_NS)[0].text
    duration    = int(duration) * 1000
    date        = item.xpath('./media:content/mvn:airDate', namespaces=RSS_NS)[0].text
    date        = Datetime.ParseDate(date).strftime('%a %b %d, %Y')
    thumb       = item.xpath('./media:content/media:thumbnail', namespaces=RSS_NS)[0].text
    url         = item.xpath('./media:content', namespaces=RSS_NS)[0].get('url')

    dir.Append(VideoItem(url, title=title, subtitle=date, duration=duration, summary=description, thumb=thumb))

  return dir
