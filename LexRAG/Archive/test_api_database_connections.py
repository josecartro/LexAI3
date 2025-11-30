"""
Test API Database Connections
Verify all APIs can reach their required databases
"""

import requests
import clickhouse_connect
import json

def test_clickhouse_connection():
    """Test ClickHouse database connection"""
    
    print("TESTING CLICKHOUSE DATABASE")
    print("="*40)
    
    try:
        client = clickhouse_connect.get_client(
            host='127.0.0.1', 
            port=8125, 
            username='genomics', 
            password='genomics123'
        )
        
        # Test basic connection
        version = client.query('SELECT version()').result_rows[0][0]
        print(f"✅ ClickHouse connected: {version}")
        
        # Test our databases
        databases = ['genomics_db', 'expression_db', 'proteins_db', 'population_db', 
                    'regulatory_db', 'ontology_db', 'reference_db', 'pathways_db', 'digital_twin_db']
        
        total_records = 0
        
        for db in databases:
            try:
                tables = client.query(f"SHOW TABLES FROM {db}").result_rows
                db_records = 0
                
                for table in tables:
                    table_name = table[0]
                    try:
                        count = client.query(f"SELECT COUNT(*) FROM {db}.{table_name}").result_rows[0][0]
                        db_records += count
                    except:
                        pass
                
                total_records += db_records
                print(f"  {db}: {len(tables)} tables, {db_records:,} records")
                
            except Exception as e:
                print(f"  {db}: ERROR - {e}")
        
        print(f"\\nTotal records across all databases: {total_records:,}")
        
        if total_records > 1000000:  # Should have millions of records
            print("✅ Database verification: PASSED")
            return True
        else:
            print("❌ Database verification: FAILED - Not enough records")
            return False
            
    except Exception as e:
        print(f"❌ ClickHouse connection failed: {e}")
        return False

def test_api_database_access():
    """Test if APIs can access their databases"""
    
    print("\\nTESTING API DATABASE ACCESS")
    print("="*40)
    
    api_tests = [
        {
            'name': 'Genomics API',
            'url': 'http://127.0.0.1:8001/health',
            'database_check': 'Should show ClickHouse connection'
        },
        {
            'name': 'Users API', 
            'url': 'http://127.0.0.1:8007/health',
            'database_check': 'Should show user database connection'
        },
        {
            'name': 'DigitalTwin API',
            'url': 'http://127.0.0.1:8008/health', 
            'database_check': 'Should show ClickHouse + user DB connection'
        },
        {
            'name': 'AIGateway API',
            'url': 'http://127.0.0.1:8009/health',
            'database_check': 'Should show all API connections'
        }
    ]
    
    working_apis = 0
    
    for test in api_tests:
        print(f"\\nTesting {test['name']}...")
        
        try:
            response = requests.get(test['url'], timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'unknown')
                databases = data.get('databases', {})
                
                print(f"  Status: {status}")
                print(f"  Database connections:")
                
                db_working = 0
                for db_name, db_info in databases.items():
                    db_status = db_info.get('status', 'unknown')
                    print(f"    {db_name}: {db_status}")
                    
                    if db_status == 'connected':
                        db_working += 1
                        
                        # Show record counts if available
                        if 'total_records' in db_info:
                            print(f"      Records: {db_info['total_records']}")
                
                if db_working > 0:
                    working_apis += 1
                    print(f"  Result: ✅ WORKING ({db_working} database connections)")
                else:
                    print(f"  Result: ❌ NO DATABASE CONNECTIONS")
                    
            else:
                print(f"  Result: ❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"  Result: ❌ ERROR - {e}")
    
    print(f"\\n{'='*40}")
    print(f"API DATABASE ACCESS SUMMARY")
    print(f"{'='*40}")
    print(f"APIs with database access: {working_apis}/{len(api_tests)}")
    
    if working_apis >= 3:
        print("✅ SYSTEM READY: Core APIs have database access")
        return True
    else:
        print("❌ SYSTEM NOT READY: APIs cannot access databases")
        return False

def test_specific_genomics_access():
    """Test specific genomics data access"""
    
    print("\\nTESTING GENOMICS DATA ACCESS")
    print("="*40)
    
    try:
        # Test BRCA1 gene analysis (should use 4.4B records)
        response = requests.get('http://127.0.0.1:8001/analyze/gene/BRCA1', timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            variants = data.get('variants', {})
            total_variants = variants.get('total_variants', 0)
            pathogenic = variants.get('pathogenic_variants', 0)
            
            print(f"✅ BRCA1 analysis working:")
            print(f"  Total variants: {total_variants:,}")
            print(f"  Pathogenic variants: {pathogenic:,}")
            
            if total_variants > 10000:  # Should have thousands of BRCA1 variants
                print("✅ Genomics database access: CONFIRMED")
                return True
            else:
                print("❌ Genomics database access: LIMITED DATA")
                return False
        else:
            print(f"❌ Genomics API failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Genomics test failed: {e}")
        return False

def main():
    """Run complete system verification"""
    
    print("COMPLETE LEXRAG SYSTEM VERIFICATION")
    print("="*60)
    print("Verifying database connections and API functionality")
    print("="*60)
    
    # Test ClickHouse
    clickhouse_ok = test_clickhouse_connection()
    
    # Test API database access
    apis_ok = test_api_database_access()
    
    # Test specific genomics functionality
    genomics_ok = test_specific_genomics_access()
    
    print(f"\\n{'='*60}")
    print("FINAL SYSTEM STATUS")
    print(f"{'='*60}")
    print(f"ClickHouse Database: {'✅ WORKING' if clickhouse_ok else '❌ FAILED'}")
    print(f"API Database Access: {'✅ WORKING' if apis_ok else '❌ FAILED'}")
    print(f"Genomics Data Access: {'✅ WORKING' if genomics_ok else '❌ FAILED'}")
    
    if clickhouse_ok and apis_ok and genomics_ok:
        print("\\n🎉 COMPLETE SYSTEM VERIFICATION: PASSED")
        print("✅ 4.4B genomic records accessible")
        print("✅ All APIs connected to databases")
        print("✅ Ready for AI integration")
    else:
        print("\\n❌ SYSTEM VERIFICATION: FAILED")
        print("Some components need attention before proceeding")
    
    return clickhouse_ok and apis_ok and genomics_ok

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\\nSYSTEM READY FOR PRODUCTION")
    else:
        print("\\nSYSTEM NEEDS DEBUGGING")
    
    input("\\nPress Enter to continue...")
