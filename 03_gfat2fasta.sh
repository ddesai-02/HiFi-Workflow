#!/bin/bash
#SBATCH --account=rrg-shaferab
#SBATCH --mem=8G
#SBATCH --cpus-per-task=1
#SBATCH --time=0:30:00
#SBATCH --job-name=gfa2fasta
#SBATCH --output=/home/devan/projects/def-shaferab/devan/Odocoileus_virginianus/sperm/hifi/gfa2fasta.out

# --- Configuration (Full Absolute Paths) ---
BASE_PATH="/home/devan/projects/def-shaferab/devan/Odocoileus_virginianus/sperm/hifi"
ASSEMBLY_DIR="$BASE_PATH/assemblies"
OUTPUT_DIR="$ASSEMBLY_DIR/fasta_refs"

# PATH TO YOUR COMPILED GFATOOLS: This is the hardcoded path based on your git clone.
GFATOOLS_BIN="$BASE_PATH/gfatools/gfatools" 

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "Starting GFA to FASTA conversion using $GFATOOLS_BIN"

# Check if gfatools binary exists
if [ ! -f "$GFATOOLS_BIN" ]; then
    echo "FATAL ERROR: gfatools binary not found at $GFATOOLS_BIN."
    echo "Please verify the location and re-run."
    exit 1
fi

# Find all Haplotype 1 GFA files to iterate over the 5 samples
for HAP1_GFA in $ASSEMBLY_DIR/*.asm.bp.hap1.p_ctg.gfa; do
    
    if [ -f "$HAP1_GFA" ]; then
        # Extract the sample name (e.g., MD_837)
        SAMPLE=$(basename "$HAP1_GFA" | sed 's/\.asm\.bp\.hap1\.p_ctg\.gfa//')
        
        # Define Haplotype 2 file name
        HAP2_GFA="$ASSEMBLY_DIR/${SAMPLE}.asm.bp.hap2.p_ctg.gfa"
        
        if [ ! -f "$HAP2_GFA" ]; then
            echo "Warning: Missing Haplotype 2 file ($HAP2_GFA) for $SAMPLE. Skipping."
            continue
        fi

        # 1. Convert Haplotype 1
        HAP1_OUT="$OUTPUT_DIR/${SAMPLE}.hap1.fasta"
        echo "Converting $SAMPLE Haplotype 1: $HAP1_GFA -> $HAP1_OUT"
        "$GFATOOLS_BIN" gfa2fa "$HAP1_GFA" > "$HAP1_OUT"
        
        # 2. Convert Haplotype 2
        HAP2_OUT="$OUTPUT_DIR/${SAMPLE}.hap2.fasta"
        echo "Converting $SAMPLE Haplotype 2: $HAP2_GFA -> $HAP2_OUT"
        "$GFATOOLS_BIN" gfa2fa "$HAP2_GFA" > "$HAP2_OUT"
    fi
done

echo "Conversion complete. FASTA files are ready in $OUTPUT_DIR"
