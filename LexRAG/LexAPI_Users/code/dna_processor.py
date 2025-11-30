"""
DNA Processor for LexAPI_Users
Handles DNA file upload, processing, and variant extraction
"""

import gzip
import json
import csv
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import hashlib

from code.database_manager import UserDatabaseManager

class DNAProcessor:
    """Processes DNA files from various sources"""
    
    def __init__(self):
        self.db_manager = UserDatabaseManager()
        self.supported_formats = {
            "23andme": self._process_23andme,
            "ancestry": self._process_ancestry,
            "myheritage": self._process_myheritage,
            "vcf": self._process_vcf,
            "generic": self._process_generic_csv
        }
    
    def process_dna_file(self, user_id: str, file_path: Path, file_type: str = "auto") -> Dict[str, Any]:
        """Process uploaded DNA file and extract variants"""
        try:
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            
            # Auto-detect file type if not specified
            if file_type == "auto":
                file_type = self._detect_file_type(file_path)
            
            print(f"Processing DNA file: {file_path.name} ({file_size_mb:.1f} MB) as {file_type}")
            
            # Generate file ID
            file_id = hashlib.md5(f"{user_id}_{file_path.name}_{datetime.now()}".encode()).hexdigest()
            
            # Process file based on type
            if file_type in self.supported_formats:
                variants = self.supported_formats[file_type](file_path)
            else:
                return {"error": f"Unsupported file type: {file_type}"}
            
            # Calculate quality metrics
            quality_metrics = self._calculate_quality_metrics(variants)
            
            # Store in database
            conn = self.db_manager.get_user_db_connection(read_only=False)
            
            conn.execute("""
                INSERT INTO user_genomics 
                (user_id, file_id, file_name, file_type, file_size_mb, variant_count, 
                 processing_status, quality_score, upload_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                user_id, file_id, file_path.name, file_type, file_size_mb,
                len(variants), "processed", quality_metrics["overall_quality"],
                datetime.now()
            ])
            
            conn.close()
            
            return {
                "file_id": file_id,
                "processing_status": "completed",
                "variants_found": len(variants),
                "quality_metrics": quality_metrics,
                "file_type_detected": file_type,
                "processing_time": "calculated_in_background",
                "next_steps": ["review_findings", "complete_questionnaire"]
            }
            
        except Exception as e:
            return {"error": f"DNA processing failed: {e}"}
    
    def _detect_file_type(self, file_path: Path) -> str:
        """Auto-detect DNA file type from content"""
        try:
            # Read first few lines to detect format
            if file_path.suffix == '.gz':
                with gzip.open(file_path, 'rt') as f:
                    first_lines = [f.readline().strip() for _ in range(5)]
            else:
                with open(file_path, 'r') as f:
                    first_lines = [f.readline().strip() for _ in range(5)]
            
            # Check for format indicators
            content = "\\n".join(first_lines).lower()
            
            if "23andme" in content or "rsid\\tchromosome\\tposition" in content:
                return "23andme"
            elif "ancestrydna" in content or "rsid,chromosome,position" in content:
                return "ancestry"
            elif "##fileformat=vcf" in content:
                return "vcf"
            elif "myheritage" in content:
                return "myheritage"
            else:
                return "generic"
                
        except Exception:
            return "generic"
    
    def _process_23andme(self, file_path: Path) -> List[Dict]:
        """Process 23andMe format file"""
        variants = []
        
        try:
            open_func = gzip.open if file_path.suffix == '.gz' else open
            mode = 'rt' if file_path.suffix == '.gz' else 'r'
            
            with open_func(file_path, mode) as f:
                # Skip header lines starting with #
                for line in f:
                    if line.startswith('#'):
                        continue
                    
                    # Process variant lines
                    parts = line.strip().split('\\t')
                    if len(parts) >= 4:
                        rsid, chromosome, position, genotype = parts[:4]
                        
                        if rsid.startswith('rs') and genotype != '--':
                            variants.append({
                                "rsid": rsid,
                                "chromosome": chromosome,
                                "position": int(position) if position.isdigit() else 0,
                                "genotype": genotype,
                                "source": "23andme"
                            })
                            
                    # Limit processing for large files
                    if len(variants) >= 1000000:  # 1M variants max for demo
                        break
                        
        except Exception as e:
            print(f"Error processing 23andMe file: {e}")
        
        return variants
    
    def _process_ancestry(self, file_path: Path) -> List[Dict]:
        """Process AncestryDNA format file"""
        variants = []
        
        try:
            with open(file_path, 'r') as f:
                reader = csv.reader(f)
                
                # Skip header
                next(reader, None)
                
                for row in reader:
                    if len(row) >= 5:
                        rsid, chromosome, position, allele1, allele2 = row[:5]
                        
                        if rsid.startswith('rs'):
                            variants.append({
                                "rsid": rsid,
                                "chromosome": chromosome,
                                "position": int(position) if position.isdigit() else 0,
                                "genotype": f"{allele1}{allele2}",
                                "source": "ancestry"
                            })
                            
                    if len(variants) >= 1000000:
                        break
                        
        except Exception as e:
            print(f"Error processing AncestryDNA file: {e}")
        
        return variants
    
    def _process_vcf(self, file_path: Path) -> List[Dict]:
        """Process VCF format file"""
        variants = []
        
        try:
            open_func = gzip.open if file_path.suffix == '.gz' else open
            mode = 'rt' if file_path.suffix == '.gz' else 'r'
            
            with open_func(file_path, mode) as f:
                for line in f:
                    if line.startswith('#'):
                        continue
                    
                    parts = line.strip().split('\\t')
                    if len(parts) >= 5:
                        chrom, pos, variant_id, ref, alt = parts[:5]
                        
                        variants.append({
                            "rsid": variant_id,
                            "chromosome": chrom,
                            "position": int(pos) if pos.isdigit() else 0,
                            "ref": ref,
                            "alt": alt,
                            "source": "vcf"
                        })
                        
                    if len(variants) >= 1000000:
                        break
                        
        except Exception as e:
            print(f"Error processing VCF file: {e}")
        
        return variants
    
    def _process_generic_csv(self, file_path: Path) -> List[Dict]:
        """Process generic CSV format"""
        variants = []
        
        try:
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    # Try to extract standard fields
                    variant = {}
                    
                    # Look for common column names
                    for key, value in row.items():
                        key_lower = key.lower()
                        if 'rsid' in key_lower or 'rs' in key_lower:
                            variant["rsid"] = value
                        elif 'chrom' in key_lower or 'chr' in key_lower:
                            variant["chromosome"] = value
                        elif 'pos' in key_lower or 'position' in key_lower:
                            variant["position"] = int(value) if value.isdigit() else 0
                        elif 'genotype' in key_lower:
                            variant["genotype"] = value
                    
                    if variant.get("rsid"):
                        variant["source"] = "generic"
                        variants.append(variant)
                        
                    if len(variants) >= 1000000:
                        break
                        
        except Exception as e:
            print(f"Error processing generic file: {e}")
        
        return variants
    
    def _process_myheritage(self, file_path: Path) -> List[Dict]:
        """Process MyHeritage format file"""
        # Similar to 23andMe but with slight format differences
        return self._process_23andme(file_path)  # Use same logic for now
    
    def _calculate_quality_metrics(self, variants: List[Dict]) -> Dict[str, Any]:
        """Calculate quality metrics for processed variants"""
        if not variants:
            return {"overall_quality": 0.0, "metrics": {}}
        
        # Calculate various quality metrics
        total_variants = len(variants)
        valid_chromosomes = sum(1 for v in variants if v.get("chromosome", "").replace("chr", "") in [str(i) for i in range(1, 23)] + ["X", "Y"])
        valid_positions = sum(1 for v in variants if isinstance(v.get("position", 0), int) and v["position"] > 0)
        valid_rsids = sum(1 for v in variants if v.get("rsid", "").startswith("rs"))
        
        # Quality scores
        chromosome_quality = valid_chromosomes / total_variants if total_variants > 0 else 0
        position_quality = valid_positions / total_variants if total_variants > 0 else 0
        rsid_quality = valid_rsids / total_variants if total_variants > 0 else 0
        
        # Coverage assessment (basic)
        coverage_quality = min(total_variants / 500000, 1.0)  # 500K variants = good coverage
        
        # Overall quality
        overall_quality = (chromosome_quality + position_quality + rsid_quality + coverage_quality) / 4
        
        return {
            "overall_quality": round(overall_quality, 3),
            "metrics": {
                "total_variants": total_variants,
                "chromosome_quality": round(chromosome_quality, 3),
                "position_quality": round(position_quality, 3),
                "rsid_quality": round(rsid_quality, 3),
                "coverage_quality": round(coverage_quality, 3)
            },
            "quality_grade": (
                "Excellent" if overall_quality >= 0.9 else
                "Good" if overall_quality >= 0.7 else
                "Fair" if overall_quality >= 0.5 else
                "Poor"
            )
        }
