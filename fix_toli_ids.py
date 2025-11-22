#!/usr/bin/env python3
"""
Script to check and fix toli_id format in programs collection
"""

from app.database import MongoDB
from bson import ObjectId

def check_and_fix_toli_ids():
    """Check toli_id format in all programs and fix if needed"""
    db = MongoDB()
    
    print("=" * 80)
    print("CHECKING TOLI_ID FORMAT IN PROGRAMS")
    print("=" * 80)
    
    # Get all programs
    all_programs = db.get_all_programs()
    print(f"\n📊 Total programs in database: {len(all_programs)}")
    
    if not all_programs:
        print("❌ No programs found in database")
        return
    
    # Check toli_id format
    string_format = 0
    objectid_format = 0
    none_format = 0
    
    programs_to_fix = []
    
    for program in all_programs:
        toli_id = program.get('toli_id')
        
        if toli_id is None:
            none_format += 1
            print(f"⚠️ Program '{program.get('title')}' has no toli_id")
        elif isinstance(toli_id, str):
            string_format += 1
            programs_to_fix.append(program)
        elif isinstance(toli_id, ObjectId):
            objectid_format += 1
        else:
            print(f"⚠️ Unknown format for program '{program.get('title')}': {type(toli_id)}")
    
    print(f"\n📈 Format Statistics:")
    print(f"   String format: {string_format}")
    print(f"   ObjectId format: {objectid_format}")
    print(f"   None/Missing: {none_format}")
    
    # Show sample data
    if all_programs:
        sample = all_programs[0]
        print(f"\n📋 Sample Program:")
        print(f"   Title: {sample.get('title')}")
        print(f"   Toli ID: {sample.get('toli_id')}")
        print(f"   Toli ID Type: {type(sample.get('toli_id'))}")
        print(f"   Student ID: {sample.get('student_id')}")
        print(f"   Toli Name: {sample.get('toli_name', 'N/A')}")
    
    # Check if conversion is needed
    if string_format > 0:
        print(f"\n⚠️ Found {string_format} programs with string toli_id")
        print("ℹ️ This is actually OKAY! The query has been updated to handle both formats.")
        print("ℹ️ No database changes needed.")
    
    if objectid_format > 0:
        print(f"\n✅ Found {objectid_format} programs with ObjectId toli_id")
    
    # Show toli mapping
    print(f"\n📊 Programs by Toli:")
    toli_counts = {}
    for program in all_programs:
        toli_id = str(program.get('toli_id', 'Unknown'))
        toli_name = program.get('toli_name', 'Unknown')
        key = f"{toli_name} ({toli_id[:8]}...)"
        toli_counts[key] = toli_counts.get(key, 0) + 1
    
    for toli, count in sorted(toli_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {toli}: {count} programs")
    
    print("\n" + "=" * 80)
    print("✅ CHECK COMPLETE")
    print("=" * 80)
    print("\nℹ️ The database query has been updated to handle both string and ObjectId formats.")
    print("ℹ️ Programs should now display correctly in admin view.")
    print("\n💡 To test:")
    print("   1. Login as admin")
    print("   2. Go to Manage Tolis")
    print("   3. Click on any toli")
    print("   4. Click 'View Programs'")
    print("   5. Programs should now display!")

if __name__ == '__main__':
    check_and_fix_toli_ids()
