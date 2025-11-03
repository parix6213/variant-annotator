import sys
import requests
from typing import Dict


BASE_URL = "https://rest.ensembl.org"


def format_chromosome(chrom: str) -> str:
    return chrom[3:] if chrom.startswith('chr') else chrom


def build_variant_region(chrom: str, pos: int, alt: str) -> str:
    formatted_chrom = format_chromosome(chrom)
    return f"{formatted_chrom}:{pos}-{pos}/{alt}"


def create_error_response(error_type: str = 'API_ERROR') -> Dict:
    return {
        'gene_id': error_type,
        'gene_symbol': error_type,
        'biotype': error_type,
        'consequence_terms': error_type,
        'impact': error_type,
        'strand': error_type
    }


def parse_vep_response(data: list) -> Dict:
    if not data or len(data) == 0:
        return {
            'gene_id': 'N/A',
            'gene_symbol': 'N/A',
            'biotype': 'N/A',
            'consequence_terms': 'N/A',
            'impact': 'N/A',
            'strand': 'N/A'
        }
    
    variant = data[0]
    consequences = variant.get('transcript_consequences', [])
    
    if consequences:
        consequence = consequences[0]
        return {
            'gene_id': consequence.get('gene_id', 'N/A'),
            'gene_symbol': consequence.get('gene_symbol', 'N/A'),
            'biotype': consequence.get('biotype', 'N/A'),
            'consequence_terms': ', '.join(consequence.get('consequence_terms', [])),
            'impact': consequence.get('impact', 'N/A'),
            'strand': consequence.get('strand', 'N/A')
        }
    
    return {
        'gene_id': 'N/A',
        'gene_symbol': 'N/A',
        'biotype': 'N/A',
        'consequence_terms': 'N/A',
        'impact': 'N/A',
        'strand': 'N/A'
    }


def handle_vep_error(error_msg: str, variant_region: str, chrom: str, pos: int, ref: str, alt: str) -> Dict:
    if "matches reference" in error_msg:
        print(f"Warning: Reference mismatch for {chrom}:{pos} ref={ref} alt={alt}: {error_msg}", file=sys.stderr)
        return create_error_response('REF_MISMATCH')
    else:
        print(f"Warning: VEP API error for {variant_region}: {error_msg}", file=sys.stderr)
        return create_error_response('API_ERROR')


def get_variant_effects(
    chrom: str,
    pos: int,
    ref: str,
    alt: str,
    species: str = "human",
    assembly: str = "GRCh37"
) -> Dict:
    variant_region = build_variant_region(chrom, pos, alt)
    endpoint = f"{BASE_URL}/vep/{species}/region/{variant_region}"
    params = {
        "content-type": "application/json",
        "assembly": assembly
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.get(endpoint, headers=headers, params=params, timeout=10)
        
        # Try to parse JSON response even for error status codes
        try:
            data = response.json()
        except ValueError:
            # Not JSON, raise the HTTP error
            response.raise_for_status()
            data = None
        
        # Handle error responses (including 400 Bad Request with JSON error messages)
        if isinstance(data, dict) and "error" in data:
            error_msg = data.get('error', 'Unknown error')
            return handle_vep_error(error_msg, variant_region, chrom, pos, ref, alt)
        
        # Raise for other HTTP errors
        response.raise_for_status()
        
        # Parse successful response
        return parse_vep_response(data)
        
    except requests.exceptions.HTTPError as e:
        # For HTTP errors, try to get JSON error message if available
        if e.response is not None:
            try:
                error_data = e.response.json()
                if isinstance(error_data, dict) and "error" in error_data:
                    error_msg = error_data.get('error', str(e))
                    return handle_vep_error(error_msg, variant_region, chrom, pos, ref, alt)
                else:
                    print(f"Warning: VEP API HTTP error for {variant_region}: {e}", file=sys.stderr)
            except (ValueError, AttributeError):
                print(f"Warning: VEP API HTTP error for {variant_region}: {e}", file=sys.stderr)
        else:
            print(f"Warning: VEP API HTTP error for {variant_region}: {e}", file=sys.stderr)
        
        return create_error_response('API_ERROR')
        
    except requests.exceptions.RequestException as e:
        # For other request exceptions (network errors, timeouts, etc.)
        print(f"Warning: VEP API request failed for {variant_region}: {e}", file=sys.stderr)
        return create_error_response('API_ERROR')

