#!/usr/bin/python

import json
import os
import shutil
import requests
from tqdm import tqdm
from pathlib import Path

download_dir = 'download'
image_dir = download_dir + "/jpg/"
bin_dir = download_dir + "/bin/"

def prepare_download(download_path:str):
    if os.path.isdir(download_path):
        print("Cleaning old download directory")
        shutil.rmtree(download_path)
    os.mkdir(download_path)
    os.mkdir(download_path + "/bin",)
    os.mkdir(download_path + "/jpg")


def downloadFile(uri, path):
    filename=uri.split('/')[-1]
    url = "https://" + uri
    jpg = open(filename, 'wb')
    down_headers = headers
    down_headers['Host'] = 'image.isu.pub'
    response = requests.request("GET",url, headers=headers)
    jpg.write(response.content)
    jpg.close()


url = "https://reader3.isu.pub/ducatiomaha/ducatiomaha_2015_diavel/reader3_4.json"

payload = ""
headers = {
    'Host': "reader3.isu.pub",
    'User-Agent': "Mozilla/5.0 (X11; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0",
    'Accept': "*/*",
    'Accept-Language': "en-US,en;q=0.5",
    'Referer': "https://issuu.com/ducatiomaha/docs/ducatiomaha_2015_diavel?e=1222863/13414409",
    'Cache-Control': "max-age=0",
    'DNT': "1",
    'Origin': "https://issuu.com",
    'TE': 'Trailers'
    }

response = requests.request("GET", url, data=payload, headers=headers)


data = response.json()

print("Got a document with", len(data['document']['pages']), "pages")

prepare_download(download_dir)
os.chdir(download_dir)
print("Downloading Images")
images = []
for page in tqdm(data['document']['pages']):
    imgPath = os.path.join(download_dir, page['imageUri'].split('/')[-1])
    downloadFile(page['imageUri'], download_dir + "/jpg/")
    images.append({
        "name": imgPath,
        "height": page["height"],
        "width": page["width"],
        "verfied": False
        })
    downloadFile(page['layersInfo']['uri'], download_dir + "/bin/")

print(images)
