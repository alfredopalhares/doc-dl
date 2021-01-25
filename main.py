#!/usr/bin/python

import json
import os
import requests
import shutil
from PIL import Image
from fpdf import FPDF
from pathlib import Path
from tqdm import tqdm
import re

download_dir = 'download'
image_dir = os.path.join(download_dir, "jpg/")
bin_dir = os.path.join(download_dir, "bin/")

def prepare_download(download_path:str):
    if os.path.isdir(download_path):
        print("Cleaning old download directory")
        shutil.rmtree(download_path)
    os.mkdir(download_path)
    os.mkdir(image_dir)
    os.mkdir(bin_dir)

# TODO: Check if the file is already there

def downloadFile(uri, path):
    filename=os.path.join(os.getcwd(), path, uri.split('/')[-1])
    url = "https://" + uri
    jpg = open(filename, 'wb')
    down_headers = headers
    down_headers['Host'] = 'image.isu.pub'
    response = requests.request("GET",url, headers=headers)
    jpg.write(response.content)
    jpg.close()


def extract_number_from_page(page_uri: str) -> int:
    """ Tryies to extrat the number from the pages """
    # Yeah, you will never remember this
    # https://regex101.com/r/2ZGOJj/2
    page_no = re.search(r'(?<=page_)\d+', page_uri)
    if page_no == None:
        print("Raise an exepction")
        exit(1)
    else:
        return int(page_no.group())
    return 0

url = "https://reader3.isu.pub/ducatiomaha/ducatiomaha_2015_diavel/reader3_4.json"

payload = ""
headers = {
    'Host': "reader3.isu.pub",
    'User-Agent':  "Mozilla/5.0 (X11; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0",
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
print("Downloading Files")
# TODO: Bin files are not downloading right
# maybe the is the Host Header that is not matching the link
images = []
for page in tqdm(data['document']['pages']):
    imgPath = os.path.join(download_dir, 'jpg', page['imageUri'].split('/')[-1])
    page_no = extract_number_from_page(page['imageUri'])
    downloadFile(page['imageUri'], download_dir + "/jpg/")
    images.append({
        "name": imgPath,
        "page_no" : page_no,
        "height": page["height"],
        "width": page["width"],
        "verfied": False
        })
    downloadFile(page['layersInfo']['uri'], download_dir + "/bin/")

print(images)
# Converting images to PDFs
# https://pyfpdf.github.io/fpdf2/Tutorial.html 
print("Converting images into PDF")
pdf = FPDF()
for img in tqdm(images):
    print(img)
    if not os.path.exists(img['name']):
        print("Something wronh could not find the image")
        exit(1)
    elif img['page_no'] == 1:
        print('Using the first page as cover')
        pdf = FPDF(unit= "pt", format= [img['width'], img['height']] )
    pdf.add_page()
    pdf.image(img['name'], 0, 0, img['width'], img['height']) 

pdf.output("output.pdf")