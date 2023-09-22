# $Header$
import numpy as num
import AspHealPix
import databaseAccess

class HealPixIndex(object):
    def __init__(self, nside=32, ord=AspHealPix.Healpix.NESTED,
                 coordsys=AspHealPix.SkyDir.EQUATORIAL):
        self.hp = AspHealPix.Healpix(nside, ord, coordsys)
    def __call__(self, ra, dec):
        return AspHealPix.Pixel(AspHealPix.SkyDir(ra, dec), self.hp).index()

hp_index = HealPixIndex()

def insert_pointsource(name, ra, dec, source_type, debug=False):
    nx = num.cos(ra*num.pi/180.)*num.cos(dec*num.pi/180.)
    ny = num.sin(ra*num.pi/180.)*num.cos(dec*num.pi/180.)
    nz = num.sin(dec*num.pi/180.)

    healpix_id = hp_index(ra, dec)

    sql = "insert into POINTSOURCES (PTSRC_NAME, HEALPIX_ID, SOURCE_TYPE, SPECTRUM_TYPE, RA, DEC, ERROR_RADIUS, NX, NY, NZ, IS_OBSOLETE, IS_PUBLIC) values ('%s', %i, '%s', 'PowerLaw2', %7.3f, %7.3f, 0, %f, %f, %f, 0, 0)" % (name, healpix_id, source_type, ra, dec, nx, ny, nz)

    if debug:
        print sql
    else:
        databaseAccess.apply(sql)

def create_alias(ptsrc_name, alias, debug=False):
    sql = ("update pointsources set alias='%s' where ptsrc_name='%s'"
           % (alias, ptsrc_name))
    if debug:
        print sql
    else:
        databaseAccess.apply(sql)

def set_pointsourcetype(ptsrc_name, sourcetype, debug=False):
    sql = ("insert into pointsourcetypeset (ptsrc_name, sourcesub_type) "
           + "values ('%s', '%s')" % (ptsrc_name, sourcetype))
    if debug:
        print sql
    else:
        databaseAccess.apply(sql)

def update_pointsourcetype(ptsrc_name, sourcetype, debug=False):
    sql = ("update pointsourcetypeset set "
           "sourcesub_type='%s' where ptsrc_name='%s'"
           % (sourcetype, ptsrc_name))
    if debug:
        print sql
    else:
        databaseAccess.apply(sql)

def set_ispublic(srcname, debug=False):
    sql = "update pointsources set is_public=1 where ptsrc_name='%s'" % srcname
    if debug:
        print sql
    else:
        databaseAccess.apply(sql)

def expose_lightcurves(aspname, day, week, debug=False):
    sql = ("update lightcurves set is_monitored=1 where " +
           "ptsrc_name='%s' " % aspname +
           "and ((interval_number<%i and frequency='daily') " % day +
           "or (interval_number<%i and frequency='weekly'))" % week)
    if debug:
        print sql
    else:
        databaseAccess.apply(sql)

def add_drp_source(srcname, ra, dec, srctype, aspnames, day, week, debug=True):
    insert_pointsource(srcname, ra, dec, srctype, debug)
    set_pointsourcetype(srcname, 'DRP', debug)
    set_ispublic(srcname, debug)
    for item in aspnames:
        create_alias(item, srcname, debug)
        update_pointsourcetype(item, 'ATEL', debug)
        expose_lightcurves(item, day, week, debug)

if __name__ == '__main__':
    add_drp_source('4FGL J1706.8+1319', 256.72, 13.33, 'Blazar',
                   ('ASPJ170823+125348',), 5536, 792, debug=False)

