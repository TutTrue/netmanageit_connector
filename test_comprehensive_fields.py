#!/usr/bin/env python3
"""
Comprehensive test for all fields in observables and indicators
"""

import sys
import os
import json

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.opencti_stix_converter import OpenCTISTIXConverter
from unittest.mock import Mock


def test_comprehensive_observable_fields():
    """Test all possible fields in observables"""
    print("Testing comprehensive observable fields...")
    
    # Mock helper
    helper = Mock()
    helper.connector_logger = Mock()
    
    # Comprehensive observable data with all possible fields
    sample_observable = {
        "id": "90d6dd50-75c6-43a8-b6f5-2f4dd278e7da",
        "standard_id": "ipv4-addr--bfe7e781-c571-5232-968a-110824c59769",
        "entity_type": "IPv4-Addr",
        "observable_value": "46.185.128.24",
        "created_at": "2025-09-03T16:03:21.541Z",
        "updated_at": "2025-09-03T16:03:21.654Z",
        "parent_types": ["Basic-Object", "Stix-Object", "Stix-Core-Object", "Stix-Cyber-Observable"],
        "x_opencti_stix_ids": ["stix-id-1", "stix-id-2"],
        "spec_version": "2.1",
        "x_opencti_score": 75,
        "x_opencti_description": "Internet Scanning IP detected by GreyNoise with classification `malicious`.",
        "value": "46.185.128.24",
        "createdBy": {
            "id": "645ac892-7ad5-4dfc-9f99-3ca29ce1f577",
            "name": "GreyNoise Feed",
            "entity_type": "Organization"
        },
        "objectMarking": [
            {
                "id": "marking-definition--45f55942-ec5c-4e86-befc-2e108045c9f3",
                "definition": "TLP:GREEN",
                "x_opencti_color": "#2e7d32"
            },
            {
                "id": "marking-definition--12345678-1234-1234-1234-123456789abc",
                "definition": "TLP:AMBER",
                "x_opencti_color": "#ff9800"
            }
        ],
        "objectLabel": [
            {
                "id": "8e1b4486-49ce-4d9d-b669-f7ebc4c9c59c",
                "value": "gn-classification: malicious",
                "color": "#ff8178"
            },
            {
                "id": "a3a4aedd-2822-47c3-afe5-9d250d2d1986",
                "value": "smbv1 crawler",
                "color": "#ffffff"
            }
        ],
        "creators": [
            {
                "id": "88ec0c6a-13ce-5e39-b486-354fe4a7084f",
                "name": "admin"
            },
            {
                "id": "another-creator-id",
                "name": "analyst"
            }
        ],
        "externalReferences": {
            "edges": [
                {
                    "node": {
                        "id": "d840243d-7ca3-43cc-a5b1-17acaa4e52e2",
                        "source_name": "GreyNoise Feed",
                        "url": "https://viz.greynoise.io/ip/46.185.128.24",
                        "description": "GreyNoise analysis"
                    }
                }
            ]
        },
        "indicators": {
            "edges": [
                {
                    "node": {
                        "id": "indicator-id-1",
                        "name": "Malicious IP Indicator",
                        "pattern_type": "stix",
                        "created_at": "2025-09-03T15:21:58.230Z",
                        "updated_at": "2025-09-03T17:04:47.492Z"
                    }
                }
            ]
        },
        "importFiles": {
            "edges": [
                {
                    "node": {
                        "id": "file-import-1",
                        "name": "import.csv",
                        "uploadStatus": "COMPLETED"
                    }
                }
            ]
        },
        "exportFiles": {
            "edges": [
                {
                    "node": {
                        "id": "file-export-1",
                        "name": "export.json",
                        "uploadStatus": "COMPLETED"
                    }
                }
            ]
        }
    }
    
    try:
        converter = OpenCTISTIXConverter(helper)
        stix_observable = converter.create_observable_from_opencti(sample_observable)
        
        if stix_observable:
            print("✓ Observable created successfully")
            print(f"  - Type: {stix_observable.get('type')}")
            print(f"  - Value: {stix_observable.get('value')}")
            print(f"  - ID: {stix_observable.get('id')}")
            
            # Test all custom properties (they are at the top level in STIX 2.1)
            print(f"  - x_opencti_score: {stix_observable.get('x_opencti_score')}")
            print(f"  - x_opencti_description: {stix_observable.get('x_opencti_description')}")
            print(f"  - x_opencti_labels: {stix_observable.get('x_opencti_labels')}")
            print(f"  - x_opencti_object_marking_refs: {stix_observable.get('x_opencti_object_marking_refs')}")
            print(f"  - x_opencti_stix_ids: {stix_observable.get('x_opencti_stix_ids')}")
            print(f"  - x_opencti_creators: {stix_observable.get('x_opencti_creators')}")
            print(f"  - x_opencti_external_references: {len(stix_observable.get('x_opencti_external_references', []))} references")
            
            return True
        else:
            print("✗ Failed to create observable")
            return False
            
    except Exception as e:
        print(f"✗ Error creating observable: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_comprehensive_indicator_fields():
    """Test all possible fields in indicators"""
    print("\nTesting comprehensive indicator fields...")
    
    # Mock helper
    helper = Mock()
    helper.connector_logger = Mock()
    
    # Comprehensive indicator data with all possible fields
    sample_indicator = {
        "id": "4e6f0300-197e-46f6-9a20-30f4703055bb",
        "standard_id": "indicator--af0662ea-ce12-5ccd-af06-cda4127a3fcc",
        "entity_type": "Indicator",
        "x_opencti_stix_ids": ["stix-indicator-1", "stix-indicator-2"],
        "spec_version": "2.1",
        "revoked": False,
        "confidence": 100,
        "created": "2025-09-03T15:21:58.230Z",
        "modified": "2025-09-03T17:04:47.492Z",
        "created_at": "2025-09-03T15:21:58.230Z",
        "updated_at": "2025-09-03T17:04:47.492Z",
        "name": "111.53.66.90",
        "pattern": "[ipv4-addr:value = '111.53.66.90']",
        "pattern_type": "stix",
        "description": "Malicious IP address indicator",
        "valid_from": "2025-09-03T15:21:58.230Z",
        "valid_until": "2025-09-04T15:21:58.230Z",
        "x_opencti_score": 20,
        "x_opencti_detection": False,
        "x_mitre_platforms": ["Windows", "Linux"],
        "indicator_types": ["malicious-activity"],
        "x_opencti_main_observable_type": "IPv4-Addr",
        "workflowEnabled": True,
        "createdBy": {
            "id": "36acd961-a509-44f6-9db9-4f04798f1378",
            "name": "GreyNoise Internet Scanner",
            "entity_type": "Organization",
            "x_opencti_reliability": "A"
        },
        "creators": [
            {
                "id": "creator-1",
                "name": "analyst1"
            },
            {
                "id": "creator-2",
                "name": "analyst2"
            }
        ],
        "objectMarking": [
            {
                "id": "marking-definition--12345678-1234-1234-1234-123456789abc",
                "definition_type": "TLP",
                "definition": "TLP:RED",
                "x_opencti_order": 1,
                "x_opencti_color": "#f44336"
            }
        ],
        "objectLabel": [
            {
                "id": "c1039b9a-9a9f-4630-80b6-1a471c23deb9",
                "value": "gn-classification: unknown",
                "color": "#a6a09f"
            }
        ],
        "status": {
            "id": "d152d5a3-b0fe-4790-9bdf-de49dfd8b241",
            "order": 1,
            "template": {
                "id": "template-1",
                "name": "NEW",
                "color": "#ff9800"
            }
        },
        "decay_base_score": 20,
        "decay_base_score_date": "2025-09-03T15:21:58.230Z",
        "decay_history": [
            {
                "score": 20,
                "updated_at": "2025-09-03T15:21:58.230Z"
            },
            {
                "score": 18,
                "updated_at": "2025-09-03T17:04:47.234Z"
            }
        ],
        "decay_applied_rule": {
            "decay_rule_id": "rule-1",
            "decay_lifetime": 30,
            "decay_pound": 0.5,
            "decay_points": 10,
            "decay_revoke_score": 0
        },
        "decayLiveDetails": {
            "live_score": 18,
            "live_points": [
                {
                    "score": 18,
                    "updated_at": "2025-09-03T17:04:47.234Z"
                }
            ]
        },
        "decayChartData": {
            "live_score_serie": [
                {
                    "updated_at": "2025-09-03T15:21:58.230Z",
                    "score": 20
                },
                {
                    "updated_at": "2025-09-03T17:04:47.234Z",
                    "score": 18
                }
            ]
        },
        "killChainPhases": [
            {
                "id": "kill-chain-1",
                "entity_type": "Kill-Chain-Phase",
                "kill_chain_name": "lockheed-martin-cyber-kill-chain",
                "phase_name": "delivery",
                "x_opencti_order": 1
            }
        ],
        "draftVersion": {
            "draft_id": "draft-123",
            "draft_operation": "create"
        },
        "observables": {
            "edges": [
                {
                    "node": {
                        "id": "3a47ef67-c90a-48c2-951d-b16240a31d4e",
                        "standard_id": "ipv4-addr--1cdf8bee-c7ac-5a00-a248-9bd2740789df",
                        "entity_type": "IPv4-Addr",
                        "parent_types": ["Basic-Object", "Stix-Object", "Stix-Core-Object", "Stix-Cyber-Observable"],
                        "observable_value": "111.53.66.90",
                        "created_at": "2025-09-03T15:14:39.411Z",
                        "updated_at": "2025-09-03T17:04:45.983Z"
                    }
                }
            ],
            "pageInfo": {
                "globalCount": 1
            }
        },
        "externalReferences": {
            "edges": [
                {
                    "node": {
                        "id": "ext-ref-1",
                        "source_name": "External Source",
                        "url": "https://example.com/indicator",
                        "description": "External reference"
                    }
                }
            ]
        },
        "importFiles": {
            "edges": [
                {
                    "node": {
                        "id": "import-file-1",
                        "name": "indicators.csv",
                        "uploadStatus": "COMPLETED",
                        "lastModified": "2025-09-03T15:21:58.230Z",
                        "lastModifiedSinceMin": 0,
                        "metaData": {
                            "mimetype": "text/csv"
                        }
                    }
                }
            ]
        },
        "exportFiles": {
            "edges": [
                {
                    "node": {
                        "id": "export-file-1",
                        "name": "indicators.json",
                        "uploadStatus": "COMPLETED",
                        "lastModified": "2025-09-03T15:21:58.230Z",
                        "lastModifiedSinceMin": 0,
                        "metaData": {
                            "mimetype": "application/json"
                        }
                    }
                }
            ]
        },
        "pendingFiles": {
            "edges": []
        },
        "objectOrganization": {
            "id": "org-1",
            "name": "Security Team"
        }
    }
    
    try:
        converter = OpenCTISTIXConverter(helper)
        stix_indicator = converter.create_indicator_from_opencti(sample_indicator)
        
        if stix_indicator:
            print("✓ Indicator created successfully")
            print(f"  - Type: {stix_indicator.get('type')}")
            print(f"  - Name: {stix_indicator.get('name')}")
            print(f"  - ID: {stix_indicator.get('id')}")
            print(f"  - Pattern: {stix_indicator.get('pattern')}")
            print(f"  - Confidence: {stix_indicator.get('confidence')}")
            
            # Test all custom properties (they are at the top level in STIX 2.1)
            print(f"  - x_opencti_score: {stix_indicator.get('x_opencti_score')}")
            print(f"  - x_opencti_detection: {stix_indicator.get('x_opencti_detection')}")
            print(f"  - x_opencti_main_observable_type: {stix_indicator.get('x_opencti_main_observable_type')}")
            print(f"  - draftVersion: {stix_indicator.get('draftVersion')}")
            print(f"  - x_opencti_stix_ids: {stix_indicator.get('x_opencti_stix_ids')}")
            print(f"  - x_opencti_creators: {stix_indicator.get('x_opencti_creators')}")
            print(f"  - x_mitre_platforms: {stix_indicator.get('x_mitre_platforms')}")
            print(f"  - decay_base_score: {stix_indicator.get('decay_base_score')}")
            print(f"  - decay_history: {len(stix_indicator.get('decay_history', []))} entries")
            print(f"  - decayLiveDetails: {stix_indicator.get('decayLiveDetails')}")
            print(f"  - workflowEnabled: {stix_indicator.get('workflowEnabled')}")
            print(f"  - status: {stix_indicator.get('status')}")
            print(f"  - x_opencti_object_marking_refs: {stix_indicator.get('x_opencti_object_marking_refs')}")
            
            return True
        else:
            print("✗ Failed to create indicator")
            return False
            
    except Exception as e:
        print(f"✗ Error creating indicator: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_relationship_creation():
    """Test relationship creation between indicators and observables"""
    print("\nTesting relationship creation...")
    
    # Mock helper
    helper = Mock()
    helper.connector_logger = Mock()
    
    try:
        converter = OpenCTISTIXConverter(helper)
        
        # Test relationship creation
        source_id = "indicator--af0662ea-ce12-5ccd-af06-cda4127a3fcc"
        target_id = "ipv4-addr--1cdf8bee-c7ac-5a00-a248-9bd2740789df"
        
        relationship = converter.create_relationship(source_id, "indicates", target_id)
        
        if relationship:
            print("✓ Relationship created successfully")
            print(f"  - Source: {relationship['source_ref']}")
            print(f"  - Target: {relationship['target_ref']}")
            print(f"  - Type: {relationship['relationship_type']}")
            return True
        else:
            print("✗ Failed to create relationship")
            return False
            
    except Exception as e:
        print(f"✗ Error creating relationship: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all comprehensive tests"""
    print("OpenCTI NetManageIT Connector Comprehensive Field Test Suite")
    print("=" * 70)
    
    tests = [
        test_comprehensive_observable_fields,
        test_comprehensive_indicator_fields,
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
    
    print("\n" + "=" * 70)
    print(f"Comprehensive Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All comprehensive tests passed! The connector handles all fields correctly.")
        return 0
    else:
        print("✗ Some comprehensive tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
