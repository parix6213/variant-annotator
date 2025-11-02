"""
Exporter - Pure functions for exporting annotation data to TSV format.
"""

import csv
import sys
from typing import List, Dict


FIELDNAMES = [
    'chromosome', 'position', 'variant_id', 'reference', 'alternate',
    'quality', 'filter', 'variant_type',
    'depth', 'variant_reads', 'reference_reads', 
    'variant_percentage', 'reference_percentage', 'allele_frequency',
    'gene_id', 'gene_symbol', 'biotype', 'consequence_terms', 
    'impact', 'strand'
]


def export_to_tsv(annotations: List[Dict], output_file: str) -> None:
    """
    Export annotations to TSV file.
    
    Args:
        annotations: List of annotation dictionaries
        output_file: Path to output TSV file
    """
    if not annotations:
        print("No annotations to export", file=sys.stderr)
        return
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, delimiter='\t')
        writer.writeheader()
        writer.writerows(annotations)
    
    print(f"Annotations exported to {output_file}", file=sys.stderr)