#    add_drp_source('S5 0532+82', 85.911862, 82.641323, 'Blazar',
#                   ('ASPJ054342+823445',), 5484, 784, debug=False)
#
#    add_drp_source('TXS 0358+210', 60.438192, 21.174607, 'Blazar',
#                   ('ASPJ040037+202801',), 5465, 781, debug=False)
#
#    add_drp_source('3C 216', 137.38957, 42.89624, 'Blazar',
#                   ('ASPJ090833-425048',), 5424, 776, debug=False)
#
#    add_drp_source('4C +27.50', 350.499, 27.546, 'Blazar',
#                   ('ASPJ231858+264553', 'ASPJ232449+280111'), 5247, 750,
#                   debug=False)
#
#    add_drp_source('Fermi J0008+6829', 2.086, 68.579, 'Blazar',
#                   ('ASPJ000950+680328',), 5243, 749, debug=False)
#
#    add_drp_source('TXS 1029-137', 158.0259, -14.0054, 'Blazar',
#                   ('ASPJ103251-135338',), 5172, 739, debug=False)
#
#    add_drp_source('PKS B0027-426', 7.572886, -42.412912, 'Blazar',
#                   ('ASPJ003046-421817',), 4712, 674, debug=False)
#
#    add_drp_source('PKS 1716-771', 260.961855, -77.230706, 'Blazar',
#                   ('ASPJ172523-772516',), 5072, 725, debug=False)
#
#    add_drp_source('Fermi J0431+5458', 67.86, 54.98, 'Blazar',
#                   ('ASPJ042637+543910',), 4973, 711, debug=False)
#
#    add_drp_source('Fermi J0614+1713', 93.63, 17.23, 'Blazar',
#                   ('ASPJ061429+170747',), 4969, 710, debug=False)
#
#    add_drp_source('PMN J1315-5334', 198.767667, -53.576667, 'Blazar',
#                   ('ASPJ131525-534219',), 4834, 691, debug=False)
#
#    add_drp_source('PKS 0301-721', 45.410407, -71.942953, 'Blazar',
#                   ('ASPJ030254-715350',), 4826, 690, debug=False)
#
#    add_drp_source('RS Oph', 267.555008, -6.707911, 'MQ',
#                   ('ASPJ175144-064351',), 4793, 685, debug=False)
#
#    add_drp_source('PKS 0202-17', 31.240310, -17.022178, 'Blazar',
#                   ('ASPJ020749-165422',), 4772, 682, debug=False)
#
#    add_drp_source('PKS 1127-14', 172.529385, -14.824274, 'Blazar',
#                   ('ASPJ112923-145052',), 4552, 651, debug=False)
#
#    add_drp_source('TXS 2013+370', 303.869708, 37.183198, 'Blazar',
#                   ('ASPJ201610+371125',), 4548, 650, debug=False)
#
#    add_drp_source('S4 1726+45', 261.865212, 45.511036, 'Blazar',
#                   ('ASPJ172439+452613',), 4514, 646, debug=False)
#
#    add_drp_source('PKS 1156-221', 179.796947, -22.476917, 'Blazar',
#                   ('ASPJ115736-221020',), 4265, 610, debug=False)
#
#    add_drp_source('OS 300', 240.5302642, 33.4480756, 'Blazar',
#                   ('ASPJ160329+333314',), 4429, 633, debug=False)
#
#    add_drp_source('PKS 1719-729', 261.506000, -72.999556, 'Blazar',
#                   ('ASPJ172614-725305',), 4405, 630, debug=False)
#
#    add_drp_source('TXS 2032+117', 308.6546, 11.9087, 'Blazar',
#                   ('ASPJ203459+122311',), 4349, 622, debug=False)
#
#    add_drp_source('PKS 1335-127', 204.415761, -12.956859, 'Blazar',
#                   ('ASPJ133647-122651',), 4345, 621, debug=False)
#
#    add_drp_source('PKS 1453-426', 224.304083, -42.810083, 'Blazar',
#                   ('ASPJ145603-425137',), 4312, 616, debug=False)
#
#    add_drp_source('PKS 2052-47', 314.068166, -47.246563, 'Blazar',
#                   ('ASPJ205731-471323',), 4269, 610, debug=False)
#
#    add_drp_source('PKS 2004-447', 301.979929, -44.578967, 'Blazar',
#                   ('ASPJ200743-442549',), 4140, 592, debug=False)
#
#    add_drp_source('PKS 2345-16', 357.010869, -16.520006, 'Blazar',
#                   ('ASPJ234841-163341',), 4120, 588, debug=False)
#
#    add_drp_source('PKS 1413+135', 213.99507, 13.33992, 'Blazar',
#                   ('ASPJ141639+132059',), 4082, 584, debug=False)
#
#    add_drp_source('TXS 0025+197', 7.1242433, 20.0074289, 'Blazar',
#                   ('ASPJ002815+200630',), 3754, 537, debug=False)
#
#    add_drp_source('PKS 2246+208', 342.252361, 21.11745, 'Blazar',
#                   ('ASPJ224851+210149',), 3845, 550, debug=False)
#
#    add_drp_source('PKS 0226-559', 37.090042, -55.767639, 'Blazar',
#                   ('ASPJ023100-562210',), 3867, 553, debug=False)
#    print "\n"
#    add_drp_source('B3 0650+453', 103.598807, 45.239874, 'Blazar',
#                   ('ASPJ065300+451500',), 1154, 166, debug=False)
#    print "\n"
#    add_drp_source('TXS 0059+581', 15.690676, 58.403093, 'Blazar',
#                   ('ASPJ010240+582309',), 1296, 186, debug=False)
#    print "\n"
#    add_drp_source('Fermi J0052+1110', 13.09, 11.16, 'Blazar',
#                   ('ASPJ005201+102041',), 1314, 188, debug=False)
#    print "\n"
#    add_drp_source('Fermi J0902-4624', 135.56, -46.41, 'Blazar',
#                   ('ASPJ085846-464741',), 1360, 195, debug=False)
#    print "\n"
#    add_drp_source('PMN J2141-6411', 325.443458, -64.187333, 'Blazar',
#                   ('ASPJ213832-641920',), 2281, 327, debug=False)
#    print "\n"
#    add_drp_source('4C +40.25', 155.798192, 39.804272, 'Blazar',
#                   ('ASPJ102318+395444',), 2709, 388, debug=False)
#    debug = False
#    srcname = 'PSR B1259-63'
#    set_ispublic(srcname, debug)
#    update_pointsourcetype(srcname, 'DRP', debug)
#    aspname = 'ASPJ125654-634112'
#    create_alias(aspname, srcname, debug)
#    expose_lightcurves(aspname, 3418, 489, debug)
#
#    print "\n"
#    add_drp_source('PSR B1259-63', 195.698559, -63.835729, 'Pulsar',
#                   ('ASPJ125654-634112',), 3418, 489, debug=False)
#    print "\n"
#    add_drp_source('1ES 1215+303', 184.467008, 30.116843, 'Blazar',
#                   ('ASPJ121738+300445',), 3215, 460, debug=False)
#
#
#    add_drp_source('OQ 334', 215.626579, 32.386233, 'Blazar',
#                   ('ASPJ141749+322549',), 3816, 546, debug=False)
#
#    add_drp_source('PKS 2134+004', 324.160776, 0.698392, 'Blazar',
#                   ('ASPJ213608+005212',), 3815, 546, debug=False)
#
#    add_drp_source('Fermi J1153-1124', 178.44, -11.11, 'Blazar',
#                   ('ASPJ115255-112410',), 3792, 542, debug=False)
#
#    add_drp_source('PKS 0035-252', 9.561397, -24.983954, 'Blazar',
#                   ('ASPJ003846-245830',), 3671, 525, debug=False)
#
#    add_drp_source('TXS 0646-176', 102.118744, -17.734844, 'Blazar',
#                   ('ASPJ064841-174828',), 3638, 520, debug=False)
#
#    add_drp_source('PKS 1004-217', 151.6933900, -21.9890028, 'Blazar',
#                   ('ASPJ100711-220018',), 3540, 506, debug=False)
#
#    add_drp_source('PKS 0346-27', 57.1589354, -27.8204344, 'Blazar',
#                   ('ASPJ034550-271339',), 3510, 502, debug=False)
#
#    add_drp_source('OT 355', 263.5857438, 38.9642894, 'Blazar',
#                   ('ASPJ173353+385306',), 3508, 502, debug=False)
#
#    add_drp_source('TXS 0552+398', 88.8783567, 39.8136569, 'Blazar',
#                   ('ASPJ055531+392514',), 3482, 498, debug=False)
#
#    add_drp_source('PMN J0852-5755', 133.161250, -57.925056, 'Blazar',
#                   ('ASPJ085233-575310',), 3460, 494, debug=False)
#
#    add_drp_source('GB6 J0713+5738', 108.268946, 57.636144, 'Blazar',
#                   ('ASPJ071252+574410',), 3458, 494, debug=False)
#
#    add_drp_source('OK +630', 140.4009629, 62.2644944, 'Blazar',
#                   ('ASPJ092046+630233',), 3452, 493, debug=False)
#
#    add_drp_source('PKS 0131-522', 23.2740104, -52.0010961, 'Blazar',
#                   ('ASPJ012907-523429',), 3433, 491, debug=False)
#
#    add_drp_source('PKS 2144+092', 326.7923454, 9.4962978, 'Blazar',
#                   ('ASPJ214755+093302',), 3395, 486, debug=False)
#
#    add_drp_source('PKS 0537-286', 84.9761725, -28.6655406, 'Blazar',
#                   ('ASPJ054023-283332',), 3237, 463, debug=False)
#
#    add_drp_source('PKS 0438-43', 70.0715829, -43.5523894, 'Blazar',
#                   ('ASPJ044129-434613',), 3092, 442, debug=False)
#
#    add_drp_source('ASASSN-16ma', 275.21716667, -28.37041667, 'Other_FSP',
#                   (), 3059, 438, debug=False)
#
#    add_drp_source('OT 081', 267.8867437, 9.6502022, 'Blazar',
#                   ('ASPJ175136+093234',), 2937, 420, debug=False)
#
#    add_drp_source('Cygnus X-3', 308.107417, 40.957750, 'MQ',
#                   ('ASPJ202841+411212',), 3005, 430, debug=False)
#
#    add_drp_source('B2 0748+33', 117.9736383, 33.2221719, 'Blazar',
#                   ('ASPJ075117+332902',), 3022, 432, debug=False)
#
#    add_drp_source('PKS 2247-131', 342.4983854, -12.8546736, 'Blazar',
#                   ('ASPJ224701-125854',), 2956, 423, debug=False)
#
#    add_drp_source('PKS 0403-13', 61.3916804, -13.1371364, 'Blazar',
#                   ('ASPJ040645-131514',), 2939, 420, debug=False)
#
#    add_drp_source('PG 1553+113', 238.9293500, 11.1901014, 'Blazar',
#                   ('ASPJ155600+105821',), 2876, 411, debug=False)
#
#    add_drp_source('AP Lib', 229.4242212, -24.3720764, 'Blazar',
#                   ('ASPJ151523-243321',), 2876, 411, debug=False)
#
#    add_drp_source('S4 1800+44', 270.3846454, 44.0727500, 'Blazar',
#                   ('ASPJ180010+441055',), 2818, 403, debug=False)
#
#    add_drp_source('TXS 2358+209', 0.384875, 21.226739, 'Blazar',
#                   (), 2782, 398, debug=False)
#
#    add_drp_source('S5 2007+77', 301.3788744, 77.8786491, 'Blazar',
#                   ('ASPJ200514+774757',), 2780, 398, debug=False)
#
#    add_drp_source('PKS 0514-459', 78.938767, -45.945369, 'Blazar',
#                   ('ASPJ051426-462653',), 2771, 397, debug=False)
#
#    add_drp_source('PKS 1313-333', 199.0332746, -33.6497697, 'Blazar',
#                   ('BM_PKS1313m333',), 2756, 394, debug=False)
#
#    add_drp_source('TXS 1923+123', 291.4200708, 12.4605797, 'Blazar',
#                   ('ASPJ192639+120051',), 2745, 393, debug=False)
#
#    add_drp_source('B2 1846+32B', 282.1431713, 32.7333719, 'Blazar',
#                   ('ASPJ184905+321247',), 2704, 387, debug=False)
#
#    add_drp_source('PKS 1954-388', 299.4992467, -38.7517656, 'Blazar',
#                   ('ASPJ195803-384157',), 2640, 378, debug=False)
#
#    add_drp_source('PKS 0903-57', 136.2215792, -57.5849397, 'Blazar',
#                   ('ASPJ090409-574111',), 2554, 366, debug=False)
#
#    add_drp_source('ON 246', 187.5587054, 25.3019822, 'Blazar',
#                   ('ASPJ122908+251127',), 2536, 363, debug=False)
#
#    add_drp_source('PKS 2032+107', 308.8430554, 10.9352192, 'Blazar',
#                   ('ASPJ203523+110815',), 2497, 357, debug=False)
#
#    add_drp_source('3C 120', 68.2962313, 5.3543389, 'Blazar',
#                   ('ASPJ043144+050410',), 2283, 327, debug=False)
#
#    add_drp_source('PKS B2258-022', 345.2832433, -1.9679403, 'Blazar',
#                   ('ASPJ230219-022137',), 2493, 357, debug=False)
#
#    add_drp_source('PKS 0130-17', 23.1811975, -16.9134783, 'Blazar',
#                   ('ASPJ013231-165023',), 2483, 355, debug=False)
#
#    add_drp_source('TXS 2241+406', 341.0530463, 40.9537836, 'Blazar',
#                   ('ASPJ224406+410733',), 2433, 348, debug=False)
#
#    add_drp_source('B2 1504+37', 226.5397079, 37.5142033, 'Blazar',
#                   ('ASPJ150422+372727',), 2345, 336, debug=False)
#
#    add_drp_source('PKS 0736+01', 114.8251408, 1.6179497, 'Blazar',
#                   ('ASPJ073929+014347',), 2340, 335, debug=False)
#
#    add_drp_source('S4 0954+65', 149.6968546, 65.5652272, 'Blazar',
#                   ('BM_S40954p65',), 2335, 334, debug=False)
#
#    add_drp_source('PKS 1824-582', 277.3016763, -58.2319892, 'Blazar',
#                   ('ASPJ182858-581022',), 2117, 303, debug=False)
#
#    add_drp_source('PKS B1908-201', 287.7902200, -20.1153078, 'Blazar',
#                   ('ASPJ191117-201949',), 2301, 329, debug=False)
#
#    add_drp_source('PKS 0336-01', 54.8789071, -1.7766119, 'Blazar',
#                   ('BM_PKS0336m01',), 2300, 329, debug=False)
#
#    add_drp_source('Fermi J2007-2518', 302.371, -25.411, 'Blazar',
#                   ('ASPJ200831-260239',), 2288, 328, debug=False)
#
#    add_drp_source('PKS 0502+049', 76.3466029, 4.9952014, 'Blazar',
#                   ('ASPJ050626+045814', ), 2250, 322, debug=False)
#
#    add_drp_source('OP 313', 197.6194325, 32.3454953, 'Blazar',
#                   ('ASPJ130853+323648',), 2118, 303, debug=False)
#
#    add_drp_source('B2 1144+40', 176.7429079, 39.9761956, 'Blazar',
#                   ('ASPJ114704+395823',), 2080, 298, debug=False)
#    
#    add_drp_source('4C +01.28', 164.6233550, 1.5663400, 'Blazar',
#                   ('ASPJ105835+011335',), 2065, 296, debug=False)
#
#    add_drp_source('4C +50.11', 59.8739467, 50.9639336, 'Blazar',
#                   ('ASPJ040117+501710',), 2045, 293, debug=False)
#                   
#    add_drp_source('S5 1044+71', 162.1150829, 71.7266494, 'Blazar',
#                   ('ASPJ104816+713958',), 2033, 291, debug=False)
#                   
#    add_drp_source('PKS 2136-642', 325.003500, -64.026389, 'Blazar',
#                   ('ASPJ213832-641920',), 2008, 287, debug=False)
#
#    add_drp_source('1ES 2322-409', 351.186125, -40.680361, 'Blazar',
#                   ('ASPJ232100-401500',), 1931, 277, debug=False)
#    
#    add_drp_source('VER 0521+211', 80.4415242, 21.2142919, 'Blazar',
#                   ('ASPJ052148+211658',), 1938, 278, debug=False)
#
#    add_drp_source('4C +01.02', 17.1615458, 1.5834214, 'Blazar',
#                   ('ASPJ010700+021500',), 1908, 273, debug=False)
#    
#    add_drp_source('1H 0323+342', 51.1715054, 34.1794044, 'Blazar',
#                   ('ASPJ032529+335254',), 1891, 271, debug=False)
#    
#    add_drp_source('PKS 0920-39', 140.6934092, -39.9930739, 'Blazar',
#                   ('ASPJ092132-395302',), 1886, 270, debug=False)
#    
#    add_drp_source('PMN J0017-0512', 4.3992383, -5.2116019, 'Blazar',
#                   ('ASPJ001750-051806',), 1796, 257, debug=False)
#
#    add_drp_source('PKS 2320-035', 350.8831404, -3.2847286, 'Blazar',
#                   ('ASPJ232327-033931',), 1766, 253, debug=False)
#    
#    add_drp_source('PKS 0507+17', 77.5098713, 18.0115506, 'Blazar',
#                   ('ASPJ050833+173640',), 1762, 252, debug=False)
#    
#    add_drp_source('NGC 1275', 49.9506671, 41.5116961, 'Blazar',
#                   ('ASPJ031821+413814',), 1671, 239, debug=False)
#    
#    add_drp_source('PKS 2149-306', 327.9813496, -30.4649158, 'Blazar',
#                   ('ASPJ214718-303659',), 1655, 237, debug=False)
#
#    add_drp_source('PKS 0250-225', 43.1998067, -22.3237403, 'Blazar',
#                   ('ASPJ025259-221459',), 1603, 229, debug=False)
#
#    add_drp_source('PKS 1451-375', 223.6142071, -37.7925400, 'Blazar',
#                   ('ASPJ145626-374211',), 1589, 227, debug=False)
#    
#    add_drp_source('PKS 2255-282', 344.524875, -27.972556, 'Blazar',
#                   ('ASPJ225745-274417',), 1342, 192, debug=False)
#
#    add_drp_source('PKS 0458-02', 75.3033742, -1.9872931, 'Blazar',
#                   ('ASPJ050059-015955',), 1545, 221, debug=False)
#    
#    add_drp_source('S3 0218+35', 35.2727921, 35.9371450, 'Blazar',
#                   ('ASPJ022041+355108',), 1524, 218, debug=False)
#
#    add_drp_source('PMN J1626-2426', 246.7500417, -24.4445833, 'Blazar',
#                   ('ASPJ162447-243039',), 1517, 217, debug=False)
#    
#    add_drp_source('NRAO 676', 330.4314050, 50.8156633, 'Blazar',
#                   ('ASPJ220127+495804',), 1453, 208, debug=False)
#    
#    add_drp_source('PKS 2233-148', 339.1420296, -14.5561633, 'Blazar',
#                   ('ASPJ223605-143814',), 1441, 207, debug=False)
#
#    add_drp_source('PMN J1038-5311', 159.669000, -53.195250, 'Blazar',
#                   ('ASPJ104139-532807',), 1351, 193, debug=False)
#
#    add_drp_source('PKS 1346-112', 207.3810133, -11.5482858, 'Blazar',
#                   ('ASPJ134924-113145',), 1249, 179, debug=False)
#
#    add_drp_source('Fermi J1717-5156', 259.3945, -51.9255, 'Blazar',
#                   ('ASPJ171857-515956',), 1383, 198, debug=False)
#
#    add_drp_source('PKS 2123-463', 321.6279342, -46.0966367, 'Blazar',
#                   ('ASPJ212656-460503',), 1268, 181, debug=True)
#
#    add_drp_source('OG 050', 83.1624933, 7.5453736, 'Blazar',
#                   ('ASPJ053248+073357',), 1231, 176, debug=True)
#
#    add_drp_source('3C 446', 336.4469133, -4.9503861, 'Blazar',
#                   ('ASPJ222508-041457',), 1201, 172, debug=True)
#
#    add_drp_source('4C +28.07', 39.4683567, 28.8024972, 'Blazar',
#                   ('BM_4C28_07',), 1196, 171, debug=True)
#
#    add_drp_source('FERMI J1532-1321 (ATel #3579)', 233.16, -13.35, 'Blazar',
#                   ('ASPJ153115-124324',), 1154, 165, debug=True)
#
#    add_drp_source('MG1 J050533+0415', 76.394892, 4.265172, 'Blazar',
#                   ('ASPJ050626+045814',), 1151, 164, debug=True)
#
#    add_drp_source('CGRaBS J1849+6705', 282.3169679, 67.0949108, 'Blazar',#
#                   ('ASPJ184847+671447',), 1107, 158, debug=True)
#
#    add_drp_source('S5 1803+78', 270.1903496, 78.4677828, 'Blazar',
#                   ('ASPJ180237+782938',), 1042, 149, debug=True)
#
#    add_drp_source('PMN J1123-6417', 170.82833,	-64.29694, 'Blazar',
#                   ('ASPJ112900-634500',), 1070, 153, debug=True)
#
#    add_drp_source('CTA 102', 338.1517038, 11.7308067, 'Blazar',
#                   ('BM_CTA102',), 1039, 149, debug=True)
#
#    add_drp_source('1150+497', 178.3519442, 49.5191194, 'Blazar',
#                   ('ASPJ115243+494115',), 1035, 148, debug=True)
#
#    add_drp_source('S5 0836+71', 130.3515217, 70.8950481, 'Blazar',
#                   ('BM_S50836p71',), 1013, 145, debug=True)
#
#    add_drp_source('PKS 1622-253', 246.4453817, -25.4606461, 'Blazar',
#                   ('ASPJ162447-243039',), 467, 67, debug=True)
#
#    add_drp_source('BZU J0742+5444', 115.6657942, 54.7401850, 'Blazar',
#                   ('ASPJ074034+543435',), 977, 139, debug=True)
#
#    add_drp_source('S4 1749+70', 267.1368337, 70.0974356, 'Blazar',
#                   ('ASPJ174803+700324',), 966, 139, debug=True)
#
#    add_drp_source('CGRaBS J0211+1051', 32.8049054, 10.8596661, 'Blazar',
#                   ('ASPJ020917+105658',), 943, 135, debug=True)
#
#    add_drp_source('B2 2308+34', 347.7722033, 34.4196958, 'Blazar',
#                   ('ASPJ231221+350112',), 774, 111, debug=True)
#
#    add_drp_source('B3 1708+433', 257.4211983, 43.3123742, 'Blazar',
#                   ('ASPJ170941+432215',), 868, 124, debug=True)
#
#    add_drp_source('PMN J1913-3630', 288.3370367, -36.5053831, 'Blazar',
#                   ('ASPJ191334-363742',),  849, 122, debug=True)
#
#    add_drp_source('4C 14.23',111.320032, 14.4204853 , 'Blazar',
#                   ('ASPJ072638+143408',), 476, 69, debug=True)
#
#    add_drp_source('CGRaBS J1848+3219', 282.0920354, 32.3173897, 'Blazar',
#                   ('ASPJ184905+321247',), 846, 121, debug=True)
#
#    add_drp_source('CRATES J0531-4827', 82.994208, -48.459972, 'Blazar',
#                   ('ASPJ053136-482335',), 823, 118, debug=False)
#
#    add_drp_source('PKS 1830-211', 278.4162007, -21.0610479, 'Blazar',
#                   ('ASPJ183235-204445',), 842, 121, debug=False)
#
#    add_drp_source('PKS 0727-11', 112.5796350, -11.6868331, 'Blazar',
#                   ('ASPJ072946-113635',), 819, 117, debug=True)
#
#    add_drp_source('B2 0619+33', 95.7175912, 33.4362250, 'Blazar',
#                   ('ASPJ062303+332557',), 801, 115, debug=True)
#
#    add_drp_source('Ton 599', 179.8826413, 29.2455075, 'Blazar',
#                   ('BM_TON599',), 782, 112, debug=False)
#
#    add_drp_source('PKS 2326-502', 352.3370000, -49.9279667, 'Blazar',
#                   ('ASPJ232500-491500',), 774, 111, debug=False)
#
#    add_drp_source('PMN J0948+0022', 147.2388337, 0.3737661, 'Blazar',
#                   ('ASPJ094824+001628',), 745, 106, debug=False)

