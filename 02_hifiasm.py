import os
import glob
import sys

# --- Define Sample Information ---
# Map of Desired_Name: (Barcode, Full_Sample_Name)
SAMPLES = {
    "WTD_RI": ("bc2001", "WhiteTail_RI"),
    "MD_837": ("bc2065", "Mule_837"),
    "WTD_EL": ("bc2066", "WhiteTail_EL"),
    "WTD_La": ("bc2069", "WhiteTail_Lacoste"),
    "MD_838": ("bc2070", "Mule_838"),
}

# --- Define Paths ---
BASE_PATH = "/home/devan/projects/def-shaferab/devan/Odocoileus_virginianus/sperm/hifi"

DIR_HIFI1 = os.path.join(BASE_PATH, "raw_data", "HiFi_1")
DIR_HIFI2 = os.path.join(BASE_PATH, "raw_data", "HiFi_2")

OUTPUT_DIR = os.path.join(BASE_PATH, "assemblies")
SCRIPT_OUTPUT_DIR = os.path.join(BASE_PATH, "hifiasm_scripts")

# Ensure output directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(SCRIPT_OUTPUT_DIR, exist_ok=True)


BASH_TEMPLATE = """#!/bin/bash
#SBATCH --account=rrg-shaferab
#SBATCH --mem=64G          
#SBATCH --cpus-per-task=24 
#SBATCH --time=23:59:00  
#SBATCH --job-name=hifiasm_{JOB_NAME}
#SBATCH --output={SCRIPT_OUTPUT_DIR}/{JOB_NAME}.out

# Load hifiasm module
module load hifiasm

# --- Configuration (Hardcoded Absolute Paths) ---
SAMPLE_NAME="{SAMPLE_NAME}"
INPUT_FILE1="{INPUT_FILE1}"
INPUT_FILE2="{INPUT_FILE2}"
OUTPUT_DIR="{OUTPUT_DIR}"

# --- Program Execution ---
echo "Starting assembly for $SAMPLE_NAME"
mkdir -p "$OUTPUT_DIR"

echo "Input 1: $INPUT_FILE1"
echo "Input 2: $INPUT_FILE2"

# Run Hifiasm
hifiasm -t 24 -o "$OUTPUT_DIR/{SAMPLE_NAME}.asm" "$INPUT_FILE1" "$INPUT_FILE2"

echo "Hifiasm assembly complete for $SAMPLE_NAME."
"""

# --- Generation Loop ---
print(f"Generating scripts in {SCRIPT_OUTPUT_DIR}...")

for desired_name, (barcode, full_name) in SAMPLES.items():
    # --- Find the exact file paths using glob ---
    # File 1 pattern is based on the barcode appearing twice
    pattern1 = os.path.join(DIR_HIFI1, f"*{barcode}--{barcode}*.fastq.gz")
    matches1 = glob.glob(pattern1)

    # File 2 pattern is based on the sample name (or barcode) appearing once
    # Use the sample name from the HiFi_2 files for maximum safety
    if desired_name == "MD_837":
        # The file in HiFi_2 for MD_837 starts with "Mule_837_bc2065"
        pattern2 = os.path.join(DIR_HIFI2, f"{full_name}_*.fastq.gz")
    elif desired_name == "MD_838":
        # The file in HiFi_2 for MD_838 starts with "Mule_838_bc2070"
        pattern2 = os.path.join(DIR_HIFI2, f"{full_name}_*.fastq.gz")
    else:
        # Use the barcode for other files which all seem to be WhiteTail*
        pattern2 = os.path.join(DIR_HIFI2, f"*{barcode}*.fastq.gz")
        
    matches2 = glob.glob(pattern2)
    
    # Error checking within Python
    if len(matches1) != 1:
        print(f"\nFATAL ERROR: Could not uniquely match Run 1 for {desired_name} ({barcode}). Found {len(matches1)} matches for pattern: {pattern1}")
        print(f"Matches: {matches1}")
        sys.exit(1)
    
    if len(matches2) != 1:
        print(f"\nFATAL ERROR: Could not uniquely match Run 2 for {desired_name} ({barcode}). Found {len(matches2)} matches for pattern: {pattern2}")
        print(f"Matches: {matches2}")
        sys.exit(1)
    
    # Assign the hardcoded paths
    input_file1 = matches1[0]
    input_file2 = matches2[0]

    # --- Generate the script ---
    script_name = f"submit_hifiasm_{desired_name}.sh"
    output_path = os.path.join(SCRIPT_OUTPUT_DIR, script_name)

    formatted_script = BASH_TEMPLATE.format(
        JOB_NAME=desired_name,
        SAMPLE_NAME=desired_name,
        INPUT_FILE1=input_file1,
        INPUT_FILE2=input_file2,
        OUTPUT_DIR=OUTPUT_DIR,
        SCRIPT_OUTPUT_DIR=SCRIPT_OUTPUT_DIR
    )

    # Write the script to file
    with open(output_path, "w") as f:
        f.write(formatted_script)

    os.chmod(output_path, 0o755) # Make it executable

    print(f"  Created: {script_name}.")

print("\nScript generation complete.")
