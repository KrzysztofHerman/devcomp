
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

# Function to read and aggregate data from CSVs in a directory structure
def aggregate_data(root_dir, csv_file):
    all_data = []
    
    # Walk through the directory structure
    for subdir, _, files in os.walk(root_dir):
        if csv_file in files:
            # Construct full file path
            file_path = os.path.join(subdir, csv_file)
            
            # Load the CSV data with space as the separator (assuming no header)
            data = pd.read_csv(file_path, sep=' ', header=None)
            #           print(data.iloc[:10])  # Print first 10 rows of the file
            if not data.empty:
                all_data.append(data)
                # Append a row of NaNs to separate datasets
                all_data.append(pd.DataFrame([[float('nan'), float('nan')]], columns=[1, 3]))

    
    # Combine all data into a single DataFrame
    if all_data:
        combined_data = pd.concat(all_data, ignore_index=True)
        return combined_data
    else:
        print("No CSV files found.")
        sys.exit(1)

# Function to plot the combined data
def plot_combined_data(combined_data):
    # Plot semilogx (logarithmic x-axis) for the combined data
    plt.figure()
    plt.loglog(combined_data.iloc[:, 1], combined_data.iloc[:, 3],label='Combined Data')  # Column 0 for X, 1 for Y
    plt.title('NGspice output voltage noise simulation W <1u:1u:10u>, L=0.5u, Ng=<1:4> ')
    plt.xlabel('frequency [Hz]')
    plt.ylabel('Noise PSD V^2/Hz')
    plt.grid(True)
    plt.savefig('ngspice.png')
    plt.show()

# Function to save the combined data to a file
def save_combined_data(combined_data, output_file):
    # Save the combined data to a CSV file
    combined_data.to_csv(output_file, sep=' ', index=False, header=False)
    print(f"Combined data saved to {output_file}")

if __name__ == "__main__":
    # Check if root directory and CSV filename are passed as arguments
    if len(sys.argv) != 3:
        print("Usage: python script.py <root_directory> <csv_filename>")
        sys.exit(1)

    # Get the root directory and csv filename from the command line arguments
    root_dir = sys.argv[1]
    csv_file = sys.argv[2]

    # Aggregate the data from all directories
    combined_data = aggregate_data(root_dir, csv_file)
    fname  = root_dir + 'combined.csv'
    save_combined_data(combined_data, fname)
    # Plot the combined data
    plot_combined_data(combined_data)
