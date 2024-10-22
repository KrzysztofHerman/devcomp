import pandas as pd
from psf_utils import PSF
from inform import Error, display
import matplotlib.pyplot as plt



try:
    psf = PSF('sweep/psf_0_0_0/noise.noise')
    sweep = psf.get_sweep()
    out = psf.get_signal('out')
    
    df = pd.DataFrame({
    'freq': sweep.abscissa,
    'noise': out.ordinate**2 })
    
    df.to_csv('sweep/psf_0_0_0/noise.csv', sep=' ', index=False, header=False)

    figure = plt.figure()
    axes = figure.add_subplot(1,1,1)
    axes.loglog(sweep.abscissa, out.ordinate**2, linewidth=2, label=out.name)
    axes.set_title('Noise name')
    axes.set_xlabel(f'{sweep.name} ({PSF.units_to_unicode(sweep.units)})')
    axes.set_ylabel(f'{out.name} ({PSF.units_to_unicode(out.units)})')
    plt.show()
except Error as e:
    e.terminate()
