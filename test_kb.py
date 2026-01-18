#!/usr/bin/env python3
"""
Test script to verify the knowledge base fallback functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nl2sql.phidata_setup import get_knowledge_base

def test_knowledge_base():
    """Test if knowledge base can be created with fallback"""
    try:
        print("Testing knowledge base creation...")
        kb = get_knowledge_base()
        print(f"✅ Knowledge base created successfully: {type(kb)}")
        return True
    except Exception as e:
        print(f"❌ Knowledge base creation failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_knowledge_base()
    sys.exit(0 if success else 1)