#    add_drp_source('PKS 1329-049', 203.0186025, -5.1620292, 'Blazar',
#                   ('ASPJ133200-050651',), 743, 106, debug=False)
#
#    add_drp_source('PKS 0521-36', 80.7416025, -36.4585689, 'Blazar',
#                   ('ASPJ052321-362958',), 723, 103, debug=False)
#
#    add_drp_source('PKS 0235-618', 9.2218571, -61.6042175, 'Blazar',
#                   ('ASPJ023713-614301',), 716, 102, debug=False)

#    add_drp_source('S4 1030+61', 158.4642871, 60.8520372, 'Blazar',
#                   ('ASPJ103430+605012',), 689, 98, debug=False)
#
#    add_drp_source('PKS 0301-243', 45.860409, -24.119731, 'Blazar',
#                   ('ASPJ030306-241940',), 673, 97, debug=False)

#    expose_lightcurves("ASPJ150432+102709", 43, 7)
#    expose_lightcurves("ASPJ150345+102405", 43, 7)
#
#    expose_lightcurves("ASPJ145759-351535", 72, 11)

#    set_pointsourcetype('PKS 1502+106', 'DRP')
#    set_pointsourcetype('PKS 1454-354', 'DRP')

#    add_drp_source('PKS 1424-41', 216.9845729, -42.1053992, 'Blazar',
#                   ('BM_PKS1424m41',), 666, 96, debug=False)

