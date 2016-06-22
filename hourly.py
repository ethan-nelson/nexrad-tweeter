import pyart
import matplotlib.pyplot as plt
import glob
import time
import requests
import StringIO
import xml.etree.cElementTree as ElementTree
import tempfile
import os
import imageio
import twitter
import datetime
import os

twitter_keys = ['twitter_consumer_key', 'twitter_consumer_secret', 'twitter_access_token_key', 'twitter_access_token_secret']
keys = {}


for key in twitter_keys:
    try:
        keys[key] = os.environ[key]
    except:
        raise Exception('Environment key %s not found' % (key,))


def get_filenames(year, month, day, hour, site):
    url = "http://noaa-nexrad-level2.s3.amazonaws.com/?prefix=%s/%s/%s/%s/%s%s%s%s_%s" % \
            (year, month.zfill(2), day.zfill(2), site, site, year, month.zfill(2), day.zfill(2), hour.zfill(2))
    content = requests.get(url)
    content = StringIO.StringIO(content.content)

    return content


def parse_xml(content):
    e = ElementTree.parse(xml)
    r = e.getroot()

    filenames = []
    for child in r:
        if child.tag[-8:] == 'Contents':
            for c in child:
                if c.tag[-3:] == 'Key':
                    filenames.append(c.text)

    return filenames


def get_files(filelist):
    url_base = 'https://noaa-nexrad-level2.s3.amazonaws.com/'
    files = []
    for filename in filelist:
        content = requests.get(url_base + filename)
        c = content.content
        name = os.path.basename(filename)
        f = open(name,'w')
        f.write(c)
        f.close()
        files.append(name)

    return files


now = datetime.datetime.utcnow() + datetime.timedelta(hours=-1)
print now.year, now.month, now.day, now.hour
xml = get_filenames(str(now.year), str(now.month), str(now.day), str(now.hour), 'KMKX') 

filenames = parse_xml(xml)
if len(filenames) == 0:
    raise Exception('No files found.')

files = get_files(filenames)

image_filenames = []
for a_file in files:
    data = pyart.io.read_nexrad_archive(a_file)

    display = pyart.graph.RadarMapDisplay(data)
    fig = plt.figure(figsize=(6,6))

    ax = fig.add_subplot(111, frameon=False)
    display.plot_ppi_map('reflectivity', 0, title_flag=False, colorbar_flag=False, vmin=-30, vmax=75,  ax=ax, resolution='i', projection='aea', height=475000, width=475000)
    plt.axis('off')
    fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
    plt.annotate(a_file[13:-4]+'Z', xy=(0.98,0.04), xycoords='figure fraction', ha='right', va='center', fontsize=14)
    name = a_file[:-4]+'.png'
    plt.savefig(name)
    plt.close()
    image_filenames.append(name)


images = []
for filename in image_filenames:
    images.append(imageio.imread(filename))
imageio.mimsave('latest.gif', images, fps=2)


def tweet():
    api = twitter.Api(consumer_key=keys['twitter_consumer_key'],
        consumer_secret=keys['twitter_consumer_secret'],
        access_token_key=keys['twitter_access_token_key'],
        access_token_secret=keys['twitter_access_token_secret'])
    api.PostUpdate('Latest hourly radar loop', media='latest.gif')

tweet()
