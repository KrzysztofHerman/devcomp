import os
from tqdm import tqdm
from utils import *
from config import *
from simulator import Simulator

SIMULATOR_ARGS = {
    'spectre' : ['+escchars', 
                '=log', 
                './sweep/psf/spectre.out', 
                '-format', 
                'psfascii', 
                '-raw', 
                './sweep/psf'],

    'ngspice' : ['-b']
}


def csum(a, b):
    return a + b


def devcomp():
    print("Hello")


def main():
#conf=Config('sc.cfg')
   swp=Sweep('sc.cfg')
   swp.run()

class Sweep:
    def __init__(self, config_file_path: str):
        self._config = Config(config_file_path)
        simulator = self._config['SETTINGS']['SIMULATOR']
        self._simulator = Simulator(simulator, SIMULATOR_ARGS[simulator])
        
    def run(self):
        
        Ws = self._config['SWEEP']['WIDTH']
        Ls = self._config['SWEEP']['LENGTH']
        Ngs = self._config['SWEEP']['NFING']

        for i, WIDTH in enumerate(tqdm(Ws,desc="Sweeping W")):
            for j, L in enumerate(tqdm(Ls, desc="Sweeping L", leave=False)):
                for k, NFING in enumerate(tqdm(Ngs, desc="Sweeping Ng", leave=False)):
                    print(f' W {i} L {j}  Ng {k}')
                    self._write_params(width = WIDTH, length=L, ngates=NFING)
 
                    sim_path = f"./sweep/psf_{i}_{j}_{k}"
                    self._simulator.directory = sim_path
                    simulator = self._simulator.simulator
                    # !TODO necessary to change extension?
                    if simulator == 'spectre':
                        cp = self._simulator.run('pysweep.scs')
                    elif simulator == 'ngspice':
                        if not os.path.exists(sim_path):
                            os.makedirs(sim_path)
                        cp = self._simulator.run('./../../pysweep.spice', **{'cwd' : sim_path})


    def _write_params(self, width=1, length=1, ngates=1):
        if self._simulator.simulator == 'spectre':
            ext = 'scs'
            with open(f'params.{ext}', 'w') as outfile:
                outfile.write(f"parameters width={width}")
        elif self._simulator.simulator == 'ngspice':
            paramfile = self._config['MODEL']['PARAMFILE']
            with open(f'{paramfile}', 'w') as outfile:
                outfile.write(f'XM1 drain_n gate_n GND bulk_n sg13_lv_nmos W={width*10e-6} L={length*10e-6} ng={int(ngates)} m=1')


if __name__ == "__main__":
    main()
