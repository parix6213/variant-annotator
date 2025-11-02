import sys
from typing import Dict, List, Optional, Callable

from vcf_parser import parse_header, parse_variants
from vep_client import get_variant_effects
from variant_analysis import calculate_read_statistics, determine_variant_type


def annotate_variant(
    variant: Dict,
    vep_getter: Optional[Callable] = None,
    species: str = "human",
    assembly: str = "GRCh37"
) -> Dict:
    # Basic read statistics
    stats = calculate_read_statistics(variant)
    
    # Variant type
    variant_type = determine_variant_type(variant['ref'], variant['alt'])
    
    # Initialize annotation
    annotation = {
        'chromosome': variant['chrom'],
        'position': variant['pos'],
        'variant_id': variant['id'] if variant['id'] != '.' else f"{variant['chrom']}:{variant['pos']}",
        'reference': variant['ref'],
        'alternate': variant['alt'],
        'quality': variant['qual'],
        'filter': variant['filter'],
        'variant_type': variant_type,
        **stats
    }
    
    # VEP annotations (always enabled)
    vep_func = vep_getter if vep_getter else get_variant_effects
    vep_data = vep_func(
        variant['chrom'],
        variant['pos'],
        variant['ref'],
        variant['alt'],
        species=species,
        assembly=assembly
    )
    annotation.update(vep_data)
    
    return annotation


def annotate_vcf(
    vcf_file: str,
    assembly: str = "GRCh37",
    limit: Optional[int] = None
) -> List[Dict]:
    # Parse header to get samples
    _, samples = parse_header(vcf_file)
    
    annotations = []
    count = 0
    
    # Process variants
    for variant in parse_variants(vcf_file, samples):
        if limit and count >= limit:
            break
        
        annotation = annotate_variant(
            variant,
            assembly=assembly
        )
        
        annotations.append(annotation)
        count += 1
        
        if count % 10 == 0:
            print(f"Annotated {count} variants...", file=sys.stderr)
    
    print(f"Total variants annotated: {count}", file=sys.stderr)
    return annotations

