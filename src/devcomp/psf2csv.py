
from psf_utils import PSF
from inform import Error, display
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

# Function to read and aggregate data from .noise in a directory structure
def aggregate_data(root_dir, csv_file):
    
    # Walk through the directory structure
    for subdir, _, files in os.walk(root_dir):
        print(files)
        print(subdir)
        if csv_file in files:
                
            file_path = os.path.join(subdir, csv_file)
            print(file_path)
            try:
               psf = PSF(file_path)
               sweep = psf.get_sweep()
               NF = psf.get_signal('NF')
               NFmin = psf.get_signal('NFmin')
               RN = psf.get_signal('RN')
               df = pd.DataFrame({
               'freq': sweep.abscissa,
               'NF': NF.ordinate, 
               'NFmin': NFmin.ordinate, 
               'RN': RN.ordinate 
               })
               fname_csv = file_path + '.csv'
               df.to_csv(fname_csv, sep=',', index=False, header=False)
            except Error as e:
               e.terminate()
   
    else:
        print("No .noise files found.")
        sys.exit(1)


if __name__ == "__main__":
    # Check if root directory and CSV filename are passed as arguments
    if len(sys.argv) != 3:
        print("Usage: python script.py <root_directory> <noise_filename>")
        sys.exit(1)

    # Get the root directory and csv filename from the command line arguments
    root_dir = sys.argv[1]
    noise_file = sys.argv[2]

    # Aggregate the data from all directories
    aggregate_data(root_dir, noise_file)
    





