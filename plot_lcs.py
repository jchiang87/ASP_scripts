import astropy.io.fits as fits
import pylab_plotter as plot
plot.pylab.ion()

foo = fits.open('pulsar_lcs.fits')

#source = 'ASPJ183900-054500'
source = 'ASPJ202124+365447'
#source = 'Crab Pulsar'
#source = 'Geminga'

time = (foo[source].data.field('START') + foo[source].data.field('STOP'))/2.
flux = foo[source].data.field('FLUX')
error = foo[source].data.field('ERROR')

win = plot.xyplot(time, flux, yerr=error, xname='time (MET)', yname='flux')
win.set_title(source)
try:
    plot.pylab.annotate('PSR association: %s'%foo[source].header['PSRASSOC'],
                        (0.55, 0.95), xycoords='axes fraction', size='small')
except KeyError:
    pass
