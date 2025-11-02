from typing import Dict


def calculate_read_statistics(variant: Dict) -> Dict:
    info = variant['info']
    
    # Extract depth and read support from INFO field
    depth = info.get('DP', 0)
    ref_reads = info.get('RO', 0)
    alt_reads = info.get('AO', 0)
    
    # Calculate percentage
    if depth > 0:
        variant_percentage = (alt_reads / depth) * 100 if alt_reads else 0
        ref_percentage = (ref_reads / depth) * 100 if ref_reads else 0
    else:
        variant_percentage = 0
        ref_percentage = 0
    
    # Get allele frequency from INFO if available
    af = info.get('AF', 0)
    
    return {
        'depth': depth,
        'variant_reads': alt_reads,
        'reference_reads': ref_reads,
        'variant_percentage': round(variant_percentage, 2),
        'reference_percentage': round(ref_percentage, 2),
        'allele_frequency': round(af, 4) if isinstance(af, (int, float)) else 0
    }


def determine_variant_type(ref: str, alt: str) -> str:
    ref_len = len(ref)
    alt_len = len(alt)
    
    if ref_len == alt_len == 1:
        return "SNP (substitution)"
    elif alt_len > ref_len:
        return "Insertion"
    elif ref_len > alt_len:
        return "Deletion"
    elif '[' in alt or ']' in alt:
        return "CNV"
    elif alt.startswith('<') or ref.startswith('<'):
        return "Structural variant"
    else:
        return "Indel"

