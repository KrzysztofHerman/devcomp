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
            try:
                mn_supplement = '\n\t'.join(json.loads(self._config['MODEL']['MN']))
            except json.decoder.JSONDecodeError:
                raise "Error parsing config: make sure MN has no weird characters in it, and that the list isn't terminated with a trailing ','"
            try:
                mp_supplement = '\n\t'.join(json.loads(self._config['MODEL']['MP']))
            except json.decoder.JSONDecodeError:
                raise "Error parsing config: make sure MP has no weird characters in it, and that the list isn't terminated with a trailing ','"
            
            netlist = [
                f"//pysweep.spice",
                f"include {modelfile}",
                f'include "{paramfile}"\n',   
                f'save mn:oppoint',  
                f'save mp:oppoint',
                f'\n',
                f'parameters gs=0.498 ds=0.2 L=length*1e-6 Wtot={width}e-6 W=500n',
                f'\n',
                f'vnoi     (vx  0)         vsource dc=0',  
                f'vdsn     (vdn vx)         vsource dc=ds',   
                f'vgsn     (vgn 0)         vsource dc=gs',   
                f'vbsn     (vbn 0)         vsource dc=-sb',  
                f'vdsp     (vdp vx)         vsource dc=-ds',  
                f'vgsp     (vgp 0)         vsource dc=-gs',  
                f'vbsp     (vbp 0)         vsource dc=sb',  
                f'\n',	 
                f'\n',	 
                f'mp (vdp vgp 0 vbp) {modelp} {mp_supplement}',
                f'\n',	 
                f'mn (vdn vgn 0 vbn) {modeln} {mn_supplement}',
                f'\n',	 
                f'simulatorOptions options gmin=1e-13 reltol=1e-4 vabstol=1e-6 iabstol=1e-10 temp={temp} tnom=27',  
                f'sweepvds sweep param=ds start=0 stop={VDS_max} step={VDS_step} {{',  
                f'sweepvgs dc param=gs start=0 stop={VGS_max} step={VGS_step}',  
                f'}}', 
                f'sweepvds_noise sweep param=ds start=0 stop={VDS_max} step={VDS_step} {{', 
                f'	sweepvgs_noise noise freq=1 oprobe=vnoi param=gs start=0 stop={VGS_max} step={VGS_step}', 
                f'}}'
                ]
            netlist[3:3] = eval(additional_settings)
        elif simulator == 'ngspice':
            netlist = [
                f"*//pysweep.spice",
                f"******* generated circuit ************ ",
                f'\n',
                f'\n',
                f'Vgs_n      gate_n     GND         {Vgs}',
                f'Vds_n      drain_n    GND         {Vds}',
                f'Vb_n       bulk_n     GND         {-Vsb}',
                f'\n',
                f'\n',
                f'.param temp={temp}',
                f'\n',
                f".include ./{paramfile}",
                f'\n',
                f".lib {modelfile}",
                f'.control',
                f'*---- NMOS',
                f'pre_osdi ./psp103_nqs.osdi',
                f'op',
                f'show all > op_point.out',
                f'.endc',
                f'.GLOBAL GND',
                f'.end',
            ]
        #       netlist[-9:-9] = eval(additional_settings)
        with open('pysweep.spice', 'w') as outfile:
            outfile.write('\n'.join(netlist))