#    add_drp_source('PKS B0906+015', 137.2920479, 1.3598939, 'Blazar',
#                   ('ASPJ090701+012134',), 653, 93, debug=False)
#
#    add_drp_source('PKS 2142-75', 326.8030429, -75.6036736, 'Blazar',
#                   ('ASPJ214347-753227',), 649, 93, debug=False)
#
#    add_drp_source('J1512-3221', 228.04, -32.36, 'Blazar',
#                   ('ASPJ151320-323521',), 643, 92, debug=False)

#    add_drp_source('PKS 0244-470', 41.500000, -46.855111, 'Blazar',
#                   ('ASPJ024605-464526',), 598, 86, debug=False)
#
#    add_drp_source('PMN J2345-1555', 356.3019263, -15.9188428, 'Blazar',
#                   ('ASPJ234439-154712',), 582, 84, debug=False)
#    add_drp_source('PKS 0402-362', 60.9739579, -36.0838644, 'Blazar',
#                   ('ASPJ040213-355246',), 587, 85, debug=False)

#    add_drp_source('PKS 2155-83', 330.582875, -83.637028, 'Blazar',
#                   ('ASPJ220916-840928',), 560, 81, debug=False)
#
#    add_drp_source('OX 169', 325.8981021, 17.7302186, 'Blazar',
#                   ('ASPJ214147+171202',), 573, 82, debug=False)

