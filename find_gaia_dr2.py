#!/usr/bin/env python
"""G.Landais (CDS) 24-mar-2018
   Query I/345/gaia2

   find_gaia_dr2.py [-h] [-a] [-r radius] [-m max] [constraints] [--format=tsv|votable|ascii] [position]
            [--ipix=order:num] [--no-format]
     -a: display all columns
     -r: radius in arcsec
     -m: max number of lines in output
     -h: this help
     --format: output (--format=tsv|votable|ascii)

     position : ra dec position or target name
                example: find_gaia_dr2.py M1

     Other constraints:
		--no-format : ...
		--ra= : ...
		--dec= : ...
		--source_id= : ...
		--random_index= : ...
		--parallax= : ...
		--parallax_error= : ...
		--parallax_over_error= : ...
		--pmra= : ...
		--pmdec= : ...
		--phot_g_mean_mag= : ...
		--phot_bp_mean_mag= : ...
		--phot_rp_mean_mag= : ...
		--bp_rp= : ...
		--bp_g= : ...
		--g_rp= : ...
		--radial_velocity= : ...
		--radial_velocity_error= : ...
		--l= : ...
		--b= : ...
		--ipix= : ...
		--no-format : ...


     Example: --ra=>"10"

Note: ouput&capabilites are specific to the options

use --no-format to get original precision
(only available with position or ipix constraint)


     Licensed under a BSD license - see LICENSE.txt for details

"""

import os, sys
import getopt
try:
    sys.path.append(os.path.split(os.path.abspath(sys.argv[0]))[0])
    import vizquery
except:
    sys.stderr.write("(error) needs vizquery.py in PYTHONPATH\n")
    sys.exit(1)

if int(sys.version[0])<3:
    from urllib2 import quote
else:
    from urllib.parse import quote

NO_FORMAT = "noformat"

class QueryCat():
    def __init__(self):
        self.position = None
        self.radius = vizquery.DEFAULT_RADIUS
        self.__constraints = []
        self.format = None

    def query_cat(self, constraints=None, all = False, limit=vizquery.DEFAULT_LIMIT):
        """init constraints parameters
        :param constraints: list of constraints ((name,value), ...)
        :param all: display all columns(efault False)
        :param limit: max number of records
        """
        pass

    def get(self):
        """get astropy table"""
        pass

    def print_stdout(self):
        """print the result on stdout"""
        pass


class QueryCatVizieR(QueryCat):
    def __init__(self):
        QueryCat.__init__(self)
        self.__client = vizquery.CDSClient(default_format=vizquery.FORMAT_ASCII)
        self.limit = vizquery.DEFAULT_LIMIT

    def query_cat(self, constraints=None, all = False, limit=vizquery.DEFAULT_LIMIT):
        params = []

        if self.position:
            params.append("-c={0}".format(quote(self.position)))

        if self.radius:
            params.append("-c.rs={0:f}".format(self.radius))

        if all is True:
            params.append("-out.all=1")

        if limit is not None:
            params.append("-out.max={0:d}".format(limit))
        else:
            params.append("-out.max={0:d}".format(self.limit))

        if constraints is not None:
            for constraint in constraints:
                params.append("{0}=={1}".format(constraint[0], constraint[1]))

        self.__client.query("I/345/gaia2", params=params)

        if self.format is not None:
            self.__client.format = self.format

    def get(self):
        return self.__client.get()

    def print_stdout(self):
        return self.__client.print_stdout()

import re

if int(sys.version[0])<3:
    import urllib2 as ulib
else:
    import urllib.request as ulib

