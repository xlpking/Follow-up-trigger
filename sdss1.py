# this cell imports functions from the python standard library in a way that works with both python 2 and 3
try:
    # Python 3.x
    from urllib.parse import urlencode
    from urllib.request import urlretrieve
except ImportError:
    # Python 2.x
    from urllib import urlencode
    from urllib import urlretrieve

import numpy as np
import IPython.display
from matplotlib import pyplot as plt
from astroquery.sdss import SDSS
from astropy import units as u
from astropy.coordinates import SkyCoord
import sys
from astropy.table import Table

def xgetsdss(ra,dec):
    #hcg7_center = SkyCoord.from_name('HCG 7')
    #hcg7_center = "20.81625, 0.88806"
    print("ra=%f, dec=%f\n"%(ra, dec))
    hcg7_center = str(ra) + "," + str(dec)
    print("hcg7 is %s\n"%(hcg7_center))

    sdss = SDSS.query_region(coordinates=hcg7_center, radius=20*u.arcsec,
                             spectro=False,
                             photoobj_fields=['ra','dec','u','g','r','i','z'])
    print(sdss)
    filename =  str(hcg7_center) + "_sdss.txt"
  #  with open(filename, 'a') as f:  # 如果filename不存在会自动创建， 'a'表示追加数据
  #      f.write(str(sdss))

    np.savetxt(filename, sdss, fmt='%f', header='ra, dec, u, g, r, i, z')


if __name__=='__main__':
    #raput = float(sys.argv[1])
    #decput = float(sys.argv[2])
    #raput = 20.81625
    #decput = 0.88806
    raput = 132.82277
    decput = 71.20111 
    xgetsdss(raput, decput)


