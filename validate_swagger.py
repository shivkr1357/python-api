#!/usr/bin/env python3
"""
Script to validate Swagger/OpenAPI specification files
"""

import json
import yaml
import sys
from pathlib import Path

def validate_yaml_swagger(file_path):
    """Validate YAML Swagger file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            yaml_content = yaml.safe_load(file)
        
        # Basic validation
        required_fields = ['openapi', 'info', 'paths']
        for field in required_fields:
            if field not in yaml_content:
                print(f"❌ Missing required field: {field}")
                return False
        
        # Check OpenAPI version
        if yaml_content['openapi'] != '3.0.3':
            print(f"⚠️  OpenAPI version is {yaml_content['openapi']}, expected 3.0.3")
        
        # Check info
        info = yaml_content['info']
        if 'title' not in info or 'version' not in info:
            print("❌ Missing required info fields: title or version")
            return False
        
        # Check paths
        if not yaml_content['paths']:
            print("⚠️  No paths defined in the specification")
        
        print(f"✅ YAML Swagger file '{file_path}' is valid")
        return True
        
    except yaml.YAMLError as e:
        print(f"❌ YAML parsing error in {file_path}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error validating {file_path}: {e}")
        return False

def validate_json_swagger(file_path):
    """Validate JSON Swagger file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            json_content = json.load(file)
        
        # Basic validation
        required_fields = ['openapi', 'info', 'paths']
        for field in required_fields:
            if field not in json_content:
                print(f"❌ Missing required field: {field}")
                return False
        
        # Check OpenAPI version
        if json_content['openapi'] != '3.0.3':
            print(f"⚠️  OpenAPI version is {json_content['openapi']}, expected 3.0.3")
        
        # Check info
        info = json_content['info']
        if 'title' not in info or 'version' not in info:
            print("❌ Missing required info fields: title or version")
            return False
        
        # Check paths
        if not json_content['paths']:
            print("⚠️  No paths defined in the specification")
        
        print(f"✅ JSON Swagger file '{file_path}' is valid")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error in {file_path}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error validating {file_path}: {e}")
        return False

def compare_swagger_files(yaml_path, json_path):
    """Compare YAML and JSON Swagger files"""
    try:
        # Load YAML file
        with open(yaml_path, 'r', encoding='utf-8') as file:
            yaml_content = yaml.safe_load(file)
        
        # Load JSON file
        with open(json_path, 'r', encoding='utf-8') as file:
            json_content = json.load(file)
        
        # Convert both to JSON for comparison
        yaml_json = json.dumps(yaml_content, sort_keys=True, indent=2)
        json_json = json.dumps(json_content, sort_keys=True, indent=2)
        
        if yaml_json == json_json:
            print("✅ YAML and JSON Swagger files are identical")
            return True
        else:
            print("❌ YAML and JSON Swagger files are different")
            return False
            
    except Exception as e:
        print(f"❌ Error comparing files: {e}")
        return False

def main():
    """Main validation function"""
    print("🔍 Swagger/OpenAPI Specification Validator")
    print("=" * 50)
    
    yaml_file = Path("swagger.yaml")
    json_file = Path("swagger.json")
    
    # Check if files exist
    if not yaml_file.exists():
        print(f"❌ YAML file not found: {yaml_file}")
        return False
    
    if not json_file.exists():
        print(f"❌ JSON file not found: {json_file}")
        return False
    
    # Validate files
    yaml_valid = validate_yaml_swagger(yaml_file)
    json_valid = validate_json_swagger(json_file)
    
    # Compare files
    if yaml_valid and json_valid:
        compare_swagger_files(yaml_file, json_file)
    
    # Summary
    print("\n" + "=" * 50)
    if yaml_valid and json_valid:
        print("🎉 All Swagger files are valid!")
        return True
    else:
        print("❌ Some Swagger files have issues")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
