import stix2
from stix2 import TLP_RED, TLP_AMBER, TLP_GREEN, TLP_WHITE
from stix2.v21 import CustomObservable as V21CustomObservable
from stix2.v21.observables import StringProperty
from pycti import Identity, StixCoreRelationship, OpenCTIConnectorHelper
from typing import Dict, List, Optional


# Define custom hostname observable using v21
@V21CustomObservable('x-netmanageit-hostname', [
    ('value', StringProperty(required=True)),
], [
    'value'
])
class Hostname:
    """Custom STIX 2.1 observable for hostnames."""
    pass


# Define custom software observable using v21
@V21CustomObservable('x-netmanageit-software', [
    ('name', StringProperty(required=True)),
    ('version', StringProperty(required=False)),
    ('vendor', StringProperty(required=False)),
], [
    'name'
])
class Software:
    """Custom STIX 2.1 observable for software."""
    pass


# Define custom cryptocurrency wallet observable using v21
@V21CustomObservable('x-netmanageit-cryptocurrency-wallet', [
    ('value', StringProperty(required=True)),
    ('type', StringProperty(required=False)),
    ('currency', StringProperty(required=False)),
], [
    'value'
])
class CustomCryptocurrencyWallet:
    """Custom STIX 2.1 observable for cryptocurrency wallets."""
    pass


