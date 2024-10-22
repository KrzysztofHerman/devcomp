
#
import pandas as pd
import matplotlib.pyplot as plt
import sys

# Function to read data from CSV and plot in semilogx and semilogy
def plot_data(csv_file):
    # Load the CSV data into a pandas DataFrame (assuming no header)
    data = pd.read_csv(csv_file, sep=' ', header=None)
    # Plot semilogx (logarithmic x-axis)
    plt.figure()
    plt.loglog(data.iloc[:,0], data.iloc[:,1])
    plt.title('Semilogx Plot (Logarithmic X-Axis)')
    plt.xlabel('X (Log Scale)')
    plt.ylabel('Y')
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    # Check if a filename is passed as an argument
    if len(sys.argv) != 2:
        print("Usage: python script.py <csv_filename>")
        sys.exit(1)

    # Get the filename from command line argument
    csv_file = sys.argv[1]
    
    # Plot the data from the CSV file
    plot_data(csv_file)
