import numpy as np
import json
import ast
import configparser

def matrange(start, step, stop):
    num = round((stop - start) / step + 1)
    
    return np.linspace(start, stop, num)

def toupper(option):
    return option.upper()

class Config:
    def __init__(self, config_file_path: str):
        self._configParser = configparser.ConfigParser()	
        self._configParser.optionxform = toupper
        self._configParser.read(config_file_path)
        self._config = {s:dict(self._configParser.items(s)) for s in self._configParser.sections()}
        self._parse_ranges()
        self._generate_netlist()
        
    def _parse_ranges(self):
        # parse numerical ranges		
        for k in ['VGS', 'VDS', 'VSB', 'LENGTH', 'WIDTH', 'NFING']:
            v = ast.literal_eval(self._config['SWEEP'][k])
            v = [v] if type(v) is not list else v
            v = [matrange(*r) for r in v]
            v = [val for r in v for val in r] 
            self._config['SWEEP'][k] = v
    
            #    for k in ['WIDTH', 'NFING']:
            #self._config['SWEEP'][k] = int(self._config['SWEEP'][k])
    def __getitem__(self, key):
        if key not in self._config.keys():
            raise ValueError(f"Lookup table does not contain this data")
    
        return self._config[key]
         
    def generate_m_dict(self):
        return {
            'INFO' : self._config['MODEL']['INFO'],
            'CORNER' : self._config['MODEL']['CORNER'],
            'TEMP' : self._config['MODEL']['TEMP'],
            'NFING' : self._config['SWEEP']['NFING'],
            'L' : np.array(self._config['SWEEP']['LENGTH']).T,
            'W' : self._config['SWEEP']['WIDTH'],
            'VGS' : np.array(self._config['SWEEP']['VGS']).T,
            'VDS' : np.array(self._config['SWEEP']['VDS']).T,
            'VSB' : np.array(self._config['SWEEP']['VSB']).T 
        }
        
    def _generate_netlist(self):
        modelfile = self._config['MODEL']['FILE']
        corner = self._config['MODEL']['CORNER']
        paramfile = self._config['MODEL']['PARAMFILE']
        width = self._config['SWEEP']['WIDTH']
        modelp = self._config['MODEL']['MODELP']
        modeln = self._config['MODEL']['MODELN']
        simulator = self._config.get('SETTINGS', 'spectre').get('SIMULATOR', 'spectre')
        # parse additional settings
        additional_settings = self._config.get('SETTINGS', []).get('RAW_INCLUDE', [])
        temp =int(self._config['MODEL']['TEMP'])-273
        VDS_max = max(self._config['SWEEP']['VDS'])
        VDS_step = self._config['SWEEP']['VDS'][1] - self._config['SWEEP']['VDS'][0] 
        VGS_max = max(self._config['SWEEP']['VGS'])
        VGS_step = self._config['SWEEP']['VGS'][1] - self._config['SWEEP']['VGS'][0]
        Vgs = VGS_max
        Vds = VDS_max
        Vsb = self._config['SWEEP']['VSB'][0]
        NFING = self._config['SWEEP']['NFING']
     
     
        if simulator == "spectre":
            
            netlist = [
                f"//pysweep.scs",
		f' simulator lang=spectre',
		f' global 0',
                 f' include "{modelfile}" section = {corner}',
		f'\n',
                f' include "{paramfile}" ',
		f'\n',
                f'PORT1 (in 0) port r=50 num=1 dc=0 type=sine ampl=632.456m freq=1M',
                f'PORT2 (out 0) port r=50 num=2 dc=0 type=sine ampl=6.32456u freq=1M',
                f'V1 (net10 0) vsource dc={Vds} type=dc',
                f'V0 (net11 0) vsource dc={Vgs} type=dc',
     
                f'C2 (in gate_n) capacitor c=1m',
                f'C0 (drain_n out) capacitor c=1m',
                f'L0 (gate_n net11) inductor l=1m',
                f'L1 (drain_n net10) inductor l=1m',
                f'Vb_n       (source_n      GND) vsource    dc=0',
                f'Vs_n       (bulk_n        GND) vsource    dc=0',
		f'\n',
                f' simulatorOptions options psfversion="1.1.0" reltol=1e-3 vabstol=1e-6 \ ',
                f' iabstol=1e-12 temp=27 tnom=27 scalem=1.0 scale=1.0 gmin=1e-12 rforce=1 \ ',
                f' maxnotes=5 maxwarns=5 digits=5 cols=80 pivrel=1e-3 \ ',
                f' sensfile="../psf/sens.output" checklimitdest=psf ignorezerovar=yes ',
		f'\n',
                f'sp sp ports=[PORT1 PORT2] start=100M stop=65G log=200 donoise=yes \ ',
                f'           oprobe=PORT2 iprobe=PORT1 annotate=status ',
		f' saveOptions options save=allpub currents=all subcktprobelvl=5 saveahdlvars=all',
                f'\n',
                ]
            with open('pysweep.scs', 'w') as outfile:
                outfile.write('\n'.join(netlist))
       
        elif simulator == 'ngspice':
            netlist = [
                f"*//pysweep.spice",
                f"******* generated circuit ************ ",
                f'\n',
                f'\n',
                f'I1         0          drain_n    DC  1m',
                f'Vdg_n      drain_n    gate_n     DC   0',
                f'Vsb_n      source_n   bulk_n     DC   0',
                f'V1         bulk_n     GND    DC 0 SIN(0 1 1K 0 0 0) AC 1 ACPHASE 0',
                f'\n',
                f'\n',
                f'.param temp={temp}',
                f'\n',
                f".include ./{paramfile}",
                f'\n',
                f".lib {modelfile} {corner}",
                f'.control',
                f'*---- NMOS',
                f'noise v(drain_n) V1 dec 101 1MEG 10G',
                f'setplot noise1',
                f'wrdata onoise.csv onoise_spectrum',
                f'.endc',
                f'.GLOBAL GND',
                f'.end',
            ]
        #       netlist[-9:-9] = eval(additional_settings)
            with open('pysweep.spice', 'w') as outfile:
                outfile.write('\n'.join(netlist))
