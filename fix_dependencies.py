#!/usr/bin/env python3
"""
Script to fix dependency conflicts in the NL2SQL project
"""
import subprocess
import sys

def run_command(cmd):
    """Run a command and return the result"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd.split(), capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"Error: {result.stderr}")
    return result.returncode == 0

def main():
    print("Fixing dependency conflicts...")
    
    # Uninstall conflicting packages
    print("1. Removing conflicting pinecone packages...")
    run_command("pip uninstall pinecone-plugin-assistant -y")
    run_command("pip uninstall pinecone-plugin-interface -y")
    run_command("pip uninstall pinecone -y")
    
    # Install compatible pinecone version
    print("2. Installing compatible pinecone version...")
    run_command("pip install pinecone-client==3.2.2")
    
    # Check for conflicts
    print("3. Checking for remaining conflicts...")
    run_command("pip check")
    
    print("Done!")

if __name__ == "__main__":
    main()