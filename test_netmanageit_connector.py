#!/usr/bin/env python3
"""
Test script for the OpenCTI NetManageIT Connector
This script tests the connector functionality without requiring a full OpenCTI setup
"""

import json
import sys
import os
from unittest.mock import Mock, patch

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.opencti_netmanageit_client import OpenCTINetManageITClient
from src.utils.opencti_stix_converter import OpenCTISTIXConverter


def test_observable_conversion():
    """Test converting OpenCTI observable data to STIX"""
    print("Testing observable conversion...")
    
    # Mock helper
    helper = Mock()
    helper.connector_logger = Mock()
    
    # Sample observable data from the JSON file
    sample_observable = {
        "id": "90d6dd50-75c6-43a8-b6f5-2f4dd278e7da",
        "standard_id": "ipv4-addr--bfe7e781-c571-5232-968a-110824c59769",
        "entity_type": "IPv4-Addr",
        "observable_value": "46.185.128.24",
        "created_at": "2025-09-03T16:03:21.541Z",
        "updated_at": "2025-09-03T16:03:21.654Z",
        "x_opencti_score": 75,
        "x_opencti_description": "Internet Scanning IP detected by GreyNoise with classification `malicious`.",
        "value": "46.185.128.24",
        "objectLabel": [
            {
                "id": "8e1b4486-49ce-4d9d-b669-f7ebc4c9c59c",
                "value": "gn-classification: malicious",
                "color": "#ff8178"
            }
        ],
        "objectMarking": [
            {
                "id": "45f55942-ec5c-4e86-befc-2e108045c9f3",
                "definition": "TLP:GREEN",
                "x_opencti_color": "#2e7d32"
            }
        ],
        "externalReferences": {
            "edges": [
                {
                    "node": {
                        "id": "d840243d-7ca3-43cc-a5b1-17acaa4e52e2",
                        "source_name": "GreyNoise Feed",
                        "url": "https://viz.greynoise.io/ip/46.185.128.24",
                        "description": None
                    }
                }
            ]
        }
    }
    
    # Test conversion
    converter = OpenCTISTIXConverter(helper)
    try:
        stix_observable = converter.create_observable_from_opencti(sample_observable)
        
        if stix_observable:
            print(f"✓ Successfully converted observable: {stix_observable['value']}")
            print(f"  - ID: {stix_observable['id']}")
            print(f"  - Type: {stix_observable['type']}")
            print(f"  - Labels: {stix_observable.get('x_opencti_labels', [])}")
            return True
        else:
            print("✗ Failed to convert observable")
            return False
    except Exception as e:
        print(f"✗ Error converting observable: {e}")
        return False


def test_indicator_conversion():
    """Test converting OpenCTI indicator data to STIX"""
    print("\nTesting indicator conversion...")
    
    # Mock helper with real logging
    helper = Mock()
    helper.connector_logger = Mock()
    
    # Make the logger methods actually print
    def log_info(msg):
        print(f"INFO: {msg}")
    def log_warning(msg):
        print(f"WARNING: {msg}")
    def log_error(msg):
        print(f"ERROR: {msg}")
    
    helper.connector_logger.info = log_info
    helper.connector_logger.warning = log_warning
    helper.connector_logger.error = log_error
    
    # Sample indicator data from the JSON file
    sample_indicator = {
        "id": "4e6f0300-197e-46f6-9a20-30f4703055bb",
        "standard_id": "indicator--af0662ea-ce12-5ccd-af06-cda4127a3fcc",
        "entity_type": "Indicator",
        "name": "111.53.66.90",
        "pattern": "[ipv4-addr:value = '111.53.66.90']",
        "pattern_type": "stix",
        "created": "2025-09-03T15:21:58.230Z",
        "modified": "2025-09-03T17:04:47.492Z",
        "confidence": 100,
        "revoked": True,
        "description": None,
        "valid_from": "2025-09-03T15:21:58.230Z",
        "valid_until": "2025-09-04T15:21:58.230Z",
        "x_opencti_score": 20,
        "x_opencti_detection": False,
        "objectLabel": [
            {
                "id": "c1039b9a-9a9f-4630-80b6-1a471c23deb9",
                "value": "gn-classification: unknown",
                "color": "#a6a09f"
            }
        ],
        "objectMarking": [],
        "externalReferences": {"edges": []},
        "killChainPhases": [],
        "observables": {
            "edges": [
                {
                    "node": {
                        "id": "3a47ef67-c90a-48c2-951d-b16240a31d4e",
                        "standard_id": "ipv4-addr--1cdf8bee-c7ac-5a00-a248-9bd2740789df",
                        "entity_type": "IPv4-Addr",
                        "observable_value": "111.53.66.90",
                        "created_at": "2025-09-03T15:14:39.411Z",
                        "updated_at": "2025-09-03T17:04:45.983Z"
                    }
                }
            ]
        }
    }
    
    # Test conversion
    converter = OpenCTISTIXConverter(helper)
    try:
        stix_indicator = converter.create_indicator_from_opencti(sample_indicator)
        
        if stix_indicator:
            print(f"✓ Successfully converted indicator: {stix_indicator['name']}")
            print(f"  - ID: {stix_indicator['id']}")
            print(f"  - Pattern: {stix_indicator['pattern']}")
            print(f"  - Confidence: {stix_indicator['confidence']}")
            return True
        else:
            print("✗ Failed to convert indicator")
            return False
    except Exception as e:
        print(f"✗ Error converting indicator: {e}")
        return False


def test_relationship_creation():
    """Test creating relationships between indicators and observables"""
    print("\nTesting relationship creation...")
    
    # Mock helper
    helper = Mock()
    helper.connector_logger = Mock()
    
    converter = OpenCTISTIXConverter(helper)
    
    # Test relationship creation
    source_id = "indicator--af0662ea-ce12-5ccd-af06-cda4127a3fcc"
    target_id = "ipv4-addr--1cdf8bee-c7ac-5a00-a248-9bd2740789df"
    
    relationship = converter.create_relationship(source_id, "indicates", target_id)
    
    if relationship:
        print(f"✓ Successfully created relationship")
        print(f"  - Source: {relationship['source_ref']}")
        print(f"  - Target: {relationship['target_ref']}")
        print(f"  - Type: {relationship['relationship_type']}")
        return True
    else:
        print("✗ Failed to create relationship")
        return False


def main():
    """Run all tests"""
    print("OpenCTI NetManageIT Connector Test Suite")
    print("=" * 50)
    
    tests = [
        test_observable_conversion,
        test_indicator_conversion,
        test_relationship_creation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! The connector is ready to use.")
        return 0
    else:
        print("✗ Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