#    add_drp_source('PKS 0426-380 ',67.1684342, -37.9387719 , 'Blazar',
#                   ('ASPJ042833-374358',), 557, 80, debug=False)
#
#    add_drp_source('PKS B1222+216', 186.2269096, 21.3795522, 'Blazar',
#                   ('BM_4C21_35',), 536, 77, debug=False)

#    add_drp_source('GB6 B1310+4844', 198.1806400, 48.4752611, 'Blazar',
#                   ('ASPJ131152+483428',), 515, 73, debug=False)

#    add_drp_source('B3 1343+451', 206.3882183, 44.8832147, 'Blazar',
#                   ('ASPJ134421+451449',), 457, 66, debug=False)
#    add_drp_source('0FGL J1641.4+3939', 250.355, 39.666, 'Blazar',
#                   ('ASPJ164229+395620',), 457, 66, debug=False)
#

#    add_drp_source('PKS 2023-07', 306.4194183, -7.5979689  , 'Blazar',
#                   ('ASPJ202300-074500',), 425, 61, debug=False)

#    add_drp_source('PKS 0805-07', 122.0647333, -7.8527458 , 'Blazar',
#                   ('ASPJ080630-080403',), 393, 56, debug=False)

#    add_drp_source('PKS 0537-441', 84.7098392, -44.0858150, 'Blazar',
#                   ('BM_PKS0537m441',), 380, 54, debug=False)

