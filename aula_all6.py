import os
import os.path
import re
import requests
import browser_cookie3
import piexif
import argparse
import random
from rich.progress import track
from rich.console import Console
from datetime import datetime
from aulaclient import AulaClient

class AlbumToDownload:
    def __init__(self, name, type, creationDate, pictures):
        self.name = name
        self.type = type
        self.creationDate = creationDate
        self.pictures = pictures

    def __str__(self):
        return f"Type: {self.type}, CreationDate: {self.creationDate}, Pictures: {len(self.pictures)}, Name: {self.name}"

def parseDate(dateString):
    return datetime.strptime(dateString.split('T')[0], '%Y-%m-%d').date()

def parseDateTime(dateString):
    return datetime.strptime(dateString, '%Y-%m-%dT%H:%M:%S%z')

def cleanTitle(title):
    return title.strip().replace('/', '_').replace(':', '_').replace('?', '_')

def pictureHasTags(picture, tags):
    pictureTags = list(map(lambda t: t['name'], picture['tags']))
    for tag in tags:
        if tag in pictureTags:
            return True
    return False

def getAlbumsToDownloadFromGallery(institutionProfileIds):
    print('Get Albums...')
    additionalParams = { 'limit': 1000 }
    albumsToDownload = []
    albums = client.getAlbums(institutionProfileIds, additionalParams)
    albumsWithId = list(filter(lambda a: a['id'] is not None, albums))
    for album in albumsWithId:
        creationDate = parseDate(album['creationDate'])
        isAlbumCreatedAfterCutoffDate = creationDate >= cutoffDate
        if not isAlbumCreatedAfterCutoffDate:
            continue
        pictures = client.getPictures(institutionProfileIds, album['id'], additionalParams)
        if pictures:
            name = cleanTitle(album['title'])
            print(creationDate, " ", name)
            pa = AlbumToDownload(name, "Album", creationDate, pictures)
            albumsToDownload.append(pa)
    return albumsToDownload


def printArguments(cutoffDate, outputDirectory):
    paramStyle="cyan"
    console.print("Parameters:", style=paramStyle)
    console.print(f"  cutoffDate: {cutoffDate.strftime('%Y-%m-%d')}", style=paramStyle)
    console.print(f"  outputDirectory: {outputDirectory}", style=paramStyle)
    console.print()

def tryAppendAulaCookies(aulaCookies, browserName, cookieCallback):
    try:
        cookies = cookieCallback()
        aulaCookies.append(cookies)
        console.print(f"{browserName} cookies: [green]found[/]")
    except browser_cookie3.BrowserCookieError as error:
        console.print(f"{browserName} cookies: [yellow]not found[/]")

def getAulaCookies():
    aulaCookies = []
    tryAppendAulaCookies(aulaCookies, 'Chrome', lambda: browser_cookie3.chrome(domain_name='aula.dk'))
    tryAppendAulaCookies(aulaCookies, 'Chromium', lambda: browser_cookie3.chromium(domain_name='aula.dk'))
    tryAppendAulaCookies(aulaCookies, 'Opera', lambda: browser_cookie3.opera(domain_name='aula.dk'))
    tryAppendAulaCookies(aulaCookies, 'Opera GX', lambda: browser_cookie3.opera_gx(domain_name='aula.dk'))
    tryAppendAulaCookies(aulaCookies, 'Brave', lambda: browser_cookie3.brave(domain_name='aula.dk'))
    tryAppendAulaCookies(aulaCookies, 'Edge', lambda: browser_cookie3.edge(domain_name='aula.dk'))
    tryAppendAulaCookies(aulaCookies, 'Vivaldi', lambda: browser_cookie3.vivaldi(domain_name='aula.dk'))
    tryAppendAulaCookies(aulaCookies, 'Firefox', lambda: browser_cookie3.firefox(domain_name='aula.dk'))
    tryAppendAulaCookies(aulaCookies, 'Safari', lambda: browser_cookie3.safari(domain_name='aula.dk'))
    return aulaCookies

console = Console()

# Parse arguments
parser = argparse.ArgumentParser(description='Download images from aula.dk.')
parser.add_argument('-d', required=False, help='Only download images that have been posted on or after this date (format: "YYYY-MM-DD")')
parser.add_argument('-o', required=True, default='output', help='Download images in this folder')
args = parser.parse_args()

try: 
    cutoffDate = datetime.fromisoformat(args.d).date()
except Exception as error:
    cutoffDate = datetime.fromisoformat("2000-01-01").date()
outputDirectory = args.o
printArguments(cutoffDate, outputDirectory)

# Init Aula client
aulaCookies = getAulaCookies()
client = AulaClient(aulaCookies)

try:
    profiles = client.getProfiles()
except Exception as error:
    console.print(error, style="red")
    console.print("Could not get profiles, exiting.", style="red")
    exit()

institutionProfileIds = list(map(lambda p: p['id'], profiles[0]['institutionProfiles']))
childrenIds = list(map(lambda p: p['id'], profiles[0]['children']))

albumsToDownload = []
albumsToDownload = getAlbumsToDownloadFromGallery(institutionProfileIds)

print('Download Pictures...')
for album in track(albumsToDownload, "Albums to download..."):
    if album.creationDate < cutoffDate:
        continue
    print('>', album, end = ' ', flush = True)
    for picture in album.pictures:
            
            albumProperName = re.sub(r'[\\/*?:"<>| ,.]',"_",album.name)
            albumDirectoryName = album.creationDate.strftime('%Y-%m-%d') + '_' + albumProperName
            albumDirectoryPath = os.path.join(outputDirectory, albumDirectoryName)


            imageDirectoryPath = albumDirectoryPath
            
            file = picture['file']
            imageCreationTime = datetime.strptime(file['created'], '%Y-%m-%dT%H:%M:%S%z')
            imageResponse = requests.get(file['url'])

            imagename = imageCreationTime.strftime('%Y-%m-%d') + "_" + albumProperName + "_" + file['name']
            os.makedirs(imageDirectoryPath, exist_ok=True)
            imagePath = os.path.join(imageDirectoryPath, imagename)
# Rename file if file exists - happens VERY rarely with certain video files named the same (and from the same date... - this is a qucik&dirty fix and can be improved)
            if os.path.exists(imagePath):
                imagename = imageCreationTime.strftime('%Y-%m-%d') + "_" + albumProperName + "_" + str(random.randint(1,9999999)) + "_" + file['name']
                imagePath = os.path.join(imageDirectoryPath, imagename)
            open(imagePath, "wb").write(imageResponse.content)






