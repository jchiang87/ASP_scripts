"""
@brief Collate the PGWAVE and DRP_monitoring data for all of the
sources in the POINTSOURCES database table.

@author J. Chiang
"""
#
# $Header$
#

import bisect
import celgal
import databaseAccess as dbAccess

converter = celgal.celgal()
durations = {'six_hours' : 6*3600, 
             'daily' : 86400, 
             'weekly' : 7*86400}
t0 = {'six_hours' : 236023200, 
      'daily' : 235958400, 
      'weekly' : 235440000}

def tstart(interval_number, frequency):
    my_tstart = interval_number*durations[frequency] + t0[frequency]
    return my_tstart

def interval_number(tstart, tstop):
    my_durations = (6*3600, 86400, 7*86400)
    my_t0 = (236023200, 235958400, 235440000)
    frequencies = ('six_hours', 'daily', 'weekly')

    dt = tstop - tstart
    indx = bisect.bisect_left(my_durations, dt)

    return int((tstart - my_t0[indx])/my_durations[indx]), frequencies[indx]

class FlareEvent(object):
    def __init__(self, starttime, endtime, flux, fluxerr):
        self.starttime = starttime
        self.endtime = endtime
        self.pgwflux = flux
        self.pgwfluxerr = fluxerr
        self.drp_data = None
    def add_DRP_info(self, flux, fluxerr, TS, index, indexerr, is_upper_limit):
        self.drp_data =  flux, fluxerr, TS, index, indexerr, is_upper_limit
    def __str__(self):
        my_string = "%10i  %10i  " % (self.starttime, self.endtime)
        if self.pgwflux is None:
            my_string += "...  ...  "
        else:
            my_string += "%12.4e  %12.4e  " % (self.pgwflux, self.pgwfluxerr)
        if self.drp_data is None:
            my_string += "...  "*6
        elif self.drp_data[3] is None:
            my_string += ("%12.4e  %12.4e  %12.4e  ...  ...  %s" 
                          % (self.drp_data[:3] + self.drp_data[5:]))
        else:
            my_string += ("%12.4e  %12.4e  %12.4e  %8.3f  %8.3f  %s" 
                          % self.drp_data)
        return my_string

class LightCurve(object):
    def __init__(self, frequency, srcname):
        if frequency not in ('six_hours', 'daily', 'weekly'):
            raise RuntimeError("invalid frequency: %s" % frequency)
        self.freq = frequency
        self._query_pgw_data(srcname)
        self._query_drp_data(srcname)
    def _query_pgw_data(self, srcname):
        sql = """select starttime, endtime, flux, flux_err from flareevents
                 where ptsrc_name='%s'""" % srcname
        self.flareEvents = dbAccess.apply(sql, self._flareEvents)
    def _flareEvents(self, curs):
        events = {}
        for entry in curs:
            interval, freq = interval_number(*entry[:2])
            if freq == self.freq:
                events[entry[0]] = FlareEvent(*entry)
        return events
    def _drpEvents(self, curs):
        for entry in curs:
            interval_number = entry[0]
            t0 = tstart(interval_number, self.freq)
            try:
                self.flareEvents[t0].add_DRP_info(*entry[1:])
            except KeyError:
                self.flareEvents[t0] = FlareEvent(t0, t0 + durations[self.freq],
                                                  None, None)
                self.flareEvents[t0].add_DRP_info(*entry[1:])
                
    def _query_drp_data(self, srcname):
        sql = """select interval_number, flux, error, test_statistic, 
                 spectral_index, spectral_index_error, is_upper_limit
                 from lightcurves where ptsrc_name='%s' 
                 and frequency='%s'""" % (srcname, self.freq)
        dbAccess.apply(sql, self._drpEvents)
    def write_data(self, prefix, output):
        times = self.flareEvents.keys()
        times.sort()
        for t0 in times:
            output.write("%s  %s\n" % (prefix, self.flareEvents[t0]))

class Source(object):
    def __init__(self, name, ra, dec):
        self.name = name
        self.ra = ra
        self.dec = dec
        self.l, self.b = converter.gal((self.ra, self.dec))
        self.lcs = {}
    def queryData(self, frequency):
        self.lcs[frequency] = LightCurve(frequency, self.name)
    def __str__(self):
        name = self.name.replace(' ', '_')
        name = name.strip('_')
        return ("%s  %8.3f  %8.3f  %8.3f  %8.3f  " 
                % (name, self.ra, self.dec, self.l, self.b))

def source_list():
    sql = "select ptsrc_name, ra, dec from pointsources"
    def sourceNames(curs):
        my_dict = {}
        for entry in curs:
            my_dict[entry[0]] = Source(*entry)
        return my_dict
    return dbAccess.apply(sql, cursorFunc=sourceNames)

if __name__ == '__main__':
    import sys
    # Loop over source
    #    loop over frequencies
    #        gather pgwave intervals
    #        gather drp intervals
    #        loop over drp intervals
    #            insert drp intervals into corresponding pgwave intervals

    sources = source_list()
    nsrcs = len(sources)

    freq = 'daily'
    output = open('%s_lcs.txt' % freq, 'w')
    for i, name in enumerate(sources.keys()):
        print name, i, nsrcs
        sources[name].queryData(freq)
        sources[name].lcs[freq].write_data("%s" % sources[name], output)
        output.flush()
    output.close()
