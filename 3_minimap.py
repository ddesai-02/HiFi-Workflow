import os
import glob
import sys

# --- Sample Information ---
SAMPLES = {
    "WTD_RI": ("bc2001", "WhiteTail_RI"),
    "MD_837": ("bc2065", "Mule_837"),
    "WTD_EL": ("bc2066", "WhiteTail_EL"),
    "WTD_LA": ("bc2069", "WhiteTail_LA"),
    "MD_838": ("bc2070", "Mule_838"),
}

# --- Define Paths ---
BASE_PATH = "/home/devan/projects/def-shaferab/devan/Odocoileus_virginianus/sperm/hifi"

# Input Paths
DIR_HIFI1 = os.path.join(BASE_PATH, "raw_data", "HiFi_1")
DIR_HIFI2 = os.path.join(BASE_PATH, "raw_data", "HiFi_2")
REF_FASTA_DIR = os.path.join(BASE_PATH, "fasta_refs")

# Output Paths
MAPPING_OUTPUT_DIR = os.path.join(BASE_PATH, "mapping")
SCRIPT_OUTPUT_DIR = os.path.join(MAPPING_OUTPUT_DIR, "mapping_scripts")

# Ensure output directories exist
os.makedirs(MAPPING_OUTPUT_DIR, exist_ok=True)
os.makedirs(SCRIPT_OUTPUT_DIR, exist_ok=True)


# --- The Mapping SLURM Template ---
# This script will map the reads to Haplotype 1 and Haplotype 2 independently.
BASH_TEMPLATE = """#!/bin/bash
#SBATCH --account=rrg-shaferab
#SBATCH --mem=64G
#SBATCH --cpus-per-task=24
#SBATCH --time=23:59:00
#SBATCH --job-name=mm2_{JOB_NAME}
#SBATCH --output={SCRIPT_OUTPUT_DIR}/{JOB_NAME}.out

# Load necessary modules
module load minimap2
module load samtools

# --- Configuration ---
SAMPLE_NAME="{SAMPLE_NAME}"

# Input Files
INPUT_FILE1="{INPUT_FILE1}"
INPUT_FILE2="{INPUT_FILE2}"
HAP1_REF="{HAP1_REF}"
HAP2_REF="{HAP2_REF}"

# Output Path
OUTPUT_DIR="{MAPPING_OUTPUT_DIR}"

# --- Program Execution ---
echo "Starting minimap2 mapping for $SAMPLE_NAME"
mkdir -p "$OUTPUT_DIR"

# 1. Map to Haplotype 1 (Hap1)
# -ax map-hifi: optimized preset for PacBio HiFi reads
# -t 24: threads
# | samtools view: filter reads to MAPQ >= 60 (high confidence, as used in the paper)
echo "Mapping to Haplotype 1..."
cat "$INPUT_FILE1" "$INPUT_FILE2" | \\
minimap2 -t 60 -ax map-hifi "$HAP1_REF" - | \\
samtools view -@ 4 -b -h -q 60 - | \\
samtools sort -@ 4 -o "$OUTPUT_DIR/{SAMPLE_NAME}.hap1.q60.sorted.bam"

# 2. Map to Haplotype 2 (Hap2)
echo "Mapping to Haplotype 2..."
cat "$INPUT_FILE1" "$INPUT_FILE2" | \\
minimap2 -t 24 -ax map-hifi "$HAP2_REF" - | \\
samtools view -@ 4 -b -h -q 60 - | \\
samtools sort -@ 4 -o "$OUTPUT_DIR/{SAMPLE_NAME}.hap2.q60.sorted.bam"

echo "Minimap2 mapping complete for $SAMPLE_NAME. BAM files are in $OUTPUT_DIR"
"""

# --- Generation Loop ---
print(f"Generating minimap2 scripts in {SCRIPT_OUTPUT_DIR}...")

for desired_name, (barcode, full_name) in SAMPLES.items():
    # --- Find the input FASTQ paths using glob ---
    pattern1 = os.path.join(DIR_HIFI1, f"*{barcode}--{barcode}*.fastq.gz")
    matches1 = glob.glob(pattern1)
    
    if desired_name in ["MD_837", "MD_838"]:
        pattern2 = os.path.join(DIR_HIFI2, f"{full_name}_*.fastq.gz")
    else:
        pattern2 = os.path.join(DIR_HIFI2, f"*{barcode}*.fastq.gz")
        
    matches2 = glob.glob(pattern2)
    
    if len(matches1) != 1 or len(matches2) != 1:
        print(f"\nFATAL ERROR: Could not uniquely match input reads for {desired_name}. Check the paths.")
        sys.exit(1)
    
    input_file1 = matches1[0]
    input_file2 = matches2[0]
    
    # --- Define the FASTA paths ---
    hap1_ref = os.path.join(REF_FASTA_DIR, f"{desired_name}.hap1.fasta")
    hap2_ref = os.path.join(REF_FASTA_DIR, f"{desired_name}.hap2.fasta")


    # --- Generate the script ---
    script_name = f"submit_minimap2_{desired_name}.sh"
    output_path = os.path.join(SCRIPT_OUTPUT_DIR, script_name)

    formatted_script = BASH_TEMPLATE.format(
        JOB_NAME=desired_name,
        SAMPLE_NAME=desired_name,
        INPUT_FILE1=input_file1,
        INPUT_FILE2=input_file2,
        HAP1_REF=hap1_ref,
        HAP2_REF=hap2_ref,
        MAPPING_OUTPUT_DIR=MAPPING_OUTPUT_DIR,
        SCRIPT_OUTPUT_DIR=SCRIPT_OUTPUT_DIR
    )

    # Write the script to file
    with open(output_path, "w") as f:
        f.write(formatted_script)

    os.chmod(output_path, 0o755) # Make it executable

    print(f"  Created: {script_name}")

print("\nScript generation complete. These will run after the FASTA conversion step.")
