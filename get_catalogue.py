from astroquery.vizier import Vizier
#---importastropystuff
from astropy.table import Table,Column

# Vizier.ROW_LIMIT = -1
Vizier.ROW_LIMIT = 50

catalog_list = Vizier.find_catalogs('glade2')

print('description',{k:v.description for k,v in catalog_list.items()})

cat = Vizier.get_catalogs('VII/281/glade2')
# print(len(cat))

s4n=Vizier.get_catalogs(cat.keys())
print('glade table:')
print(s4n[0])

v=Vizier(columns=['RAJ2000','DEJ2000'])
# print(v)
# agn = Vizier(catalog="VII/281/glade2",columns=['RAJ2000','DEJ2000'])[0]
# print('agn',agn)

outputfile = 'glade2.3.txt'
g = open(outputfile,'w')
for p in range(len(s4n[0])):
	ra = s4n[0][p][6]
	dec = s4n[0][p][7]
	ra_tex = ra*10000
	if dec >= 0:
		dec_tex = dec*10000
	else:
		dec_tex = abs(dec*10000) + 10000000
	galaxy_id = ("%i-%07d-%08d" % (p,ra_tex,dec_tex))
	g.write('%s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s \n' % (galaxy_id,s4n[0][p][0],s4n[0][p][1],s4n[0][p][2],s4n[0][p][3],s4n[0][p][6],s4n[0][p][7],s4n[0][p][8],s4n[0][p][9],s4n[0][p][10],s4n[0][p][11],s4n[0][p][12],s4n[0][p][13],s4n[0][p][14],s4n[0][p][15],s4n[0][p][16]))
    # g.write('%s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s \n' % (s4n[0][p][0],s4n[0][p][1],cat[p][2],cat[p][3],cat[p][6],cat[p][7],cat[p][8],cat[p][9],cat[p][10],cat[p][11],cat[p][12],cat[p][13],cat[p][14],cat[p][15],cat[p][16],cat[p][17],cat[p][18],cat[p][19]))
g.close()