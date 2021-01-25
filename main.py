#!/usr/bin/python

import json
import os
import requests
import shutil
import re
import click

from PIL import Image
from fpdf import FPDF
from pathlib import Path
from tqdm import tqdm

# Globals
verbosity = 0

def prepare_paths(download_path: str, image_path: str, bin_path: str, cleanup=False)->bool:
    if cleanup or (os.path.isdir(download_path) and not cleanup):
        log("Cleaning download directory", 1)
        shutil.rmtree(download_path)
        return True
    else:
        log(f'Storing downloads on: {download_path}', 1)
        os.mkdir(download_path)
        log(f'Storing Images on: {image_path}', 2)
        os.mkdir(image_path)
        log(f'Storing Binaries on: {bin_path}', 2)
        os.mkdir(bin_path)
        return False

# TODO: Check if the file is already there
def downloadFile(uri: str, path: str, headers: dict):
    filename=os.path.join(os.getcwd(), path, uri.split('/')[-1])
    url = "https://" + uri
    jpg = open(filename, 'wb')
    down_headers = headers
    down_headers['Host'] = uri.split('/')[0]
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

def set_log_level(verbose):
    global verbosity
    verbosity = verbose
    if verbosity > 0:
        click.echo(message=f'Verbosity leverl set to: {verbosity}', color=True)

def log(message:str, level=0):
    if level <= verbosity:
        click.echo(message)

@click.command()
@click.argument('url')
@click.option('-f', '--file', default='output.pdf', help='Name of the output pdf')
@click.option('-d', '--download', default='download', help='Download Directory')
@click.option('-k', '--keep', default=False, is_flag=True, help='Keep downladed files after generating the file')
@click.option('-v', '--verbose', count=True)

def main(download, file, keep, url, verbose):

    set_log_level(verbose)
    #url = "https://reader3.isu.pub/ducatiomaha/ducatiomaha_2015_diavel/reader3_4.json"
    image_path = os.path.join(download, "jpg/")
    bin_path = os.path.join(download, "bin/")

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
    pages = len(data['document']['pages'])
    log(f'Got a document with {pages} pages', 1)

    prepare_paths(download, image_path, bin_path)
    log("Downloading Files....")
    images = []
    for page in tqdm(data['document']['pages']):
        imgPath = os.path.join(image_path, page['imageUri'].split('/')[-1])
        page_no = extract_number_from_page(page['imageUri'])
        downloadFile(uri=page['imageUri'], path=image_path, headers=headers)
        images.append({
            "name": imgPath,
            "page_no" : page_no,
            "height": page["height"],
            "width": page["width"],
            "verfied": False
            })
        downloadFile(uri=page['layersInfo']['uri'], path=bin_path, headers=headers)

    # Converting images to PDFs
    # https://pyfpdf.github.io/fpdf2/Tutorial.html 
    print("Converting images into PDF")
    pdf = FPDF()
    for img in tqdm(images):
        if not os.path.exists(img['name']):
            print("Something wronh could not find the image")
            exit(1)
        elif img['page_no'] == 1:
            print('Using the first page as cover')
            pdf = FPDF(unit= "pt", format= [img['width'], img['height']] )
        pdf.add_page()
        pdf.image(img['name'], 0, 0, img['width'], img['height']) 

    pdf.output("output.pdf")

    prepare_paths(download_path=download, image_path=image_path, bin_path=bin_path, cleanup=keep)
if __name__ == '__main__':
    main()