import clickhouse_connect

client = clickhouse_connect.get_client(host='localhost', port=8123, username='genomics', password='genomics123')

print("CHECKING CURRENT SPLICEAI STATUS")
print("="*40)

# Check what we have
total = client.query("SELECT COUNT(*) FROM genomics_db.spliceai_full").result_rows[0][0]
print(f"Current SpliceAI rows: {total:,}")

# Check if we have useful data for key genes
genes_to_check = ['BRCA1', 'BRCA2', 'TP53', 'CFTR']
for gene in genes_to_check:
    count = client.query(f"SELECT COUNT(*) FROM genomics_db.spliceai_full WHERE gene_symbol = '{gene}'").result_rows[0][0]
    print(f"{gene}: {count:,} splice variants")

# Check score distribution
high_scores = client.query("SELECT COUNT(*) FROM genomics_db.spliceai_full WHERE max_score > 0.5").result_rows[0][0]
medium_scores = client.query("SELECT COUNT(*) FROM genomics_db.spliceai_full WHERE max_score > 0.2").result_rows[0][0]

print(f"\nScore distribution:")
print(f"High impact (>0.5): {high_scores:,}")
print(f"Medium impact (>0.2): {medium_scores:,}")

# Calculate completion
completion = (total / 3_433_300_000) * 100
print(f"\nCompletion: {completion:.2f}% of full 3.43B dataset")

if completion > 5:
    print("SUBSTANTIAL: Good dataset for testing APIs")
elif completion > 1:
    print("MODERATE: Some data available")
else:
    print("LIMITED: Very small dataset")

print(f"\nOPTIONS:")
print(f"1. Use current {total:,} rows for API testing")
print(f"2. Continue migration for full 3.43B dataset (~11 hours)")
print(f"3. Stop here and test with what we have")
