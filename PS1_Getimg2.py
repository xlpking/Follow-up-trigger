
from __future__ import print_function
import numpy
from astropy.io.fits.hdu import image
from astropy.table import Table
import requests
from PIL import Image
from io import BytesIO
import pylab
from PIL import Image
import matplotlib.pylab as plt
import os, sys
import time, datetime



def getimages(ra, dec, size=240, filters="grizy"):
    """Query ps1filenames.py service to get a list of images

    ra, dec = position in degrees
    size = image size in pixels (0.25 arcsec/pixel)
    filters = string with filters to include
    Returns a table with the results
    """

    service = "https://ps1images.stsci.edu/cgi-bin/ps1filenames.py"
    url = ("{service}?ra={ra}&dec={dec}&size={size}&format=fits"
           "&filters={filters}").format(**locals())
    table = Table.read(url, format='ascii')
    return table


def geturl(ra, dec, size=240, output_size=None, filters="grizy", format="jpg", color=False):
    """Get URL for images in the table

    ra, dec = position in degrees
    size = extracted image size in pixels (0.25 arcsec/pixel)
    output_size = output (display) image size in pixels (default = size).
                  output_size has no effect for fits format images.
    filters = string with filters to include
    format = data format (options are "jpg", "png" or "fits")
    color = if True, creates a color image (only for jpg or png format).
            Default is return a list of URLs for single-filter grayscale images.
    Returns a string with the URL
    """

    if color and format == "fits":
        raise ValueError("color images are available only for jpg or png formats")
    if format not in ("jpg", "png", "fits"):
        raise ValueError("format must be one of jpg, png, fits")
    table = getimages(ra, dec, size=size, filters=filters)
    url = ("https://ps1images.stsci.edu/cgi-bin/fitscut.cgi?"
           "ra={ra}&dec={dec}&size={size}&format={format}").format(**locals())
    if output_size:
        url = url + "&output_size={}".format(output_size)
    # sort filters from red to blue
    flist = ["yzirg".find(x) for x in table['filter']]
    table = table[numpy.argsort(flist)]
    if color:
        if len(table) > 3:
            # pick 3 filters
            table = table[[0, len(table) // 2, len(table) - 1]]
        for i, param in enumerate(["red", "green", "blue"]):
            url = url + "&{}={}".format(param, table['filename'][i])
    else:
        urlbase = url + "&red="
        url = []
        for filename in table['filename']:
            url.append(urlbase + filename)
    return url


def getcolorim(ra, dec, size=240, output_size=None, filters="grizy", format="jpg"):
    """Get color image at a sky position

    ra, dec = position in degrees
    size = extracted image size in pixels (0.25 arcsec/pixel)
    output_size = output (display) image size in pixels (default = size).
                  output_size has no effect for fits format images.
    filters = string with filters to include
    format = data format (options are "jpg", "png")
    Returns the image
    """

    if format not in ("jpg", "png"):
        raise ValueError("format must be jpg or png")
    url = geturl(ra, dec, size=size, filters=filters, output_size=output_size, format=format, color=True)
    r = requests.get(url)
    im = Image.open(BytesIO(r.content))
    return im


def getgrayim(ra, dec, size=240, output_size=None, filter="g", format="jpg"):
    """Get grayscale image at a sky position

    ra, dec = position in degrees
    size = extracted image size in pixels (0.25 arcsec/pixel)
    output_size = output (display) image size in pixels (default = size).
                  output_size has no effect for fits format images.
    filter = string with filter to extract (one of grizy)
    format = data format (options are "jpg", "png")
    Returns the image
    """

    if format not in ("jpg", "png"):
        raise ValueError("format must be jpg or png")
    if filter not in list("grizy"):
        raise ValueError("filter must be one of grizy")
    url = geturl(ra, dec, size=size, filters=filter, output_size=output_size, format=format)
    r = requests.get(url[0])
    im = Image.open(BytesIO(r.content))
    return im




def xgetps1(ra, dec, size1, otname):
    ps1img = "%s_ps1_0.jpg" % (otname)
    # grayscale image
    #gim = getgrayim(ra,dec,size=size1,filter="i")
    # color image
    cim = getcolorim(ra,dec,size=size1,filters="grz")
    #r image
    #cim = getgrayim(ra,dec, size=size1, filter="r")
    #print(dir(cim))
    cim.save(ps1img)

    if os.access(ps1img, os.F_OK):

        plt.figure(figsize=(2, 2), dpi=100)
        #set size square
        img_arr = plt.imread(ps1img)
        plt.imshow(img_arr)
        plt.xticks([])
        plt.yticks([])
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())
        plt.subplots_adjust(top=1, bottom=0, left=0, right=1, hspace=0, wspace=0)
        plt.margins(0, 0)


        x = 1200
        y = 1200
        plt.scatter(x,y, marker="o", c='', edgecolors='w', s=1000)
        textc="1*1 arcmin"
        radec = "RA=%f, DEC%f" % (ra, dec)
        plt.text(40, 50, otname, color="w")
        plt.text(40,60, radec, color="w")
        plt.text(120, 220, textc, color="w")
        #plt.show()
        pngfilename = "%s_ps1.png"%(otname)
        plt.savefig(pngfilename, dpi=100)
        return pngfilename
    else:
        print("no ps1 image ")



def xgetps10arcmin(ra, dec, size1, otname):
    ps1img = "%s_ps1_0.jpg" % (otname)
    if os.path.exists(ps1img):
        os.remove(ps1img)
    # grayscale image
    #gim = getgrayim(ra,dec,size=size1,filter="i")
    # color image
    cim = getcolorim(ra,dec,size=size1,filters="grz")
    #r image
    #cim = getgrayim(ra,dec, size=size1, filter="r")
    #print(dir(cim))
    cim.save(ps1img)

    if os.access(ps1img, os.F_OK):

        plt.figure(figsize=(4, 4), dpi=50)
        #set size square
        img_arr = plt.imread(ps1img)
        plt.imshow(img_arr)
        plt.xticks([])
        plt.yticks([])
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())
        plt.subplots_adjust(top=1, bottom=0, left=0, right=1, hspace=0, wspace=0)
        plt.margins(0, 0)


        x = 1200
        y = 1200
        plt.scatter(x,y, marker="o", c='', edgecolors='w', s=1000)
        textc="10*10 arcmin"
        
        radec = "RA=%f, DEC=%f" % (ra, dec)
        plt.text(800, 200, otname, color="w")
        plt.text(600,300, radec, color="w")
        plt.text(100, 2200, textc, color="w")
        #plt.show()
        pngfilename = "%s_ps1.png"%(otname)
        plt.savefig(pngfilename, dpi=100)
        return pngfilename
    else:
        print("no ps1 image ")


if __name__=='__main__':
    ra = sys.argv[1]
    dec = sys.argv[2]
    size1 = sys.argv[3]
    otname = sys.argv[4]
    # Crab Nebula position
    print(datetime.datetime.now())
    #ra = 42.282871
    #dec = 49.837971
    #otname = "G201221_C20405"
    # 1 arcmin
    #size1 = 240  # 4pixel= 1 arcsec,  2400pixel=10 arcmin, 240pixel=1 arcmin,
    #xgetps1(ra,dec,size1, otname)
    #10 arcmin
    #size1 = 2400  # 4pixel= 1 arcsec,  2400pixel=10 arcmin, 240pixel=1 arcmin,
    xgetps10arcmin(ra, dec, size1, otname)
       
    print(datetime.datetime.now())