VIZIER_BIG_CAT_URL = "http://axel.u-strasbg.fr/viz-bin/catClient.cgi"
class QueryCatClient(QueryCat):
    def __init__(self):
        """Constructor
        """
        QueryCat.__init__(self)
        self.__url = None
        self.__ipix = None
        self.limit = vizquery.DEFAULT_LIMIT
        self.noformat = False

    def set_healpix(self, ipix):
        self.__ipix  = ipix

    def query_cat(self, constraints=None, all = False, limit=vizquery.DEFAULT_LIMIT):
        self.__url = VIZIER_BIG_CAT_URL + "?-source=GAIA_DR2"
        self.__url += "&-c.rs=" + str(self.radius)

        if self.position:
            self.__url += "&-c="+quote(self.position)

        elif self.__ipix is not None:
            self.__url += "&--ipix="+self.__ipix
            if self.format not in (vizquery.FORMAT_TSV, vizquery.FORMAT_VOTABLE):
                self.format = vizquery.FORMAT_TSV

        if limit: self.__url += "&-out.max=" + str(limit)
        else: self.__url += "&-out.max=" + str(self.limit)

        if self.noformat is True:
            self.__url += "&--noformat=true"
            if self.format not in (vizquery.FORMAT_TSV, vizquery.FORMAT_VOTABLE):
                self.format = vizquery.FORMAT_TSV

        if self.format is None:
            self.__url += "&--format="+vizquery.FORMAT_TSV

        else:
            self.__url += "&--format="+self.format

        if constraints is not None:
            for constraint in constraints:
                self.__url += '&-filter="{0}{1}"'.format(constraint[0], constraint[1])


    def get(self):
        raise Exception("not available yet")

    def print_stdout(self):
        if self.__url is None:
            raise Exception("query needs to be init")

        #sys.stderr.write("(debug) query: {0}\n".format(self.__url))
        request = ulib.Request(self.__url)
        request.add_header("User-Agent", vizquery.USER_AGENT)
        fd = ulib.urlopen(request)
        print(fd.read().decode('utf8'))


if __name__ == "__main__":

    __radius = vizquery.DEFAULT_RADIUS
    __position = None
    __limit = None
    __mime = vizquery.FORMAT_ASCII
    __noformat = False
    __ipix = None
    __all = False
    __constraints = []


    __options = ('help','format=','no-format','ra=','dec=','source_id=','random_index=','parallax=','parallax_error=','parallax_over_error=','pmra=','pmdec=','phot_g_mean_mag=','phot_bp_mean_mag=','phot_rp_mean_mag=','bp_rp=','bp_g=','g_rp=','radial_velocity=','radial_velocity_error=','l=','b=','ipix=','no-format')
    try :
        __opts, __args = getopt.getopt(sys.argv[1:], 'har:m:', __options)
    except:
        help("__main__")
        sys.exit(1)

    for __o, __a in __opts:
        if __o in ("-h", "--help"):
            help("__main__")
            sys.exit(1)

        elif __o == "-r":
            try:
                __radius = float(__a)
            except:
                sys.stderr.write("(error) wrong radius format\n")

        elif __o == "-m":
            try:
                __limit = int(__a)
            except:
                sys.stderr.write("(error) wrong limit/max format\n")

        elif __o == "-a":
            __all = True

        elif __o == "--format":
            __mime = __a

        elif __o == "--no-format":
            __noformat = True

        elif __o == "--ipix":
            __ipix = __a

        else:
            for opt in __options[2:]:
                value = opt[:len(opt)-1]
                if __o[2:] == value:
                     __constraints.append((value, __a))
                     break


    for __arg in __args:
        if __position is None:
            __position = __arg
        else:
            __position += " "+ __arg

    if __noformat is True or __ipix is not None:
        __querycat = QueryCatClient()
        if __ipix is not None:
            __querycat.set_healpix(__ipix)
        __querycat.noformat=__noformat
    else:
        __querycat = QueryCatVizieR()


    __querycat.position = __position
    __querycat.radius = __radius

    if __mime in (vizquery.FORMAT_TSV, vizquery.FORMAT_VOTABLE, vizquery.FORMAT_ASCII):
        __querycat.format = __mime
    else:
        raise Exception("format not yet available")

    __querycat.query_cat(constraints=__constraints, all=__all, limit=__limit)
    __querycat.print_stdout()

