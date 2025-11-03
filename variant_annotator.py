#!/usr/bin/env python3
import argparse

from annotator import annotate_vcf
from exporter import export_to_tsv


def main():
    parser = argparse.ArgumentParser(
        description="Annotate variants from a VCF file",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'vcf_file',
        help='Input VCF file path'
    )
    parser.add_argument(
        '-o', '--output',
        default='annotations.tsv',
        help='Output TSV file path (default: annotations.tsv)'
    )
    parser.add_argument(
        '--assembly',
        default='GRCh37',
        choices=['GRCh37', 'GRCh38'],
        help='Genome assembly (default: GRCh37)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of variants to process (for testing)'
    )
    
    args = parser.parse_args()
    
    # Annotate variants
    annotations = annotate_vcf(
        args.vcf_file,
        assembly=args.assembly,
        limit=args.limit
    )
    
    # Export to TSV
    export_to_tsv(annotations, args.output)
    
    print(f"Done! Output saved to {args.output}")


if __name__ == '__main__':
    main()

