"""
Find Working ClickHouse Container
Test all ClickHouse containers to find which one has our 4.4B records
"""

import subprocess
import json

def find_working_clickhouse():
    """Find which ClickHouse container has our data"""
    
    print("FINDING WORKING CLICKHOUSE CONTAINER")
    print("="*50)
    
    # Get all ClickHouse containers
    try:
        result = subprocess.run(['docker', 'ps', '-a', '--filter', 'name=clickhouse', '--format', '{{.Names}}\t{{.Status}}\t{{.Ports}}'], 
                               capture_output=True, text=True)
        
        if result.returncode != 0:
            print("ERROR: Could not list Docker containers")
            return None
        
        containers = []
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                parts = line.split('\t')
                if len(parts) >= 2:
                    containers.append({
                        'name': parts[0],
                        'status': parts[1],
                        'ports': parts[2] if len(parts) > 2 else 'No ports'
                    })
        
        print(f"Found {len(containers)} ClickHouse containers:")
        for container in containers:
            print(f"  {container['name']}: {container['status']}")
            print(f"    Ports: {container['ports']}")
        
        # Test each running container for our data
        working_containers = []
        
        for container in containers:
            if 'Up' in container['status']:
                print(f"\\nTesting {container['name']} for our data...")
                
                # Test if container has our genomics data
                test_cmd = ['docker', 'exec', container['name'], 'clickhouse-client', 
                           '--query', 'SELECT COUNT(*) FROM genomics_db.clinvar_variants']
                
                try:
                    test_result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=10)
                    
                    if test_result.returncode == 0:
                        count = int(test_result.stdout.strip())
                        print(f"  SUCCESS: {count:,} ClinVar variants found")
                        
                        if count > 1000000:  # Should have millions
                            working_containers.append({
                                'name': container['name'],
                                'clinvar_count': count,
                                'status': container['status'],
                                'ports': container['ports']
                            })
                        else:
                            print(f"  WARNING: Only {count:,} variants (expected millions)")
                    else:
                        print(f"  FAILED: Cannot query database - {test_result.stderr[:100]}")
                        
                except subprocess.TimeoutExpired:
                    print("  TIMEOUT: Container not responding")
                except Exception as e:
                    print(f"  ERROR: {e}")
            else:
                print(f"\\nSkipping {container['name']} - not running")
        
        # Report results
        print(f"\\n{'='*50}")
        print("WORKING CLICKHOUSE CONTAINERS")
        print(f"{'='*50}")
        
        if working_containers:
            for container in working_containers:
                print(f"✅ {container['name']}")
                print(f"   Status: {container['status']}")
                print(f"   Ports: {container['ports']}")
                print(f"   ClinVar variants: {container['clinvar_count']:,}")
                print(f"   Recommendation: USE THIS CONTAINER")
            
            # Return the best container
            best_container = max(working_containers, key=lambda x: x['clinvar_count'])
            print(f"\\nBEST CONTAINER: {best_container['name']}")
            print(f"Has {best_container['clinvar_count']:,} ClinVar variants")
            
            return best_container['name']
        else:
            print("❌ NO WORKING CONTAINERS FOUND")
            print("All containers either:")
            print("  - Not running")
            print("  - Don't have genomics_db database")
            print("  - Have insufficient data")
            
            return None
            
    except Exception as e:
        print(f"ERROR: {e}")
        return None

if __name__ == "__main__":
    print("Searching for ClickHouse container with 4.4B genomic records...")
    
    working_container = find_working_clickhouse()
    
    if working_container:
        print(f"\\n🎉 FOUND WORKING CONTAINER: {working_container}")
        print("Use this container name in your startup scripts")
    else:
        print("\\n❌ NO WORKING CONTAINER FOUND")
        print("May need to check container data or start fresh")
    
    input("\\nPress Enter to continue...")
