"""
Tool Executor for LexAPI_AIGateway
Executes LexRAG API calls as tools for the DNA Expert model
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import sys
from pathlib import Path

parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from config.model_config import LEXRAG_APIS, TOOL_TIMEOUT

class ToolExecutor:
    """Executes tools/API calls for the AI model"""
    
    def __init__(self):
        self.apis = LEXRAG_APIS
        self.timeout = TOOL_TIMEOUT
        
    def get_user_digital_twin(self, user_id: str) -> Dict[str, Any]:
        """Get user's digital twin with Adam/Eve overlay"""
        try:
            response = requests.get(
                f"{self.apis['digital_twin']}/twin/{user_id}/model",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Digital twin retrieval failed: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"Digital twin tool error: {e}"}
    
    def analyze_gene(self, gene_symbol: str, user_id: str = None) -> Dict[str, Any]:
        """Analyze gene using 4.4B genomic records"""
        try:
            response = requests.get(
                f"{self.apis['genomics']}/analyze/gene/{gene_symbol}",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                gene_data = response.json()
                
                # Add user context if available
                if user_id:
                    user_context = self.get_user_digital_twin(user_id)
                    gene_data["user_context"] = user_context
                
                return gene_data
            else:
                return {"error": f"Gene analysis failed: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"Gene analysis tool error: {e}"}
    
    def analyze_variant(self, variant_id: str, user_id: str = None) -> Dict[str, Any]:
        """Analyze specific genetic variant"""
        try:
            response = requests.get(
                f"{self.apis['genomics']}/analyze/variant/{variant_id}",
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                variant_data = response.json()
                
                # Add user context if available
                if user_id:
                    user_context = self.get_user_digital_twin(user_id)
                    variant_data["user_context"] = user_context
                
                return variant_data
            else:
                return {"error": f"Variant analysis failed: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"Variant analysis tool error: {e}"}
    
    def get_user_genomics(self, user_id: str, gene_filter: str = None) -> Dict[str, Any]:
        """Get user's genomic data"""
        try:
            url = f"{self.apis['users']}/users/{user_id}/genomics"
            if gene_filter:
                url += f"?gene_filter={gene_filter}"
            
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"User genomics retrieval failed: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"User genomics tool error: {e}"}
    
    def analyze_drug_interactions(self, user_id: str, medications: List[str]) -> Dict[str, Any]:
        """Analyze pharmacogenomic interactions"""
        try:
            # Get user's pharmacogenomic profile
            pharma_genes = ['CYP2D6', 'CYP2C19', 'CYP3A4', 'CYP2C9', 'DPYD', 'TPMT']
            
            pharma_analysis = {}
            for gene in pharma_genes:
                gene_response = requests.get(
                    f"{self.apis['genomics']}/analyze/gene/{gene}",
                    timeout=self.timeout
                )
                
                if gene_response.status_code == 200:
                    pharma_analysis[gene] = gene_response.json()
            
            # Add user context
            user_context = self.get_user_digital_twin(user_id)
            
            return {
                "user_id": user_id,
                "medications": medications,
                "pharmacogenomic_analysis": pharma_analysis,
                "user_context": user_context,
                "analysis_type": "drug_interaction_assessment"
            }
            
        except Exception as e:
            return {"error": f"Drug interaction analysis failed: {e}"}
    
    def cross_axis_analysis(self, query: str, axes: List[str], user_id: str = None) -> Dict[str, Any]:
        """Perform multi-axis biological analysis"""
        try:
            analysis_results = {}
            
            # Query relevant APIs based on requested axes
            if "genomics" in axes:
                # Extract gene names from query for genomics analysis
                gene_names = self._extract_gene_names(query)
                for gene in gene_names:
                    gene_data = self.analyze_gene(gene, user_id)
                    analysis_results[f"genomics_{gene}"] = gene_data
            
            if "anatomy" in axes:
                # Actually analyze organ if query mentions one, or health if generic
                # For now, assume query might contain organ name
                organ_guess = "heart" if "heart" in query.lower() else "brain" if "brain" in query.lower() else None
                
                if organ_guess:
                    anatomics_response = requests.get(
                        f"{self.apis['anatomics']}/analyze/organ/{organ_guess}",
                        timeout=self.timeout
                    )
                else:
                    anatomics_response = requests.get(
                        f"{self.apis['anatomics']}/health", 
                        timeout=self.timeout
                    )
                
                if anatomics_response.status_code == 200:
                    analysis_results["anatomics"] = anatomics_response.json()
            
            if "literature" in axes:
                # Use search literature endpoint
                literature_response = requests.get(
                    f"{self.apis['literature']}/search/literature/{query}",
                    timeout=self.timeout
                )
                if literature_response.status_code == 200:
                    analysis_results["literature"] = literature_response.json()
            
            # Add user context
            if user_id:
                user_context = self.get_user_digital_twin(user_id)
                analysis_results["user_context"] = user_context
            
            return {
                "query": query,
                "axes_analyzed": axes,
                "analysis_results": analysis_results,
                "analysis_type": "cross_axis_integration"
            }
            
        except Exception as e:
            return {"error": f"Cross-axis analysis failed: {e}"}
    
    def risk_assessment(self, user_id: str, condition: str = None) -> Dict[str, Any]:
        """Comprehensive health risk assessment"""
        try:
            # Get user digital twin for context
            user_twin = self.get_user_digital_twin(user_id)
            
            # Get user genomics data
            user_genomics = self.get_user_genomics(user_id)
            
            # Analyze relevant genes based on condition
            risk_genes = self._get_risk_genes_for_condition(condition)
            
            gene_analyses = {}
            for gene in risk_genes:
                gene_data = self.analyze_gene(gene, user_id)
                gene_analyses[gene] = gene_data
            
            return {
                "user_id": user_id,
                "condition": condition,
                "user_context": user_twin,
                "genomic_data": user_genomics,
                "risk_gene_analyses": gene_analyses,
                "analysis_type": "comprehensive_risk_assessment"
            }
            
        except Exception as e:
            return {"error": f"Risk assessment failed: {e}"}
    
    def get_metabolic_profile(self, user_id: str) -> Dict[str, Any]:
        """Fetch metabolomic profile for a user."""
        try:
            response = requests.get(
                f"{self.apis['metabolics']}/analyze/metabolism/{user_id}",
                timeout=self.timeout
            )
            return response.json() if response.status_code == 200 else {"error": f"Metabolics HTTP {response.status_code}"}
        except Exception as e:
            return {"error": f"Metabolics service error: {e}"}
    
    def get_drug_metabolism(self, drug_name: str) -> Dict[str, Any]:
        """Fetch drug metabolism summary."""
        try:
            response = requests.get(
                f"{self.apis['metabolics']}/analyze/drug_metabolism/{drug_name}",
                timeout=self.timeout
            )
            return response.json() if response.status_code == 200 else {"error": f"Drug metabolism HTTP {response.status_code}"}
        except Exception as e:
            return {"error": f"Drug metabolism service error: {e}"}
    
    def get_environmental_risk(self, location: str) -> Dict[str, Any]:
        """Fetch environmental risk summary."""
        try:
            response = requests.get(
                f"{self.apis['populomics']}/analyze/environmental_risk/{location}",
                timeout=self.timeout
            )
            return response.json() if response.status_code == 200 else {"error": f"Environmental HTTP {response.status_code}"}
        except Exception as e:
            return {"error": f"Environmental service error: {e}"}
    
    def get_disease_risk(self, disease: str) -> Dict[str, Any]:
        """Fetch population disease risk summary."""
        try:
            response = requests.get(
                f"{self.apis['populomics']}/analyze/disease_risk/{disease}",
                timeout=self.timeout
            )
            return response.json() if response.status_code == 200 else {"error": f"Disease risk HTTP {response.status_code}"}
        except Exception as e:
            return {"error": f"Disease risk service error: {e}"}
    
    # ============== NEW HIGH-VALUE TOOLS ==============
    
    def analyze_splice_impact(self, gene_or_variant: str, user_id: str = None) -> Dict[str, Any]:
        """
        Analyze splice site impact for a gene or variant.
        Returns transcript-specific SpliceAI predictions, GTEx tissue dominance, and anatomy mappings.
        Combines: SpliceAI (3.43B) + GENCODE + GTEx (484M) + UBERON
        """
        try:
            results = {
                "query": gene_or_variant,
                "timestamp": datetime.now().isoformat(),
                "transcripts": [],
                "splice_predictions": {},
                "tissue_dominance": {},
                "anatomy_mappings": []
            }
            
            # Determine if it's a gene or variant
            is_gene = gene_or_variant.upper().isalpha() or (len(gene_or_variant) < 15 and not gene_or_variant.startswith("rs"))
            
            # 1. Get gene/variant data from genomics API
            if is_gene:
                gene_response = requests.get(
                    f"{self.apis['genomics']}/analyze/gene/{gene_or_variant}",
                    timeout=self.timeout
                )
                if gene_response.status_code == 200:
                    gene_data = gene_response.json()
                    results["gene_data"] = gene_data
                    
                # Query splice predictions for this gene
                splice_response = requests.get(
                    f"{self.apis['genomics']}/analyze/splice/{gene_or_variant}",
                    timeout=self.timeout
                )
                if splice_response.status_code == 200:
                    results["splice_predictions"] = splice_response.json()
            else:
                # It's a variant - get variant data
                variant_response = requests.get(
                    f"{self.apis['genomics']}/analyze/variant/{gene_or_variant}",
                    timeout=self.timeout
                )
                if variant_response.status_code == 200:
                    results["variant_data"] = variant_response.json()
            
            # 2. Get tissue expression data from metabolics (GTEx)
            expression_response = requests.get(
                f"{self.apis['metabolics']}/analyze/expression/{gene_or_variant}",
                timeout=self.timeout
            )
            if expression_response.status_code == 200:
                expr_data = expression_response.json()
                results["tissue_dominance"] = expr_data.get("tissue_expression", {})
                
                # Identify dominant tissues
                if results["tissue_dominance"]:
                    sorted_tissues = sorted(
                        results["tissue_dominance"].items(),
                        key=lambda x: x[1] if isinstance(x[1], (int, float)) else 0,
                        reverse=True
                    )
                    results["top_tissues"] = [t[0] for t in sorted_tissues[:5]]
            
            # 3. Map top tissues to anatomy
            top_tissues = results.get("top_tissues", ["brain", "liver", "heart"])
            for tissue in top_tissues[:3]:
                anatomy_response = requests.get(
                    f"{self.apis['anatomics']}/analyze/organ/{tissue}",
                    timeout=self.timeout
                )
                if anatomy_response.status_code == 200:
                    anatomy_data = anatomy_response.json()
                    results["anatomy_mappings"].append({
                        "tissue": tissue,
                        "anatomical_structures": anatomy_data.get("anatomical_structure", {})
                    })
            
            # Add user context if available
            if user_id:
                results["user_context"] = self.get_user_digital_twin(user_id)
            
            return results
            
        except Exception as e:
            return {"error": f"Splice impact analysis failed: {e}"}
    
    def phenotype_to_differential(self, phenotypes: List[str], user_id: str = None) -> Dict[str, Any]:
        """
        Map phenotypes (HPO terms or symptoms) to candidate diseases, genes, and anatomy.
        Uses: HPO + MONDO + gene-disease links from Neo4j ontology_db
        """
        try:
            results = {
                "input_phenotypes": phenotypes,
                "timestamp": datetime.now().isoformat(),
                "ranked_diseases": [],
                "matching_phenotypes": {},
                "implicated_genes": [],
                "anatomy_focus": []
            }
            
            # Common phenotype to HPO mapping for convenience
            symptom_to_hpo = {
                "seizures": "HP:0001250",
                "hypotonia": "HP:0001252",
                "intellectual disability": "HP:0001249",
                "spasticity": "HP:0001257",
                "ataxia": "HP:0001251",
                "muscle weakness": "HP:0001324",
                "developmental delay": "HP:0001263",
                "short stature": "HP:0004322",
                "obesity": "HP:0001513",
                "hearing loss": "HP:0000365",
                "vision loss": "HP:0000505",
                "cardiac arrhythmia": "HP:0011675",
                "hypertension": "HP:0000822",
                "kidney stones": "HP:0000787",
                "thyroid nodule": "HP:0002890",
                "pheochromocytoma": "HP:0002666",
                "medullary thyroid carcinoma": "HP:0002668"
            }
            
            # Normalize phenotypes - convert symptoms to HPO if possible
            normalized_hpo = []
            for pheno in phenotypes:
                if pheno.startswith("HP:"):
                    normalized_hpo.append(pheno)
                elif pheno.lower() in symptom_to_hpo:
                    normalized_hpo.append(symptom_to_hpo[pheno.lower()])
                else:
                    # Keep as-is for text search
                    normalized_hpo.append(pheno)
            
            results["normalized_hpo"] = normalized_hpo
            
            # Query anatomics API for phenotype-disease mapping (uses Neo4j)
            for hpo in normalized_hpo[:5]:  # Limit to avoid overload
                try:
                    pheno_response = requests.get(
                        f"{self.apis['anatomics']}/analyze/phenotype/{hpo}",
                        timeout=self.timeout
                    )
                    if pheno_response.status_code == 200:
                        pheno_data = pheno_response.json()
                        results["matching_phenotypes"][hpo] = pheno_data
                        
                        # Extract diseases and genes
                        if "associated_diseases" in pheno_data:
                            results["ranked_diseases"].extend(pheno_data["associated_diseases"])
                        if "implicated_genes" in pheno_data:
                            results["implicated_genes"].extend(pheno_data["implicated_genes"])
                except:
                    pass
            
            # Also search literature for phenotype combinations
            search_query = " AND ".join(phenotypes[:3])
            lit_response = requests.get(
                f"{self.apis['literature']}/search/literature/{search_query}",
                timeout=self.timeout
            )
            if lit_response.status_code == 200:
                results["literature_support"] = lit_response.json()
            
            # Get population disease risk data for top candidate diseases
            if results["ranked_diseases"]:
                top_disease = results["ranked_diseases"][0] if isinstance(results["ranked_diseases"][0], str) else results["ranked_diseases"][0].get("name", "")
                if top_disease:
                    risk_response = requests.get(
                        f"{self.apis['populomics']}/analyze/disease_risk/{top_disease}",
                        timeout=self.timeout
                    )
                    if risk_response.status_code == 200:
                        results["population_risk"] = risk_response.json()
            
            # Deduplicate genes
            results["implicated_genes"] = list(set(results["implicated_genes"]))[:10]
            
            # Map top genes to anatomy
            for gene in results["implicated_genes"][:3]:
                gene_response = requests.get(
                    f"{self.apis['genomics']}/analyze/gene/{gene}",
                    timeout=self.timeout
                )
                if gene_response.status_code == 200:
                    gene_data = gene_response.json()
                    if "expression_profile" in gene_data:
                        top_tissue = list(gene_data["expression_profile"].keys())[:1]
                        if top_tissue:
                            results["anatomy_focus"].extend(top_tissue)
            
            results["anatomy_focus"] = list(set(results["anatomy_focus"]))
            
            # Add user context if available
            if user_id:
                results["user_context"] = self.get_user_digital_twin(user_id)
            
            return results
            
        except Exception as e:
            return {"error": f"Phenotype differential analysis failed: {e}"}
    
    def analyze_regulatory_variant(self, variant_id: str, user_id: str = None) -> Dict[str, Any]:
        """
        Interpret non-coding/regulatory variants using ENCODE data.
        Returns: overlapping regulatory elements, target genes, expression impact, phenotype priors
        Uses: ENCODE (1.31M) + reg→gene links + GTEx + MONDO/HPO
        """
        try:
            results = {
                "variant_id": variant_id,
                "timestamp": datetime.now().isoformat(),
                "encode_elements": [],
                "target_genes": [],
                "expression_impact": {},
                "phenotype_priors": []
            }
            
            # 1. Get variant details from genomics API
            variant_response = requests.get(
                f"{self.apis['genomics']}/analyze/variant/{variant_id}",
                timeout=self.timeout
            )
            if variant_response.status_code == 200:
                variant_data = variant_response.json()
                results["variant_data"] = variant_data
                
                # Extract chromosome and position for regulatory lookup
                chrom = variant_data.get("chromosome", "")
                pos = variant_data.get("position", 0)
                results["genomic_location"] = {"chrom": chrom, "pos": pos}
            
            # 2. Query regulatory elements from genomics API (ENCODE data)
            regulatory_response = requests.get(
                f"{self.apis['genomics']}/analyze/regulatory/{variant_id}",
                timeout=self.timeout
            )
            if regulatory_response.status_code == 200:
                reg_data = regulatory_response.json()
                results["encode_elements"] = reg_data.get("regulatory_elements", [])
                results["target_genes"] = reg_data.get("target_genes", [])
            
            # 3. For each target gene, get expression data
            for gene_info in results["target_genes"][:5]:
                gene_name = gene_info if isinstance(gene_info, str) else gene_info.get("gene", "")
                if gene_name:
                    expr_response = requests.get(
                        f"{self.apis['metabolics']}/analyze/expression/{gene_name}",
                        timeout=self.timeout
                    )
                    if expr_response.status_code == 200:
                        expr_data = expr_response.json()
                        results["expression_impact"][gene_name] = expr_data.get("tissue_expression", {})
            
            # 4. Get phenotype associations for target genes via anatomics
            for gene_info in results["target_genes"][:3]:
                gene_name = gene_info if isinstance(gene_info, str) else gene_info.get("gene", "")
                if gene_name:
                    pheno_response = requests.get(
                        f"{self.apis['anatomics']}/analyze/gene_phenotypes/{gene_name}",
                        timeout=self.timeout
                    )
                    if pheno_response.status_code == 200:
                        pheno_data = pheno_response.json()
                        results["phenotype_priors"].append({
                            "gene": gene_name,
                            "phenotypes": pheno_data.get("associated_phenotypes", []),
                            "diseases": pheno_data.get("associated_diseases", [])
                        })
            
            # 5. Classify the regulatory element type
            if results["encode_elements"]:
                element_types = [e.get("type", "unknown") for e in results["encode_elements"] if isinstance(e, dict)]
                results["element_summary"] = {
                    "enhancers": sum(1 for t in element_types if "enhancer" in t.lower()),
                    "promoters": sum(1 for t in element_types if "promoter" in t.lower()),
                    "silencers": sum(1 for t in element_types if "silencer" in t.lower()),
                    "insulators": sum(1 for t in element_types if "insulator" in t.lower()),
                    "other": sum(1 for t in element_types if not any(x in t.lower() for x in ["enhancer", "promoter", "silencer", "insulator"]))
                }
            
            # Add user context if available
            if user_id:
                results["user_context"] = self.get_user_digital_twin(user_id)
            
            return results
            
        except Exception as e:
            return {"error": f"Regulatory variant analysis failed: {e}"}
    
    def _extract_gene_names(self, query: str) -> List[str]:
        """Extract gene names from user query"""
        # Simple gene name extraction (could be enhanced with NLP)
        common_genes = [
            'BRCA1', 'BRCA2', 'TP53', 'CFTR', 'APOE', 'EGFR', 'MYC', 'KRAS',
            'PKD1', 'PKD2', 'SCN5A', 'KCNQ1', 'KCNH2', 'RYR2', 'CACNA1C',
            'CYP2D6', 'CYP2C19', 'CYP3A4', 'DPYD', 'TPMT', 'FOXP2'
        ]
        
        found_genes = []
        query_upper = query.upper()
        
        for gene in common_genes:
            if gene in query_upper:
                found_genes.append(gene)
        
        return found_genes[:5]  # Limit to 5 genes to avoid overload
    
    def _get_risk_genes_for_condition(self, condition: str) -> List[str]:
        """Get relevant genes for specific health conditions"""
        condition_genes = {
            "cancer": ['BRCA1', 'BRCA2', 'TP53', 'EGFR', 'MYC'],
            "cardiovascular": ['APOE', 'LDLR', 'PCSK9', 'SCN5A', 'KCNQ1'],
            "diabetes": ['TCF7L2', 'PPARG', 'KCNJ11', 'HNF1A'],
            "alzheimer": ['APOE', 'APP', 'PSEN1', 'PSEN2'],
            "default": ['BRCA1', 'TP53', 'APOE', 'CFTR']
        }
        
        return condition_genes.get(condition.lower() if condition else "default", condition_genes["default"])
    
    def execute_tool_from_response(self, tool_name: str, tool_params: Dict, user_id: str) -> Dict[str, Any]:
        """Execute specific tool based on model's request"""
        try:
            if tool_name == "get_user_digital_twin":
                return self.get_user_digital_twin(user_id)
            
            elif tool_name == "analyze_gene":
                gene_symbol = tool_params.get("gene_symbol")
                return self.analyze_gene(gene_symbol, user_id)
            
            elif tool_name == "analyze_variant":
                variant_id = tool_params.get("variant_id")
                return self.analyze_variant(variant_id, user_id)
            
            elif tool_name == "cross_axis_analysis":
                query = tool_params.get("query")
                axes = tool_params.get("axes", [])
                return self.cross_axis_analysis(query, axes, user_id)
            
            elif tool_name == "risk_assessment":
                condition = tool_params.get("condition")
                return self.risk_assessment(user_id, condition)
            
            elif tool_name == "get_user_genomics":
                gene_filter = tool_params.get("gene_filter")
                return self.get_user_genomics(user_id, gene_filter)
                
            elif tool_name == "analyze_organ":
                organ_name = tool_params.get("organ_name")
                try:
                    response = requests.get(
                        f"{self.apis['anatomics']}/analyze/organ/{organ_name}",
                        timeout=self.timeout
                    )
                    return response.json() if response.status_code == 200 else {"error": f"Organ analysis failed: {response.status_code}"}
                except Exception as e:
                    return {"error": f"Organ analysis error: {e}"}

            elif tool_name == "search_literature":
                topic = tool_params.get("topic")
                try:
                    response = requests.get(
                        f"{self.apis['literature']}/search/literature/{topic}",
                        timeout=self.timeout
                    )
                    return response.json() if response.status_code == 200 else {"error": f"Literature search failed: {response.status_code}"}
                except Exception as e:
                    return {"error": f"Literature search error: {e}"}
            
            elif tool_name == "get_metabolic_profile":
                user = tool_params.get("user_id", user_id)
                return self.get_metabolic_profile(user)
            
            elif tool_name == "get_drug_metabolism":
                drug = tool_params.get("drug_name")
                return self.get_drug_metabolism(drug)
            
            elif tool_name == "get_environmental_risk":
                location = tool_params.get("location")
                return self.get_environmental_risk(location)
            
            elif tool_name == "get_disease_risk":
                disease = tool_params.get("disease")
                return self.get_disease_risk(disease)
            
            # NEW HIGH-VALUE TOOLS
            elif tool_name == "analyze_splice_impact":
                gene_or_variant = tool_params.get("gene_or_variant")
                return self.analyze_splice_impact(gene_or_variant, user_id)
            
            elif tool_name == "phenotype_to_differential":
                phenotypes = tool_params.get("phenotypes", [])
                return self.phenotype_to_differential(phenotypes, user_id)
            
            elif tool_name == "analyze_regulatory_variant":
                variant_id = tool_params.get("variant_id")
                return self.analyze_regulatory_variant(variant_id, user_id)
            
            else:
                return {"error": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            return {"error": f"Tool execution failed: {e}"}
    
    def _query_dna_expert_model(self, prompt: str) -> str:
        """Query the DNA expert model via LM Studio server"""
        try:
            response = requests.post(
                f"{self.model_url}/v1/chat/completions",
                json={
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": MODEL_CONFIG["max_tokens"],
                    "temperature": MODEL_CONFIG["temperature"],
                    "top_p": MODEL_CONFIG["top_p"],
                    "stop": MODEL_CONFIG["stop"]
                },
                timeout=120  # Longer timeout for complex analysis
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                return f"Model query failed: {response.status_code}"
                
        except Exception as e:
            return f"Model query error: {e}"
    
    def _execute_identified_tools(self, model_response: str, user_id: str) -> str:
        """Parse model response for tool calls and execute them"""
        # This would parse the model response for tool calls
        # For now, return the response as-is
        # In a full implementation, this would:
        # 1. Parse response for tool call requests
        # 2. Execute requested tools
        # 3. Integrate results back into response
        
        return model_response
    
    def _enhance_response_with_metadata(self, response: str, user_context: Dict, original_query: str) -> Dict[str, Any]:
        """Add metadata and confidence information to response"""
        
        completeness = user_context.get("completeness_score", 0)
        confidence_level = "high" if completeness > 0.8 else "medium" if completeness > 0.5 else "low"
        
        return {
            "response": response,
            "user_id": user_context.get("user_id"),
            "query": original_query,
            "confidence_level": confidence_level,
            "data_completeness": f"{completeness*100:.1f}%",
            "data_sources": self._identify_data_sources(user_context),
            "recommendations": self._generate_recommendations(response, user_context),
            "timestamp": datetime.now().isoformat()
        }
    
    def _identify_data_sources(self, user_context: Dict) -> Dict[str, str]:
        """Identify what data sources were used"""
        data_sources = user_context.get("data_sources", {})
        
        source_summary = {}
        for category, source in data_sources.items():
            if source == "user_specific":
                source_summary[category] = "Your personal data"
            elif source == "population_matched":
                source_summary[category] = "Population data for your ancestry"
            elif source == "reference_model":
                source_summary[category] = "General reference data (Adam/Eve model)"
            else:
                source_summary[category] = "Unknown source"
        
        return source_summary
    
    def _generate_recommendations(self, response: str, user_context: Dict) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        completeness = user_context.get("completeness_score", 0)
        
        if completeness < 0.5:
            recommendations.append("Upload DNA data for more personalized analysis")
        
        if completeness < 0.7:
            recommendations.append("Complete health questionnaire for better risk assessment")
        
        if "genetic counseling" in response.lower():
            recommendations.append("Consider consulting with a genetic counselor")
        
        if "healthcare provider" in response.lower():
            recommendations.append("Discuss these findings with your healthcare provider")
        
        return recommendations
    
    def _update_conversation_history(self, conversation_id: str, query: str, response: Dict[str, Any]):
        """Update conversation history for context"""
        if conversation_id not in self.conversation_history:
            self.conversation_history[conversation_id] = []
        
        self.conversation_history[conversation_id].append({
            "query": query,
            "response": response["response"],
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only recent history (last 20 exchanges)
        if len(self.conversation_history[conversation_id]) > 20:
            self.conversation_history[conversation_id] = self.conversation_history[conversation_id][-20:]
