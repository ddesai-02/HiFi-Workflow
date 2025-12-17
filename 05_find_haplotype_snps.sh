#!/bin/bash
#SBATCH --account=rrg-shaferab
#SBATCH --mem=32G
#SBATCH --cpus-per-task=12
#SBATCH --time=04:00:00
#SBATCH --job-name=hap_snps

# Define Paths
BASE_PATH="/home/devan/projects/def-shaferab/devan/Odocoileus_virginianus/sperm/hifi"
REF_DIR="$BASE_PATH/fasta_refs"
OUT_DIR="$BASE_PATH/analysis/variants"
mkdir -p "$OUT_DIR"

module load minimap2
module load samtools

SAMPLES=("MD_837" "MD_838" "WTD_EL" "WTD_LA" "WTD_RI")

for SAMPLE in "${SAMPLES[@]}"; do
    echo "Finding differences between Haplotypes for $SAMPLE..."
    
    # Align Hap2 to Hap1 using assembly-to-assembly preset (asm5)
    # --cs: generates the 'cs' tag used for calling variants
    minimap2 -t 12 -cx asm5 --cs "$REF_DIR/${SAMPLE}.hap1.fasta" "$REF_DIR/${SAMPLE}.hap2.fasta" > "$OUT_DIR/${SAMPLE}_asm_diff.paf"
    
    # Optional: Convert PAF to a VCF-like table of SNPs
    # We will use this in the next step to filter for 'good' informative sites
done