class OpenCTISTIXConverter:
    """
    Provides methods for converting OpenCTI NetManageIT data into STIX 2.1 objects.
    """

    def __init__(self, helper: OpenCTIConnectorHelper):
        self.helper = helper
        self.author = self.create_author()

    @staticmethod
    def create_author() -> dict:
        """
        Create Author
        :return: Author in Stix2 object
        """
        author = stix2.Identity(
            id=Identity.generate_id(name="OpenCTI NetManageIT", identity_class="organization"),
            name="OpenCTI NetManageIT",
            identity_class="organization",
            description="Data imported from OpenCTI NetManageIT instance.",
        )
        return author

    def create_observable_from_opencti(self, observable_data: Dict) -> Optional[Dict]:
        """
        Create STIX observable from OpenCTI observable data
        :param observable_data: OpenCTI observable data
        :return: STIX observable object
        """
        try:
            entity_type = observable_data.get("entity_type", "")
            observable_value = observable_data.get("observable_value", "")
            standard_id = observable_data.get("standard_id", "")
            
            if not observable_value or not standard_id:
                return None
            
            # Ensure the standard_id follows the correct STIX format for the entity type
            stix_id = self._ensure_valid_stix_id(standard_id, entity_type)

            # Create external references from OpenCTI data
            external_refs = self._create_external_references(observable_data)
            
            # Create labels from OpenCTI data
            labels = self._create_labels(observable_data)
            
            # Create marking definitions from OpenCTI data
            marking_defs = self._create_marking_definitions(observable_data)
            
            # Create the appropriate STIX observable based on entity type
            if entity_type == "IPv4-Addr":
                return stix2.IPv4Address(
                    id=stix_id,
                    value=observable_value,
                    object_marking_refs=marking_defs,
                    custom_properties={
                        "x_opencti_score": observable_data.get("x_opencti_score"),
                        "x_opencti_description": observable_data.get("x_opencti_description"),
                        "x_opencti_created_by_ref": self.author["id"],
                        "x_opencti_external_references": external_refs if external_refs else [],
                        "x_opencti_labels": labels if labels else [],
                        "x_opencti_stix_ids": observable_data.get("x_opencti_stix_ids", []),
                        "x_opencti_creators": self._create_creators(observable_data),
                    }
                )
            elif entity_type == "IPv6-Addr":
                return stix2.IPv6Address(
                    id=stix_id,
                    value=observable_value,
                    object_marking_refs=marking_defs,
                    custom_properties={
                        "x_opencti_score": observable_data.get("x_opencti_score"),
                        "x_opencti_description": observable_data.get("x_opencti_description"),
                        "x_opencti_created_by_ref": self.author["id"],
                        "x_opencti_external_references": external_refs if external_refs else [],
                        "x_opencti_labels": labels if labels else [],
                        "x_opencti_stix_ids": observable_data.get("x_opencti_stix_ids", []),
                        "x_opencti_creators": self._create_creators(observable_data),
                    }
                )
            elif entity_type == "Domain-Name":
                return stix2.DomainName(
                    id=stix_id,
                    value=observable_value,
                    object_marking_refs=marking_defs,
                    custom_properties={
                        "x_opencti_score": observable_data.get("x_opencti_score"),
                        "x_opencti_description": observable_data.get("x_opencti_description"),
                        "x_opencti_created_by_ref": self.author["id"],
                        "x_opencti_external_references": external_refs if external_refs else [],
                        "x_opencti_labels": labels if labels else [],
                        "x_opencti_stix_ids": observable_data.get("x_opencti_stix_ids", []),
                        "x_opencti_creators": self._create_creators(observable_data),
                    }
                )
            elif entity_type == "Url":
                return stix2.URL(
                    id=stix_id,
                    value=observable_value,
                    object_marking_refs=marking_defs,
                    custom_properties={
                        "x_opencti_score": observable_data.get("x_opencti_score"),
                        "x_opencti_description": observable_data.get("x_opencti_description"),
                        "x_opencti_created_by_ref": self.author["id"],
                        "x_opencti_external_references": external_refs if external_refs else [],
                        "x_opencti_labels": labels if labels else [],
                        "x_opencti_stix_ids": observable_data.get("x_opencti_stix_ids", []),
                        "x_opencti_creators": self._create_creators(observable_data),
                    }
                )
            elif entity_type == "Email-Addr":
                return stix2.EmailAddress(
                    id=stix_id,
                    value=observable_value,
                    object_marking_refs=marking_defs,
                    custom_properties={
                        "x_opencti_score": observable_data.get("x_opencti_score"),
                        "x_opencti_description": observable_data.get("x_opencti_description"),
                        "x_opencti_created_by_ref": self.author["id"],
                        "x_opencti_external_references": external_refs if external_refs else [],
                        "x_opencti_labels": labels if labels else [],
                        "x_opencti_stix_ids": observable_data.get("x_opencti_stix_ids", []),
                        "x_opencti_creators": self._create_creators(observable_data),
                    }
                )
            elif entity_type == "Mac-Addr":
                return stix2.MACAddress(
                    id=stix_id,
                    value=observable_value,
                    object_marking_refs=marking_defs,
                    custom_properties={
                        "x_opencti_score": observable_data.get("x_opencti_score"),
                        "x_opencti_description": observable_data.get("x_opencti_description"),
                        "x_opencti_created_by_ref": self.author["id"],
                        "x_opencti_external_references": external_refs if external_refs else [],
                        "x_opencti_labels": labels if labels else [],
                        "x_opencti_stix_ids": observable_data.get("x_opencti_stix_ids", []),
                        "x_opencti_creators": self._create_creators(observable_data),
                    }
                )
            elif entity_type == "Autonomous-System":
                return stix2.AutonomousSystem(
                    id=stix_id,
                    number=observable_data.get("number", 0),
                    name=observable_value,
                    object_marking_refs=marking_defs,
                    custom_properties={
                        "x_opencti_score": observable_data.get("x_opencti_score"),
                        "x_opencti_description": observable_data.get("x_opencti_description"),
                        "x_opencti_created_by_ref": self.author["id"],
                        "x_opencti_external_references": external_refs if external_refs else [],
                        "x_opencti_labels": labels if labels else [],
                        "x_opencti_stix_ids": observable_data.get("x_opencti_stix_ids", []),
                        "x_opencti_creators": self._create_creators(observable_data),
                    }
                )
            elif entity_type == "Process":
                return stix2.Process(
                    id=stix_id,
                    pid=observable_data.get("pid"),
                    command_line=observable_data.get("command_line"),
                    object_marking_refs=marking_defs,
                    custom_properties={
                        "x_opencti_score": observable_data.get("x_opencti_score"),
                        "x_opencti_description": observable_data.get("x_opencti_description"),
                        "x_opencti_created_by_ref": self.author["id"],
                        "x_opencti_external_references": external_refs if external_refs else [],
                        "x_opencti_labels": labels if labels else [],
                        "x_opencti_stix_ids": observable_data.get("x_opencti_stix_ids", []),
                        "x_opencti_creators": self._create_creators(observable_data),
                    }
                )
            elif entity_type == "User-Account":
                return stix2.UserAccount(
                    id=stix_id,
                    user_id=observable_data.get("account_login", observable_value),
                    account_login=observable_data.get("account_login"),
                    display_name=observable_data.get("display_name"),
                    object_marking_refs=marking_defs,
                    custom_properties={
                        "x_opencti_score": observable_data.get("x_opencti_score"),
                        "x_opencti_description": observable_data.get("x_opencti_description"),
                        "x_opencti_created_by_ref": self.author["id"],
                        "x_opencti_external_references": external_refs if external_refs else [],
                        "x_opencti_labels": labels if labels else [],
                        "x_opencti_stix_ids": observable_data.get("x_opencti_stix_ids", []),
                        "x_opencti_creators": self._create_creators(observable_data),
                    }
                )
            elif entity_type == "StixFile":
                return stix2.File(
                    id=stix_id,
                    name=observable_value,
                    object_marking_refs=marking_defs,
                    custom_properties={
                        "x_opencti_score": observable_data.get("x_opencti_score"),
                        "x_opencti_description": observable_data.get("x_opencti_description"),
                        "x_opencti_created_by_ref": self.author["id"],
                        "x_opencti_external_references": external_refs if external_refs else [],
                        "x_opencti_labels": labels if labels else [],
                        "x_opencti_stix_ids": observable_data.get("x_opencti_stix_ids", []),
                        "x_opencti_creators": self._create_creators(observable_data),
                    }
                )
            elif entity_type == "Hostname":
                return Hostname(
                    id=stix_id,
                    value=observable_value,
                    object_marking_refs=marking_defs,
                    custom_properties={
                        "x_opencti_score": observable_data.get("x_opencti_score"),
                        "x_opencti_description": observable_data.get("x_opencti_description"),
                        "x_opencti_created_by_ref": self.author["id"],
                        "x_opencti_external_references": external_refs if external_refs else [],
                        "x_opencti_labels": labels if labels else [],
                        "x_opencti_stix_ids": observable_data.get("x_opencti_stix_ids", []),
                        "x_opencti_creators": self._create_creators(observable_data),
                    }
                )
            elif entity_type == "Software":
                return Software(
                    id=stix_id,
                    name=observable_value,
                    version=observable_data.get("version"),
                    vendor=observable_data.get("vendor"),
                    object_marking_refs=marking_defs,
                    custom_properties={
                        "x_opencti_score": observable_data.get("x_opencti_score"),
                        "x_opencti_description": observable_data.get("x_opencti_description"),
                        "x_opencti_created_by_ref": self.author["id"],
                        "x_opencti_external_references": external_refs if external_refs else [],
                        "x_opencti_labels": labels if labels else [],
                        "x_opencti_stix_ids": observable_data.get("x_opencti_stix_ids", []),
                        "x_opencti_creators": self._create_creators(observable_data),
                    }
                )
            elif entity_type == "Cryptocurrency-Wallet":
                return CustomCryptocurrencyWallet(
                    id=stix_id,
                    value=observable_value,
                    type=observable_data.get("type"),
                    currency=observable_data.get("currency"),
                    object_marking_refs=marking_defs,
                    custom_properties={
                        "x_opencti_score": observable_data.get("x_opencti_score"),
                        "x_opencti_description": observable_data.get("x_opencti_description"),
                        "x_opencti_created_by_ref": self.author["id"],
                        "x_opencti_external_references": external_refs if external_refs else [],
                        "x_opencti_labels": labels if labels else [],
                        "x_opencti_stix_ids": observable_data.get("x_opencti_stix_ids", []),
                        "x_opencti_creators": self._create_creators(observable_data),
                    }
                )
            else:
                # For unknown types, create a generic artifact
                import base64
                payload_bin = base64.b64encode(observable_value.encode() if observable_value else b"").decode('utf-8')
                return stix2.Artifact(
                    id=stix_id,
                    payload_bin=payload_bin,
                    object_marking_refs=marking_defs,
                    custom_properties={
                        "x_opencti_score": observable_data.get("x_opencti_score"),
                        "x_opencti_description": observable_data.get("x_opencti_description"),
                        "x_opencti_created_by_ref": self.author["id"],
                        "x_opencti_external_references": external_refs if external_refs else [],
                        "x_opencti_labels": labels if labels else [],
                        "x_opencti_stix_ids": observable_data.get("x_opencti_stix_ids", []),
                        "x_opencti_creators": self._create_creators(observable_data),
                    }
                )
                
        except Exception as e:
            self.helper.connector_logger.error(f"Error creating observable: {e}")
            return None

    def create_indicator_from_opencti(self, indicator_data: Dict) -> Optional[Dict]:
        """
        Create STIX indicator from OpenCTI indicator data
        :param indicator_data: OpenCTI indicator data
        :return: STIX indicator object
        """
        try:
            standard_id = indicator_data.get("standard_id", "")
            name = indicator_data.get("name", "")
            pattern = indicator_data.get("pattern", "")
            pattern_type = indicator_data.get("pattern_type", "stix")
            description = indicator_data.get("description", "")
            confidence = indicator_data.get("confidence", 50)
            valid_from = indicator_data.get("valid_from")
            valid_until = indicator_data.get("valid_until")
            
            if not standard_id:
                return None
            
            # Ensure the standard_id follows the correct STIX format for indicators
            stix_id = self._ensure_valid_stix_id(standard_id, "Indicator")
            
            # Ensure valid_until is greater than valid_from
            if valid_from and valid_until and valid_until <= valid_from:
                # Set valid_until to 1 day after valid_from
                from datetime import datetime, timedelta
                try:
                    from_dt = datetime.fromisoformat(valid_from.replace('Z', '+00:00'))
                    until_dt = from_dt + timedelta(days=1)
                    valid_until = until_dt.isoformat().replace('+00:00', 'Z')
                except Exception as e:
                    self.helper.connector_logger.warning(f"Could not adjust valid_until: {e}")
                    valid_until = None
            
            if not pattern:
                return None

            # Create external references from OpenCTI data
            external_refs = self._create_external_references(indicator_data)
            
            # Create labels from OpenCTI data
            labels = self._create_labels(indicator_data)
            
            # Create marking definitions from OpenCTI data
            marking_defs = self._create_marking_definitions(indicator_data)
            
            # Create kill chain phases if available
            kill_chain_phases = self._create_kill_chain_phases(indicator_data)
            
            indicator = stix2.Indicator(
                id=stix_id,
                name=name,
                pattern=pattern,
                pattern_type=pattern_type,
                description=description,
                confidence=confidence,
                valid_from=valid_from,
                valid_until=valid_until,
                created_by_ref=self.author["id"],
                external_references=external_refs if external_refs else [],
                labels=labels if labels else [],
                kill_chain_phases=kill_chain_phases if kill_chain_phases else [],
                object_marking_refs=marking_defs,
                custom_properties={
                    "x_opencti_score": indicator_data.get("x_opencti_score"),
                    "x_opencti_detection": indicator_data.get("x_opencti_detection"),
                    "x_opencti_created_by_ref": self.author["id"],
                    "x_opencti_main_observable_type": indicator_data.get("x_opencti_main_observable_type"),
                    "draftVersion": indicator_data.get("draftVersion"),
                    "x_opencti_stix_ids": indicator_data.get("x_opencti_stix_ids", []),
                    "x_opencti_creators": self._create_creators(indicator_data),
                    "x_mitre_platforms": indicator_data.get("x_mitre_platforms"),
                    "decay_base_score": indicator_data.get("decay_base_score"),
                    "decay_base_score_date": indicator_data.get("decay_base_score_date"),
                    "decay_history": indicator_data.get("decay_history", []),
                    "decay_applied_rule": indicator_data.get("decay_applied_rule"),
                    "decayLiveDetails": indicator_data.get("decayLiveDetails"),
                    "decayChartData": indicator_data.get("decayChartData"),
                    "workflowEnabled": indicator_data.get("workflowEnabled"),
                    "status": indicator_data.get("status"),
                }
            )
            return indicator
            
        except Exception as e:
            self.helper.connector_logger.error(f"Error creating indicator: {e}")
            return None

    def create_relationship(self, source_id: str, relationship_type: str, target_id: str) -> Dict:
        """
        Creates Relationship object
        :param source_id: ID of source in string
        :param relationship_type: Relationship type in string
        :param target_id: ID of target in string
        :return: Relationship STIX2 object
        """
        relationship = stix2.Relationship(
            id=StixCoreRelationship.generate_id(
                relationship_type, source_id, target_id
            ),
            relationship_type=relationship_type,
            source_ref=source_id,
            target_ref=target_id,
            created_by_ref=self.author["id"],
        )
        return relationship

    def _create_external_references(self, data: Dict) -> List[Dict]:
        """
        Create external references from OpenCTI data
        :param data: OpenCTI data
        :return: List of external references
        """
        external_refs = []
        
        # Add external references from the data
        if "externalReferences" in data and "edges" in data["externalReferences"]:
            for edge in data["externalReferences"]["edges"]:
                node = edge.get("node", {})
                if node.get("url"):
                    external_refs.append(
                        stix2.ExternalReference(
                            source_name=node.get("source_name", "External Source"),
                            url=node.get("url"),
                            description=node.get("description")
                        )
                    )
        
        return external_refs

    def _create_labels(self, data: Dict) -> List[str]:
        """
        Create labels from OpenCTI data
        :param data: OpenCTI data
        :return: List of labels
        """
        labels = []
        
        # Add labels from objectLabel
        if "objectLabel" in data:
            for label in data["objectLabel"]:
                if isinstance(label, dict) and "value" in label:
                    labels.append(label["value"])
                elif isinstance(label, str):
                    labels.append(label)
        
        return labels

    def _create_marking_definitions(self, data: Dict) -> List:
        """
        Create marking definitions from OpenCTI data using built-in TLP definitions
        :param data: OpenCTI data
        :return: List of built-in marking definition objects
        """
        marking_defs = []
        
        # Add marking definitions from objectMarking
        if "objectMarking" in data:
            for marking in data["objectMarking"]:
                if isinstance(marking, dict):
                    # Map OpenCTI marking definitions to built-in TLP definitions
                    definition_type = marking.get("definition_type", "").lower()
                    definition = marking.get("definition", "").lower()
                    
                    # Map to built-in TLP definitions based on definition type and content
                    if definition_type == "tlp":
                        if "red" in definition or "tlp:red" in definition:
                            marking_defs.append(TLP_RED.id)
                        elif "amber" in definition or "tlp:amber" in definition:
                            marking_defs.append(TLP_AMBER.id)
                        elif "green" in definition or "tlp:green" in definition:
                            marking_defs.append(TLP_GREEN.id)
                        elif "white" in definition or "tlp:white" in definition:
                            marking_defs.append(TLP_WHITE.id)
                        elif "clear" in definition or "tlp:clear" in definition:
                            # Map TLP:CLEAR to TLP:WHITE (most permissive level)
                            marking_defs.append(TLP_WHITE.id)
                        else:
                            # Default to TLP_AMBER if TLP type is not recognized
                            self.helper.connector_logger.warning(f"Unknown TLP definition: {definition}, defaulting to TLP_AMBER")
                            marking_defs.append(TLP_AMBER.id)
                    else:
                        # For non-TLP markings, try to map based on definition content
                        if "red" in definition or "tlp:red" in definition:
                            marking_defs.append(TLP_RED.id)
                        elif "amber" in definition or "tlp:amber" in definition:
                            marking_defs.append(TLP_AMBER.id)
                        elif "green" in definition or "tlp:green" in definition:
                            marking_defs.append(TLP_GREEN.id)
                        elif "white" in definition or "tlp:white" in definition:
                            marking_defs.append(TLP_WHITE.id)
                        elif "clear" in definition or "tlp:clear" in definition:
                            # Map TLP:CLEAR to TLP:WHITE (most permissive level)
                            marking_defs.append(TLP_WHITE.id)
                        else:
                            # Default to TLP_AMBER for unrecognized markings
                            self.helper.connector_logger.warning(f"Unknown marking definition: {definition}, defaulting to TLP_AMBER")
                            marking_defs.append(TLP_AMBER.id)
                elif isinstance(marking, str):
                    # Handle string-based marking definitions
                    marking_lower = marking.lower()
                    if "red" in marking_lower or "tlp:red" in marking_lower:
                        marking_defs.append(TLP_RED.id)
                    elif "amber" in marking_lower or "tlp:amber" in marking_lower:
                        marking_defs.append(TLP_AMBER.id)
                    elif "green" in marking_lower or "tlp:green" in marking_lower:
                        marking_defs.append(TLP_GREEN.id)
                    elif "white" in marking_lower or "tlp:white" in marking_lower:
                        marking_defs.append(TLP_WHITE.id)
                    elif "clear" in marking_lower or "tlp:clear" in marking_lower:
                        # Map TLP:CLEAR to TLP:WHITE (most permissive level)
                        marking_defs.append(TLP_WHITE.id)
                    else:
                        # Default to TLP_AMBER for unrecognized markings
                        self.helper.connector_logger.warning(f"Unknown marking definition: {marking}, defaulting to TLP_AMBER")
                        marking_defs.append(TLP_AMBER.id)
        
        # If no marking definitions found, default to TLP_AMBER
        if not marking_defs:
            marking_defs.append(TLP_AMBER.id)
        
        return marking_defs

    def _is_valid_uuid(self, uuid_str: str) -> bool:
        """
        Validate UUID format
        :param uuid_str: UUID string to validate
        :return: True if valid, False otherwise
        """
        import re
        # UUID pattern: 8-4-4-4-12 hexadecimal digits
        pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(pattern, uuid_str, re.IGNORECASE))

    def _is_valid_stix_id(self, stix_id: str) -> bool:
        """
        Validate STIX identifier format
        :param stix_id: STIX identifier to validate
        :return: True if valid, False otherwise
        """
        import re
        # STIX identifier pattern: <object-type>--<UUID>
        pattern = r'^[a-z-]+--[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(pattern, stix_id, re.IGNORECASE))

    def _create_creators(self, data: Dict) -> List[Dict]:
        """
        Create creators list from OpenCTI data
        :param data: OpenCTI data
        :return: List of creators
        """
        creators = []
        
        # Add creators from creators array
        if "creators" in data:
            for creator in data["creators"]:
                if isinstance(creator, dict):
                    creators.append({
                        "id": creator.get("id"),
                        "name": creator.get("name")
                    })
        
        return creators

    def _create_kill_chain_phases(self, data: Dict) -> List[Dict]:
        """
        Create kill chain phases from OpenCTI data
        :param data: OpenCTI data
        :return: List of kill chain phases
        """
        kill_chain_phases = []
        
        # Add kill chain phases
        if "killChainPhases" in data:
            for phase in data["killChainPhases"]:
                if isinstance(phase, dict):
                    kill_chain_phases.append(
                        stix2.KillChainPhase(
                            kill_chain_name=phase.get("kill_chain_name", "lockheed-martin-cyber-kill-chain"),
                            phase_name=phase.get("phase_name", "")
                        )
                    )
        
        return kill_chain_phases
    
    def _ensure_valid_stix_id(self, standard_id: str, entity_type: str) -> str:
        """
        Ensure the standard_id follows the correct STIX format for the entity type
        :param standard_id: The standard_id from the source data
        :param entity_type: The entity type (e.g., "IPv4-Addr", "Artifact")
        :return: A valid STIX ID
        """
        # Handle special cases for custom observables first
        if entity_type == "Hostname" and standard_id.startswith("hostname--"):
            return f"x-netmanageit-hostname--{standard_id[10:]}"
        if entity_type == "Software" and standard_id.startswith("software--"):
            return f"x-netmanageit-software--{standard_id[9:]}"
        if entity_type == "Cryptocurrency-Wallet" and standard_id.startswith("cryptocurrency-wallet--"):
            return f"x-netmanageit-cryptocurrency-wallet--{standard_id[23:]}"
        
        # If it's already a valid STIX ID with correct prefix, return it
        if self._is_valid_stix_id(standard_id):
            return standard_id
        
        # Map entity types to STIX object types
        entity_type_mapping = {
            "IPv4-Addr": "ipv4-addr",
            "IPv6-Addr": "ipv6-addr", 
            "Domain-Name": "domain-name",
            "Url": "url",
            "Email-Addr": "email-addr",
            "Mac-Addr": "mac-addr",
            "Autonomous-System": "autonomous-system",
            "Process": "process",
            "User-Account": "user-account",
            "Hostname": "x-netmanageit-hostname",
            "Software": "x-netmanageit-software",
            "Cryptocurrency-Wallet": "x-netmanageit-cryptocurrency-wallet",
            "Artifact": "artifact",
            "Indicator": "indicator"
        }
        
        stix_object_type = entity_type_mapping.get(entity_type, "artifact")
        
        # If standard_id is a UUID, construct a valid STIX ID
        if self._is_valid_uuid(standard_id):
            return f"{stix_object_type}--{standard_id}"
        
        # If standard_id is not a UUID, try to extract UUID from it
        # Look for UUID pattern in the string
        import re
        uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        uuid_match = re.search(uuid_pattern, standard_id, re.IGNORECASE)
        
        if uuid_match:
            uuid_part = uuid_match.group()
            return f"{stix_object_type}--{uuid_part}"
        
        # If no UUID found, generate a new one
        import uuid
        new_uuid = str(uuid.uuid4())
        return f"{stix_object_type}--{new_uuid}"