#    add_drp_source('3EG J0903-3531', 136.202, -35.256, 'Unid',
#                   ('ASPJ090441-353013',), 376, 53, debug=True)
#
#    add_drp_source('MG2 J071354+1934', 108.4819962, 19.5834467, 'Blazar',
#                   ('ASPJ071352+191747',), 376, 53, debug=True)

#    add_drp_source('J1057-6027', 164.308, -60.458, 'Unid', 
#                   ('ASPJ110300-604500',), 352, 51, debug=True)

#    add_drp_source('4C 31.03', 18.210, 32.138, 'Blazar',
#                   ('ASPJ011242+321036',), 332, 48, debug=True)

#    add_drp_source('0FGL J0910.2-5044', 137.568, -50.743, 'Unid',
#                   ('ASPJ091024-504123',), 332, 48, debug=True)

#    add_drp_source('J123939+044409', 189.9, 4.7, 'Unid', 
#                   ('ASPJ123939+044409',), 332, 48, debug=True)

#    insert_pointsource('0716+714', 110.4727017, 71.3434342, 'Blazar')
#    insert_pointsource('PKS 1502+106', 226.1040821, 10.4942217, 'Blazar')
#    insert_pointsource('PSR J1709-44', 257.4275, -44.4858, 'Pulsar')
#    insert_pointsource('PKS 1454-354', 224.3612988, -35.6527697, 'Blazar')
#    insert_pointsource('J0910-5041', 137.69, -50.74, 'Unid')
#    insert_pointsource('PKS 1244-255', 191.695, -25.797, 'Blazar')
#    insert_pointsource('PKS 0454-234', 74.263, -23.414, 'Blazar')
#    insert_pointsource('GB6 J1700+6830', 255.039, 68.502, 'Blazar')
#    insert_pointsource('PMN J2250-2806', 342.685, -28.110, 'Blazar')
#    insert_pointsource('B2 1520+31', 230.542, 31.737, 'Blazar')
#    insert_pointsource('NRAO 190', 70.661, -0.295, 'Blazar')
#    insert_pointsource('3C 66A', 35.665, 43.035, 'Blazar')

