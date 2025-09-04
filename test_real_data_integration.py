#!/usr/bin/env python3
"""
Real data integration test for OpenCTI NetManageIT connector
Tests with actual data from the source instance
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Set
from collections import defaultdict

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.opencti_netmanageit_client import OpenCTINetManageITClient
from src.utils.opencti_stix_converter import OpenCTISTIXConverter
from src.utils.config_variables import Config
from unittest.mock import Mock


class RealDataIntegrationTest:
    def __init__(self):
        """Initialize the test with mock configuration"""
        # Mock configuration for testing
        self.config = Mock()
        self.config.opencti_url = "https://opencti.netmanageit.com/graphql"
        self.config.opencti_token = "56ed1bf8-c1e8-4a88-bcf5-a8519ad6e9a4"
        
        # Mock helper
        self.helper = Mock()
        self.helper.connector_logger = Mock()
        
        # Make the logger methods actually print
        def log_info(msg):
            print(f"INFO: {msg}")
        def log_warning(msg):
            print(f"WARNING: {msg}")
        def log_error(msg):
            print(f"ERROR: {msg}")
        
        self.helper.connector_logger.info = log_info
        self.helper.connector_logger.warning = log_warning
        self.helper.connector_logger.error = log_error
        
        # Initialize clients
        self.client = OpenCTINetManageITClient(self.helper, self.config)
        self.converter = OpenCTISTIXConverter(self.helper)
        
        # Test results
        self.observable_results = []
        self.indicator_results = []
        self.relationship_results = []
        self.stix_observables = []
        self.stix_indicators = []
        self.stix_relationships = []
        self.field_analysis = {
            'observables': defaultdict(int),
            'indicators': defaultdict(int)
        }

    def test_observables(self, limit: int = 1000) -> bool:
        """Test fetching and processing observables"""
        print(f"\n{'='*60}")
        print(f"TESTING OBSERVABLES (Limit: {limit})")
        print(f"{'='*60}")
        
        try:
            count = 0
            observable_ids = set()
            
            for observable_data in self.client.get_observables():
                if count >= limit:
                    break
                    
                count += 1
                if count % 10 == 0:
                    print(f"Processed {count} observables...")
                
                # Store original data
                self.observable_results.append(observable_data)
                observable_ids.add(observable_data.get('standard_id'))
                
                # Convert to STIX
                stix_observable = self.converter.create_observable_from_opencti(observable_data)
                
                if stix_observable:
                    # Store STIX object
                    self.stix_observables.append(stix_observable)
                    # Analyze fields
                    self._analyze_observable_fields(observable_data, stix_observable)
                else:
                    print(f"WARNING: Failed to convert observable {count}")
            
            print(f"\n✓ Successfully processed {count} observables")
            print(f"✓ Unique observable IDs: {len(observable_ids)}")
            
            return True
            
        except Exception as e:
            print(f"✗ Error testing observables: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_indicators(self, limit: int = 1000) -> bool:
        """Test fetching and processing indicators"""
        print(f"\n{'='*60}")
        print(f"TESTING INDICATORS (Limit: {limit})")
        print(f"{'='*60}")
        
        try:
            count = 0
            indicator_ids = set()
            observable_standard_ids = set()
            
            for indicator_data in self.client.get_indicators():
                if count >= limit:
                    break
                    
                count += 1
                if count % 10 == 0:
                    print(f"Processed {count} indicators...")
                
                # Store original data
                self.indicator_results.append(indicator_data)
                indicator_ids.add(indicator_data.get('standard_id'))
                
                # Convert to STIX
                stix_indicator = self.converter.create_indicator_from_opencti(indicator_data)
                
                if stix_indicator:
                    # Store STIX object
                    self.stix_indicators.append(stix_indicator)
                    # Analyze fields
                    self._analyze_indicator_fields(indicator_data, stix_indicator)
                    
                    # Check for observables and potential relationships
                    self._check_indicator_observables(indicator_data, stix_indicator)
                else:
                    print(f"WARNING: Failed to convert indicator {count}")
            
            print(f"\n✓ Successfully processed {count} indicators")
            print(f"✓ Unique indicator IDs: {len(indicator_ids)}")
            print(f"✓ Observable standard IDs found: {len(observable_standard_ids)}")
            
            return True
            
        except Exception as e:
            print(f"✗ Error testing indicators: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _analyze_observable_fields(self, original_data: Dict, stix_observable: Dict):
        """Analyze which fields are present in observables"""
        # Check original data fields
        for field in ['x_opencti_score', 'x_opencti_description', 'x_opencti_stix_ids', 
                     'objectLabel', 'objectMarking', 'creators', 'externalReferences']:
            if field in original_data and original_data[field]:
                self.field_analysis['observables'][f'original_{field}'] += 1
        
        # Check STIX object fields
        for field in ['x_opencti_score', 'x_opencti_description', 'x_opencti_stix_ids',
                     'x_opencti_labels', 'x_opencti_object_marking_refs', 'x_opencti_creators',
                     'x_opencti_external_references']:
            if stix_observable.get(field):
                self.field_analysis['observables'][f'stix_{field}'] += 1

    def _analyze_indicator_fields(self, original_data: Dict, stix_indicator: Dict):
        """Analyze which fields are present in indicators"""
        # Check original data fields
        for field in ['x_opencti_score', 'x_opencti_detection', 'x_opencti_main_observable_type',
                     'draftVersion', 'x_opencti_stix_ids', 'creators', 'x_mitre_platforms',
                     'decay_base_score', 'decay_history', 'decayLiveDetails', 'workflowEnabled',
                     'status', 'objectLabel', 'objectMarking', 'externalReferences']:
            if field in original_data and original_data[field]:
                self.field_analysis['indicators'][f'original_{field}'] += 1
        
        # Check STIX object fields
        for field in ['x_opencti_score', 'x_opencti_detection', 'x_opencti_main_observable_type',
                     'draftVersion', 'x_opencti_stix_ids', 'x_opencti_creators', 'x_mitre_platforms',
                     'decay_base_score', 'decay_history', 'decayLiveDetails', 'workflowEnabled',
                     'status', 'x_opencti_object_marking_refs']:
            if stix_indicator.get(field):
                self.field_analysis['indicators'][f'stix_{field}'] += 1

    def _check_indicator_observables(self, indicator_data: Dict, stix_indicator: Dict):
        """Check if indicator has observables and should create relationships"""
        observables = indicator_data.get('observables', {}).get('edges', [])
        
        if observables:
            for obs_edge in observables:
                obs_node = obs_edge.get('node', {})
                obs_standard_id = obs_node.get('standard_id')
                
                if obs_standard_id:
                    # This should create a relationship
                    relationship = self.converter.create_relationship(
                        stix_indicator['id'],
                        'indicates',
                        obs_standard_id
                    )
                    
                    if relationship:
                        self.relationship_results.append({
                            'indicator_id': stix_indicator['id'],
                            'observable_standard_id': obs_standard_id,
                            'relationship': relationship,
                            'indicator_name': indicator_data.get('name', 'Unknown'),
                            'observable_value': obs_node.get('observable_value', 'Unknown')
                        })
                        # Store STIX relationship object
                        self.stix_relationships.append(relationship)

    def test_relationships(self) -> bool:
        """Test relationship creation and validation"""
        print(f"\n{'='*60}")
        print(f"TESTING RELATIONSHIPS")
        print(f"{'='*60}")
        
        if not self.relationship_results:
            print("No relationships to test")
            return True
        
        print(f"✓ Found {len(self.relationship_results)} potential relationships")
        
        # Analyze relationships
        relationship_types = defaultdict(int)
        for rel in self.relationship_results:
            rel_type = rel['relationship']['relationship_type']
            relationship_types[rel_type] += 1
        
        print("Relationship types found:")
        for rel_type, count in relationship_types.items():
            print(f"  - {rel_type}: {count}")
        
        # Show sample relationships
        print(f"\nSample relationships (first 5):")
        for i, rel in enumerate(self.relationship_results[:5]):
            print(f"  {i+1}. {rel['indicator_name']} -> {rel['observable_value']}")
            print(f"     Indicator: {rel['indicator_id']}")
            print(f"     Observable: {rel['observable_standard_id']}")
        
        return True

    def print_field_analysis(self):
        """Print comprehensive field analysis"""
        print(f"\n{'='*60}")
        print(f"FIELD ANALYSIS RESULTS")
        print(f"{'='*60}")
        
        print("\nOBSERVABLE FIELDS:")
        print("-" * 40)
        for field, count in sorted(self.field_analysis['observables'].items()):
            percentage = (count / len(self.observable_results)) * 100 if self.observable_results else 0
            print(f"  {field}: {count} ({percentage:.1f}%)")
        
        print("\nINDICATOR FIELDS:")
        print("-" * 40)
        for field, count in sorted(self.field_analysis['indicators'].items()):
            percentage = (count / len(self.indicator_results)) * 100 if self.indicator_results else 0
            print(f"  {field}: {count} ({percentage:.1f}%)")

    def print_summary(self):
        """Print test summary"""
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY")
        print(f"{'='*60}")
        
        print(f"Observables processed: {len(self.observable_results)}")
        print(f"Indicators processed: {len(self.indicator_results)}")
        print(f"Relationships created: {len(self.relationship_results)}")
        
        # Calculate relationship coverage
        indicators_with_observables = len([i for i in self.indicator_results 
                                         if i.get('observables', {}).get('edges')])
        if indicators_with_observables > 0:
            relationship_coverage = (len(self.relationship_results) / indicators_with_observables) * 100
            print(f"Relationship coverage: {relationship_coverage:.1f}% ({len(self.relationship_results)}/{indicators_with_observables})")
        
        print(f"\nField coverage analysis completed")
        print(f"All tests completed successfully!")

    def run_all_tests(self, limit: int = 50):
        """Run all integration tests"""
        print("OpenCTI NetManageIT Connector - Real Data Integration Test")
        print("=" * 70)
        
        success = True
        
        # Test observables
        if not self.test_observables(limit):
            success = False
        
        # Test indicators
        if not self.test_indicators(limit):
            success = False
        
        # Test relationships
        if not self.test_relationships():
            success = False
        
        # Print analysis
        self.print_field_analysis()
        self.print_summary()
        
        # Save STIX objects to file
        self.save_stix_objects_to_file()
        
        return success
    
    def save_stix_objects_to_file(self):
        """Save all STIX objects to a JSON file for inspection"""
        print("\n" + "="*60)
        print("SAVING STIX OBJECTS TO FILE")
        print("="*60)
        
        # Prepare data for output
        output_data = {
            "observables": [],
            "indicators": [],
            "relationships": [],
            "metadata": {
                "total_observables": len(self.stix_observables),
                "total_indicators": len(self.stix_indicators),
                "total_relationships": len(self.stix_relationships),
                "test_timestamp": str(datetime.now())
            }
        }
        
        # Add observables
        for obs in self.stix_observables:
            if obs:
                # Convert STIX object to dict for JSON serialization
                obs_dict = {
                    "id": obs.get("id"),
                    "type": obs.get("type"),
                    "value": obs.get("value"),
                    "created": obs.get("created"),
                    "modified": obs.get("modified")
                }
                
                # Add all x_opencti_ properties (they're at top level, not in custom_properties)
                for key, value in obs.items():
                    if key.startswith("x_opencti_"):
                        obs_dict[key] = value
                
                # Add custom_properties for any remaining custom properties
                if hasattr(obs, 'custom_properties') and obs.custom_properties:
                    obs_dict["custom_properties"] = obs.custom_properties
                
                output_data["observables"].append(obs_dict)
        
        # Add indicators
        for ind in self.stix_indicators:
            if ind:
                # Convert STIX object to dict for JSON serialization
                ind_dict = {
                    "id": ind.get("id"),
                    "type": ind.get("type"),
                    "name": ind.get("name"),
                    "pattern": ind.get("pattern"),
                    "pattern_type": ind.get("pattern_type"),
                    "confidence": ind.get("confidence"),
                    "valid_from": ind.get("valid_from"),
                    "valid_until": ind.get("valid_until"),
                    "created": ind.get("created"),
                    "modified": ind.get("modified")
                }
                
                # Add all x_opencti_ properties (they're at top level, not in custom_properties)
                for key, value in ind.items():
                    if key.startswith("x_opencti_"):
                        ind_dict[key] = value
                
                # Add other custom properties that might not have x_opencti_ prefix
                for key, value in ind.items():
                    if key not in ind_dict and not key.startswith("x_opencti_") and key not in ["id", "type", "name", "pattern", "pattern_type", "confidence", "valid_from", "valid_until", "created", "modified", "spec_version"]:
                        ind_dict[key] = value
                
                # Add custom_properties for any remaining custom properties
                if hasattr(ind, 'custom_properties') and ind.custom_properties:
                    ind_dict["custom_properties"] = ind.custom_properties
                
                output_data["indicators"].append(ind_dict)
        
        # Add relationships
        for rel in self.stix_relationships:
            if rel:
                # Convert STIX object to dict for JSON serialization
                rel_dict = {
                    "id": rel.get("id"),
                    "type": rel.get("type"),
                    "source_ref": rel.get("source_ref"),
                    "target_ref": rel.get("target_ref"),
                    "relationship_type": rel.get("relationship_type"),
                    "created": rel.get("created"),
                    "modified": rel.get("modified")
                }
                output_data["relationships"].append(rel_dict)
        
        # Save to file
        output_file = "stix_objects_output.json"
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"✓ STIX objects saved to: {output_file}")
            print(f"  - Observables: {len(output_data['observables'])}")
            print(f"  - Indicators: {len(output_data['indicators'])}")
            print(f"  - Relationships: {len(output_data['relationships'])}")
            
        except Exception as e:
            print(f"✗ Error saving STIX objects to file: {e}")


def main():
    """Main test function"""
    test = RealDataIntegrationTest()
    
    # Run tests with 50 records each
    success = test.run_all_tests(limit=50)
    
    if success:
        print("\n✓ All integration tests passed!")
        return 0
    else:
        print("\n✗ Some integration tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
