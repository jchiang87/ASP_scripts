import astropy.io.fits as fits
from collections import OrderedDict
import databaseAccess as dbAccess
import celgal

def fitsRow(tmin, tmax, entry):
    results = [tmin, tmax]
    results.extend(entry)
    return results

class TimeIntervals(object):
    def __init__(self):
        sql = ("select INTERVAL_NUMBER, FREQUENCY, TSTART, TSTOP " + 
               "from TIMEINTERVALS")
        def getIntervals(cursor):
            myData = {'six_hours' : {},
                      'daily' : {},
                      'weekly' : {}}
            for entry in cursor:
                try:
                    myData[entry[1]][entry[0]] = (int(entry[2]), int(entry[3]))
                except KeyError:
                    # Do nothing for non-standard frequencies.
                    pass
            return myData
        self.intervals = dbAccess.apply(sql, getIntervals)
    def __call__(self, freq, interval_num):
        return self.intervals[freq][interval_num]

def find_aspj_sources(radius=0.5, source_type='Pulsar'):
    aspj_sources = OrderedDict()
    r2 = radius**2
    sql = "select ptsrc_name, ra, dec, healpix_id from POINTSOURCES where SOURCE_TYPE='%(source_type)s'" % locals()
    func = lambda curs : OrderedDict([(entry[0], entry[1:]) for entry in curs])
    pulsar_coords = dbAccess.apply(sql, cursorFunc=func)
    for pulsar, coords in pulsar_coords.items():
        ra_psr, dec_psr, healpix_id = coords
        sql = """select ptsrc_name, ra, dec, healpix_id from POINTSOURCES where 
                 ptsrc_name!='%(pulsar)s' and
                 (( (ra-%(ra_psr)f)*(ra-%(ra_psr)f) 
                 + (dec-(%(dec_psr)f))*(dec-(%(dec_psr)f)) ) < %(r2)f or
                 healpix_id=%(healpix_id)s)""" % locals()
        results = dbAccess.apply(sql, cursorFunc=func)
        if results:
            aspj_sources[pulsar] = results
    return aspj_sources

def get_pulsar_names():
    sql = """select ptsrc_name from POINTSOURCES where SOURCE_TYPE='Pulsar'"""
    func = lambda curs : [entry[0] for entry in curs]
    pulsar_names = dbAccess.apply(sql, cursorFunc=func)
    return pulsar_names

def get_pulsar_light_curves(pulsar_names, tmin, tmax, 
                            eband_id=5, frequency='weekly', chatter=2):
    time_intervals = TimeIntervals()

    results = OrderedDict()
    for i, name in enumerate(pulsar_names):
        if chatter > 0:
            print i, name
        eband_query = "lightcurves.eband_id=%i" % eband_id
        sql = """select
                 lightcurves.flux,
                 lightcurves.error,
                 lightcurves.is_upper_limit,
                 lightcurves.test_statistic,
                 lightcurves.frequency,
                 lightcurves.interval_number,
                 lightcurves.eband_id
                 from lightcurves
                 join pointsources on
                 lightcurves.ptsrc_name=pointsources.ptsrc_name
                 where
                 (%(eband_query)s)
                 and
                 lightcurves.frequency='%(frequency)s'
                 and
                 (lightcurves.ptsrc_name='%(name)s' or
                  pointsources.alias='%(name)s')
                 order by lightcurves.frequency asc,
                 lightcurves.interval_number asc,
                 lightcurves.eband_id asc""" % locals()
        if chatter > 2:
            print sql
        func = lambda curs : [entry for entry in curs]
        entries = dbAccess.apply(sql, cursorFunc=func)
        for entry in entries:
            # Time intervals are indexed by frequency and interval_number.
            start, stop = time_intervals(entry[-3], entry[-2])
            if start >= tmax or stop < tmin:
                continue
            if not results.has_key(name):
                results[name] = []
            results[name].append(fitsRow(start, stop, entry))
    return results

def write_fits_file(results, outfile, inverse_index=None, min_points=10):
    output = fits.HDUList()
    output.append(fits.PrimaryHDU())
    for source, values in results.items():
        if len(values) < min_points:
            continue
        colnames = ['START', 'STOP', 'FLUX', 'ERROR', 'UL_FLAG', 'TS']
        formats = ['D', 'D', 'E', 'E', 'I', 'E']
        units = ['s', 's', 'photons/cm**2/s', 'photons/cm**2/s', None, None]
        columns = zip(*values)[:6]
        fits_cols = []
        for colname, format, unit, column in zip(colnames, formats, units,
                                                 columns):
            if unit is not None:
                fits_cols.append(fits.Column(name=colname, format=format,
                                             unit=unit, array=column))
            else:
                fits_cols.append(fits.Column(name=colname, format=format,
                                             array=column))
        output.append(fits.BinTableHDU.from_columns(fits_cols))
        output[-1].name = source
        if inverse_index is not None:
            output[-1].header['PSRASSOC'] = inverse_index[source]
    output.writeto(outfile, clobber=True)

if __name__ == '__main__':
    tmin = 240019201
    tmax = 469929604

    pulsars = get_pulsar_names()
    aspj_sources = find_aspj_sources()
    inverse_index = {}
    for psr, associations in aspj_sources.items():
        pulsars.extend(associations.keys())
        for key in associations.keys():
            inverse_index[key] = psr

    results = get_pulsar_light_curves(pulsars, tmin, tmax)
    write_fits_file(results, 'pulsar_lcs.fits', inverse_index=inverse_index)
