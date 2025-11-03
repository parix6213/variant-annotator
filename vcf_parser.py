from typing import Dict, List, Iterator, Tuple


def parse_info(info_str: str) -> Dict:
    info_dict = {}
    for item in info_str.split(';'):
        if '=' in item:
            key, value = item.split('=', 1)
            # Handle comma-separated values (take first value)
            if ',' in value:
                value = value.split(',')[0]
            
            # Try to convert to appropriate type
            clean_value = value.replace('.', '').replace('-', '')
            if clean_value.isdigit():
                if '.' in value:
                    try:
                        info_dict[key] = float(value)
                    except ValueError:
                        info_dict[key] = value
                else:
                    try:
                        info_dict[key] = int(value)
                    except ValueError:
                        info_dict[key] = value
            else:
                info_dict[key] = value
        else:
            info_dict[item] = True
    return info_dict


def parse_genotype(genotype_str: str, format_fields: List[str]) -> Dict:
    genotype_dict = {}
    values = genotype_str.split(':')
    for i, field in enumerate(format_fields):
        genotype_dict[field] = values[i] if i < len(values) else ''
    return genotype_dict


def parse_variant_line(line: str, samples: List[str]) -> Dict:
    fields = line.split('\t')
    
    variant = {
        'chrom': fields[0],
        'pos': int(fields[1]),
        'id': fields[2],
        'ref': fields[3],
        'alt': fields[4],
        'qual': fields[5],
        'filter': fields[6],
        'info': parse_info(fields[7]),
        'format': fields[8] if len(fields) > 8 else '',
        'genotypes': {}
    }
    
    # Parse sample genotype data if available
    if len(fields) > 9 and samples:
        format_fields = variant['format'].split(':')
        for i, sample in enumerate(samples):
            sample_data = fields[9 + i] if len(fields) > 9 + i else ''
            variant['genotypes'][sample] = parse_genotype(
                sample_data, format_fields
            )
    
    return variant


def parse_header(vcf_file: str) -> Tuple[List[str], List[str]]:
    header = []
    samples = []
    
    with open(vcf_file, 'r') as f:
        for line in f:
            if line.startswith('##'):
                header.append(line.strip())
            elif line.startswith('#CHROM'):
                # Header line with sample names
                fields = line.strip().split('\t')
                samples = fields[9:] if len(fields) > 9 else []
                header.append(line.strip())
                return header, samples
    
    return header, samples


def parse_variants(vcf_file: str, samples: List[str]) -> Iterator[Dict]:
    with open(vcf_file, 'r') as f:
        # Skip header lines
        for line in f:
            if not line.startswith('#'):
                yield parse_variant_line(line.strip(), samples)

