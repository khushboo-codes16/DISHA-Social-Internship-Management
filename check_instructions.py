#!/usr/bin/env python3
"""Check if instructions exist in database"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import MongoDB

print("🔄 Connecting to database...")
db = MongoDB()

if not db.is_connected():
    print("❌ Failed to connect to database")
    sys.exit(1)

print("✅ Connected to database\n")

# Check for instructions
instruction = db.get_active_instruction()

if instruction:
    print("✅ Instruction found!")
    print(f"📝 Title: {instruction.get('title', 'N/A')}")
    print(f"📄 Content length: {len(instruction.get('content', ''))} characters")
    print(f"🔄 Updated: {instruction.get('updated_at', 'N/A')}")
    print(f"✓ Active: {instruction.get('is_active', False)}")
    print("\n📄 Content preview (first 200 chars):")
    print(instruction.get('content', 'No content')[:200])
else:
    print("❌ No instruction found in database")
    print("\n💡 To add default instructions, run:")
    print("   python3 add_default_instructions.py")
