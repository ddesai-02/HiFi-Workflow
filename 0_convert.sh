#!/bin/bash
#SBATCH --account=rrg-shaferab
#SBATCH --mem=32G
#SBATCH --cpus-per-task=4
#SBATCH --time=11:59:00
#SBATCH --job-name=bam2fastq_batch

# --- Configuration ---
module load samtools

# --- Define Paths ---
# Directory where the raw BAM files are located (Input Dir)
BAM_DIR="/home/devan/projects/rrg-shaferab/DEER_FASTQ/SPERM/HiFi_2" 
# Directory where the FASTQ files should be saved (Output Dir)
FASTQ_DIR="/home/devan/projects/def-shaferab/devan/Odocoileus_virginianus/sperm/hifi/raw_data/HiFi_2"

echo "Starting batch conversion of BAM files to FASTQ..."
echo "BAM Source Directory: ${BAM_DIR}"
echo "FASTQ Destination Directory: ${FASTQ_DIR}"
echo "---"

# Loop through all files in the defined BAM_DIR ending with .bam
for INPUT_PATH in "${BAM_DIR}"/*.bam; do
    
    # Check if any .bam files were found (to handle the literal string case)
    if [ ! -f "$INPUT_PATH" ]; then
        echo "No .bam files found in ${BAM_DIR}. Exiting."
        exit 1
    fi

    # 1. EXTRACT FILENAME: Get ONLY the filename from the full path
    # Example: /path/to/file.bam -> file.bam
    FILENAME="${INPUT_PATH##*/}"

    # 2. DEFINE OUTPUT FILENAME: Remove .bam and add .fastq.gz
    # Example: file.bam -> file.fastq.gz
    OUTPUT_FILENAME="${FILENAME%.bam}.fastq.gz"

    # 3. COMBINE: Set the full output path
    # Example: /output/dir/ + file.fastq.gz
    OUTPUT_FASTQ="${FASTQ_DIR}/${OUTPUT_FILENAME}"

    echo "Processing Input: $INPUT_PATH"
    echo "Output will be: $OUTPUT_FASTQ"
    
    # Run the samtools conversion
    if samtools fastq -@ 4 -n "$INPUT_PATH" | gzip > "$OUTPUT_FASTQ"; then
        echo "SUCCESS: $INPUT_PATH converted."
    else
        echo "ERROR: Conversion failed for $INPUT_PATH."
        # This error may also be due to not having write permissions in $FASTQ_DIR
    fi

done

echo "---"
echo "Batch conversion complete."