#
#    create_alias('ASPJ091024-504123', 'J0910-5041')
#    create_alias('ASPJ124720-254136', 'PKS 1244-255')
#    create_alias('ASPJ045715-231518', 'PKS 0454-234')
#    create_alias('ASPJ170102+681704', 'GB6 J1700+6830')
#    create_alias('ASPJ225233-273852', 'PMN J2250-2806')
#    create_alias('ASPJ152111+314420', 'B2 1520+31')    
#    create_alias('BM_PKS0440m00', 'NRAO 190')
#    create_alias('BM_3C66A', '3C 66A')

#    set_pointsourcetype('J0910-5041', 'DRP')
#    set_pointsourcetype('PKS 1244-255', 'DRP')
#    set_pointsourcetype('PKS 0454-234', 'DRP')
#    set_pointsourcetype('GB6 J1700+6830', 'DRP')
#    set_pointsourcetype('PMN J2250-2806', 'DRP')
#    set_pointsourcetype('B2 1520+31', 'DRP')
#    set_pointsourcetype('NRAO 190', 'DRP')
#    set_pointsourcetype('3C 66A', 'DRP')

#    update_pointsourcetype('ASPJ091024-504123', 'ATEL')
#    update_pointsourcetype('ASPJ124720-254136', 'ATEL')
#    update_pointsourcetype('ASPJ045715-231518', 'ATEL')
#    update_pointsourcetype('ASPJ170102+681704', 'ATEL')
#    update_pointsourcetype('ASPJ225233-273852', 'ATEL')
#    update_pointsourcetype('ASPJ152111+314420', 'ATEL')
#    update_pointsourcetype('BM_PKS0440m00', 'ATEL')
#    update_pointsourcetype('ASPJ150432+102709', 'ATEL')
#    update_pointsourcetype('ASPJ150345+102405', 'ATEL')
#    update_pointsourcetype('ASPJ145759-351535', 'ATEL')
#    update_pointsourcetype('BM_3C66A', 'ATEL')

