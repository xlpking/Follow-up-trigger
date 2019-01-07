# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup

RA = 54.10576	
DEC = 33.59914
str = '%f %f'%(RA,DEC)

url='http://vizier.u-strasbg.fr/viz-bin/VizieR-4?-ref=VIZ5bd5371da602&-out.add=_r&-out.add=_RAJ%2C_DEJ&-sort=_r&-order=I&-oc.'\
    'form=sexa&-meta.foot=1&-meta=1&-meta.ucd=2&-c.geom=r&-c.eq=J2000&-c.u=arcmin&-c.r=+0.5&-c=' + str
session=requests.Session()
r = session.get(url, timeout=500, verify=False)
content=r.text

'''
content_file=open('abc.txt', 'r')
content = content_file.read()
content_file.close()
'''
'''
content_file=open('abc.txt', 'w')
content_file.write(content)
content_file.close()
'''


#ucac4
pageContent = BeautifulSoup(content, 'html.parser')
tables = pageContent.findAll(attrs={'id' : "!ext/ucac4.exe_4"})

print("\n******************tables")
print(tables)

trs=tables[0].findAll("tr",attrs={'class' : "tuple-2"})
print("\n******************trs")
print(trs)
tds = trs[0].findAll('td')
print("\n******************tds")
print(tds)
print("\n******************td4")
td4=tds[4]
print(td4)
raj2000=td4.contents[0]
print("\n******************raj2000")
print(raj2000)
'''

#Gaia-2
pageContent = BeautifulSoup(content, 'html.parser')
tables = pageContent.findAll(attrs={'id' : "!ext-tsv/catClient.py_13"})

print("\n******************tables")
print(tables)

trs=tables[0].findAll("tr",attrs={'class' : "tuple-2"})
print("\n******************trs")
print(trs)
tds = trs[0].findAll('td')
print("\n******************tds")
print(tds)
print("\n******************td9")
td9=tds[9]
print(td9)
td31=tds[31]
plx=td9.contents[0]
Teff=td31.contents[0]
print("\n******************plx")
print(plx)
print(Teff)


'''
#Panstarrs
pageContent = BeautifulSoup(content, 'html.parser')
tables = pageContent.findAll(attrs={'id' : "!ext-tsv/catClient.py_21"})

print("\n******************tables")
print(tables)

trs=tables[0].findAll("tr",attrs={'class' : "tuple-2"})
print("\n******************trs")
print(trs)

tds = trs[0].findAll('td')
print("\n******************tds")
print(tds)
'''
print("\n******************td9")
td9=tds[9]
print(td9)
td31=tds[31]
plx=td9.contents[0]
Teff=td31.contents[0]
print("\n******************plx")
print(plx)
print(Teff)
'''
'''
td14=tds[14]
td19=tds[19]
td23=tds[23]
td29=tds[29]
td33=tds[33]

gmag14=td14.contents[0]
print(gmag14)

rmag19=td19.contents[0]
print(rmag19)

imag23=td23.contents[0]
print(imag23)

zmag29=td29.contents[0]
print(zmag29)

ymag33=td33.contents[0]
print(ymag33)

print("plx=%f, Teff=%f, gmag=%f, rmag=%f,\n"\
      "imag=%f,zmag=%f, ymag=%f\n"%(plx,Teff,gmag14,rmag19,imag23,zmag29,ymag33))
'''

