import duckdb

print("DETAILED GENOMICS DATA ANALYSIS")
print("="*80)

conn = duckdb.connect("../../data/databases/genomic_knowledge/genomic_knowledge.duckdb", read_only=True)

# Check what we're currently using
print("\nCURRENT TABLES USED BY LEXAPI_GENOMICS:")
current_tables = ["clinvar_full_production", "gencode_v44_transcripts"]

for table in current_tables:
    try:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        columns = conn.execute(f"DESCRIBE {table}").fetchall()
        print(f"  {table}:")
        print(f"    Rows: {count:,}")
        print(f"    Columns: {len(columns)}")
        print(f"    Key columns: {[col[0] for col in columns[:5]]}")
    except Exception as e:
        print(f"  {table}: ERROR - {e}")

print("\nMASSIVE PRODUCTION TABLES NOT USED:")
massive_tables = [
    "spliceai_scores_production",
    "spliceai_full_production", 
    "dbsnp_parquet_production",
    "alphafold_clinical_variant_impact",
    "alphafold_variant_protein_analysis"
]

for table in massive_tables:
    try:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        columns = conn.execute(f"DESCRIBE {table}").fetchall()
        print(f"  {table}:")
        print(f"    Rows: {count:,}")
        print(f"    Columns: {len(columns)}")
        print(f"    Key columns: {[col[0] for col in columns[:5]]}")
        
        # Check for connection columns
        connection_cols = [col[0] for col in columns if any(word in col[0].lower() for word in ['gene', 'variant', 'protein', 'tissue', 'id'])]
        print(f"    Connection columns: {connection_cols[:8]}")
        
    except Exception as e:
        print(f"  {table}: ERROR - {e}")

print("\nSEARCHING FOR CONNECTION/RELATIONSHIP TABLES:")
all_tables = conn.execute("SHOW TABLES").fetchall()
table_names = [t[0] for t in all_tables]

connection_keywords = ["connection", "relationship", "mapping", "link", "association", "interaction", "pathway", "network"]
connection_tables = []

for table in table_names:
    for keyword in connection_keywords:
        if keyword in table.lower():
            connection_tables.append(table)
            break

print(f"Found {len(connection_tables)} potential connection tables:")
for table in connection_tables:
    try:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        columns = conn.execute(f"DESCRIBE {table}").fetchall()
        print(f"  {table}: {count:,} rows, {len(columns)} cols")
        print(f"    Columns: {[col[0] for col in columns[:6]]}")
    except Exception as e:
        print(f"  {table}: ERROR - {e}")

conn.close()

print("\n" + "="*80)
print("ANALYSIS COMPLETE - Check for missing production tables and connections")
print("="*80)