#    new_sources = ('ASPJ091024-504123', 
#                   'ASPJ045715-231518', 
#                   'ASPJ124720-254136', 
#                   'ASPJ170102+681704', 
#                   'ASPJ225233-273852', 
#                   'ASPJ152111+314420', 
#                   'BM_PKS0440m00',
#                   'ASPJ150432+102709', 
#                   'ASPJ150345+102405', 
#                   'ASPJ145759-351535',
#                   'BM_3C66A')
#
#    aliases = ('PKS 1502+106',
#               'PKS 1454-354',
#               'J0910-5041',
#               'PKS 1244-255',
#               'PKS 0454-234',
#               'GB6 J1700+6830',
#               'PMN J2250-2806',
#               'B2 1520+31', 
#               'NRAO 190',
#               '3C 66A')
#
#    for item in aliases[-1:]:
#        sql = "update pointsources set is_public=1 where ptsrc_name='%s'" % item
#        print sql
#        databaseAccess.apply(sql)
#
#    for item in new_sources[-1:]:
#        sql = ("update lightcurves set is_monitored=1 where " +
#               "ptsrc_name='%s' " % item + 
#               "and ((interval_number<330 and frequency='daily') " + 
#               "or (interval_number<48 and frequency='weekly'))")
#        print sql
#        databaseAccess.apply(sql)
