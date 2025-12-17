import sys
import re

def parse_paf_cs(paf_file, output_file):
    print(f"Processing {paf_file}...")
    with open(paf_file, 'r') as f, open(output_file, 'w') as out:
        # Header for our informative SNP table
        out.write("chrom\tpos_hap1\tbase_hap1\tbase_hap2\n")
        
        for line in f:
            fields = line.strip().split('\t')
            if len(fields) < 12: continue
            
            # Hap1 (Target) Info
            t_name = fields[5]
            t_start = int(fields[7])
            
            # Find the 'cs' tag
            cs_tag = next((x for x in fields[12:] if x.startswith('cs:Z:')), None)
            if not cs_tag: continue
            cs_str = cs_tag[5:]
            
            # Regex to find: :[0-9]+ (matches), *[a-z][a-z] (mismatches), +[a-z] (ins), -[a-z] (del)
            pattern = re.compile(r'(:[0-9]+|\*[a-z][a-z]|\+[a-z]+|-[a-z]+)')
            ops = pattern.findall(cs_str)
            
            curr_t_pos = t_start
            for op in ops:
                if op.startswith(':'): # Match
                    curr_t_pos += int(op[1:])
                elif op.startswith('*'): # SNP (Mismatch)
                    # format: *[ref][query]
                    ref_base = op[1].upper()
                    qry_base = op[2].upper()
                    # Output: Chrom, 1-based Position, Hap1_Base, Hap2_Base
                    out.write(f"{t_name}\t{curr_t_pos + 1}\t{ref_base}\t{qry_base}\n")
                    curr_t_pos += 1
                elif op.startswith('-'): # Deletion in Hap2
                    curr_t_pos += len(op[1:])
                elif op.startswith('+'): # Insertion in Hap2
                    continue # Positions are relative to Hap1 (Target)

# Run for your samples
samples = ["MD_837", "MD_838", "WTD_EL", "WTD_LA", "WTD_RI"]
for s in samples:
    parse_paf_cs(f"{s}_asm_diff.paf", f"{s}_candidate_snps.tsv")06_extract_paf_snps.py 
