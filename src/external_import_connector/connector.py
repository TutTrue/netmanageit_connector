import sys
from datetime import datetime
import time
import traceback
from typing import Optional

from pycti import OpenCTIConnectorHelper
from src.utils.opencti_netmanageit_client import OpenCTINetManageITClient
from src.utils.config_variables import Config
from src.utils.opencti_stix_converter import OpenCTISTIXConverter


class ConnectorTemplate:
    """
    ---

    Attributes
        - `config (Config())`:
            Initialize the connector with necessary configuration environment variables

        - `helper (OpenCTIConnectorHelper(config))`:
            This is the helper to use.
            ALL connectors have to instantiate the connector helper with configurations.
            Doing this will do a lot of operations behind the scene.

        - `stix_client (ConnectorConverter(helper))`:
            Provide methods for converting various types of input data into STIX 2.1 objects.

    ---

    """

    def __init__(self):
        """
        Initialize the Connector with necessary configurations
        """

        # Load configuration file and connection helper
        self.config = Config()
        self.helper = OpenCTIConnectorHelper(self.config.load)
        self.client = OpenCTINetManageITClient(self.helper, self.config)

    def run(self) -> None:
        """
        Run the main process encapsulated in a scheduler
        It allows you to schedule the process to run at a certain intervals
        This specific scheduler from the pycti connector helper will also check the queue size of a connector
        If `CONNECTOR_QUEUE_THRESHOLD` is set, if the connector's queue size exceeds the queue threshold,
        the connector's main process will not run until the queue is ingested and reduced sufficiently,
        allowing it to restart during the next scheduler check. (default is 500MB)
        It requires the `duration_period` connector variable in ISO-8601 standard format
        Example: `CONNECTOR_DURATION_PERIOD=PT5M` => Will run the process every 5 minutes
        :return: None
        """
        try:
            self.process_message()
        except (KeyboardInterrupt, SystemExit):
            self.helper.log_info("Connector stop")
            sys.exit(0)
        except Exception:  # pylint:disable=broad-exception-caught
            self.helper.log_error(traceback.format_exc())
        if self.helper.connect_run_and_terminate:
            self.helper.log_info("Connector stop")
            self.helper.force_ping()
            sys.exit(0)
        sys.exit(0)

    def process_message(self) -> None:
        """
        Connector main process to collect intelligence
        :return: None
        """
        self.helper.connector_logger.info(
            "[CONNECTOR] Starting connector...",
            {"connector_name": self.helper.connect_name},
        )

        try:
            # Get the current state
            now = datetime.now()
            current_timestamp = int(datetime.timestamp(now))
            current_state = self.helper.get_state()

            if current_state is not None and "last_run" in current_state:
                last_run = current_state["last_run"]

                self.helper.connector_logger.info(
                    "[CONNECTOR] Connector last run",
                    {"last_run_datetime": last_run},
                )
            else:
                self.helper.connector_logger.info(
                    "[CONNECTOR] Connector has never run..."
                )

            # Friendly name will be displayed on OpenCTI platform
            friendly_name = "OpenCTI NetManageIT Connector"

            # Initiate a new work
            work_id = self.helper.api.work.initiate_work(
                self.helper.connect_id, friendly_name
            )

            self.helper.connector_logger.info(
                "[CONNECTOR] Running connector...",
                {"connector_name": self.helper.connect_name},
            )

            # Performing the collection of intelligence
            stix_objects = self._collect_intelligence()

            # Note: STIX objects are now sent individually for each file in _collect_intelligence
            # No need to send a bundle here anymore
            
            current_state = self.helper.get_state()
            current_state_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
            last_run_datetime = datetime.utcfromtimestamp(current_timestamp).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            if current_state:
                current_state["last_run"] = current_state_datetime
            else:
                current_state = {"last_run": current_state_datetime}
            self.helper.set_state(current_state)

            message = (
                f"{self.helper.connect_name} connector successfully run, storing last_run as "
                + str(last_run_datetime)
            )

            self.helper.api.work.to_processed(work_id, message)
            self.helper.connector_logger.info(message)

        except (KeyboardInterrupt, SystemExit):
            self.helper.connector_logger.info(
                "[CONNECTOR] Connector stopped...",
                {"connector_name": self.helper.connect_name},
            )
            sys.exit(0)
        except Exception as err:
            self.helper.connector_logger.error(str(err))

    def _collect_intelligence(self) -> list:
        """
        Collect intelligence from OpenCTI NetManageIT and convert into STIX objects
        Send STIX objects in batches
        :return: List of STIX objects (empty list since we send individually)
        """
        stix_objects = []
        observable_count = 0
        indicator_count = 0
        relationship_count = 0
        
        # First, process all observables
        self.helper.connector_logger.info("Starting to fetch observables from OpenCTI NetManageIT...")
        
        for observable_data in self.client.get_observables():
            observable_value = observable_data.get('observable_value', 'Unknown')
            entity_type = observable_data.get('entity_type', '')
            
            self.helper.connector_logger.info(
                f"Processing observable: {observable_value}"
            )
            
            # Check if observable already exists
            if self._check_existing_observable(observable_value, entity_type):
                self.helper.connector_logger.info(
                    f"Skipping existing observable: {observable_value} ({entity_type})"
                )
                continue
            
            # Convert observable to STIX
            stix_converter = OpenCTISTIXConverter(self.helper)
            observable = stix_converter.create_observable_from_opencti(observable_data)
            
            if observable:
                stix_objects.append(observable)
                observable_count += 1
                
                # Send in batches of 100
                if len(stix_objects) >= 10:
                    self._send_stix_batch(stix_objects)
                    stix_objects = []
                    break
        
        # Send remaining observables
        if stix_objects:
            self._send_stix_batch(stix_objects)
            stix_objects = []
        
        self.helper.connector_logger.info(
            f"Completed processing {observable_count} observables"
        )
        
        # Now, process all indicators
        self.helper.connector_logger.info("Starting to fetch indicators from OpenCTI NetManageIT...")
        
        for indicator_data in self.client.get_indicators():
            indicator_name = indicator_data.get('name', 'Unknown')
            pattern = indicator_data.get('pattern', '')
            
            self.helper.connector_logger.info(
                f"Processing indicator: {indicator_name}"
            )
            
            # Check if indicator already exists
            if pattern and self._check_existing_indicator(pattern):
                self.helper.connector_logger.info(
                    f"Skipping existing indicator: {indicator_name} (pattern: {pattern})"
                )
                continue
            
            # Convert indicator to STIX
            stix_converter = OpenCTISTIXConverter(self.helper)
            indicator = stix_converter.create_indicator_from_opencti(indicator_data)
            
            if indicator:
                stix_objects.append(indicator)
                indicator_count += 1
                
                # Create relationships with observables if they exist
                observables_data = indicator_data.get("observables", {}).get("edges", [])
                for observable_edge in observables_data:
                    observable_node = observable_edge.get("node", {})
                    observable_standard_id = observable_node.get("standard_id")
                    
                    if observable_standard_id:
                        # Find the observable in OpenCTI by its standard_id
                        # observable_stix_id = self._find_observable_by_standard_id(observable_standard_id)
                        observable_stix_id = observable_standard_id
                        if observable_stix_id:
                            self.helper.connector_logger.info(
                                f"Creating relationship: {indicator['id']} indicates {observable_stix_id}"
                            )
                            
                            # Ensure both IDs are valid STIX format
                            indicator_id = stix_converter._ensure_valid_stix_id(indicator["id"], "Indicator")
                            observable_id = stix_converter._ensure_valid_stix_id(observable_stix_id, "Observable")
                            
                            relationship = stix_converter.create_relationship(
                                indicator_id, "based-on", observable_id
                            )
                            if relationship:
                                self.helper.connector_logger.info(
                                    f"Created relationship object: {relationship.get('id', 'No ID')} "
                                    f"from {relationship.get('source_ref', 'No source')} "
                                    f"to {relationship.get('target_ref', 'No target')}"
                                )
                                stix_objects.append(relationship)
                                relationship_count += 1
                            else:
                                self.helper.connector_logger.error(
                                    f"Failed to create relationship from {indicator['id']} to {observable_stix_id}"
                                )
                        else:
                            self.helper.connector_logger.warning(
                                f"Could not find observable with standard_id {observable_standard_id} for indicator {indicator_name}"
                            )
                
                # Send in batches of 100
                if len(stix_objects) >= 10:
                    self._send_stix_batch(stix_objects)
                    stix_objects = []
                    break
        
        # Send remaining indicators and relationships
        if stix_objects:
            self._send_stix_batch(stix_objects)
        
        self.helper.connector_logger.info(
            f"Completed processing {indicator_count} indicators and {relationship_count} relationships"
        )
        
        return []  # Return empty list since we sent individually

    def _check_existing_indicator(self, pattern: str) -> bool:
        """
        Check if an indicator with the given pattern already exists in OpenCTI
        :param pattern: STIX pattern to check
        :return: True if indicator exists, False otherwise
        """
        try:
            existing = self.helper.api.indicator.list(
                filters={
                    "mode": "and",
                    "filters": [{"key": "pattern", "values": [pattern]}],
                    "filterGroups": []
                }
            )
            return len(existing) > 0
        except Exception as err:
            self.helper.connector_logger.warning(f"Error checking existing indicator: {err}")
            return False

    def _check_existing_observable(self, observable_value: str, entity_type: str) -> bool:
        """
        Check if an observable with the given value and type already exists in OpenCTI
        :param observable_value: The observable value to check
        :param entity_type: The entity type (e.g., 'IPv4-Addr', 'Domain-Name')
        :return: True if observable exists, False otherwise
        """
        try:
            # Map entity types to OpenCTI filter keys
            filter_key_map = {
                "IPv4-Addr": "value",
                "IPv6-Addr": "value", 
                "Domain-Name": "value",
                "Url": "value",
                "Email-Addr": "value",
                "File": "name"
            }
            
            filter_key = filter_key_map.get(entity_type, "value")
            existing = self.helper.api.stix_cyber_observable.list(
                filters={
                    "mode": "and",
                    "filters": [
                        {"key": filter_key, "values": [observable_value]},
                        {"key": "entity_type", "values": [entity_type]}
                    ],
                    "filterGroups": []
                }
            )
            return len(existing) > 0
        except Exception as err:
            self.helper.connector_logger.warning(f"Error checking existing observable: {err}")
            return False

    def _find_observable_by_standard_id(self, standard_id: str) -> Optional[str]:
        """
        Find an existing observable in OpenCTI by its standard_id
        :param standard_id: The standard_id to search for
        :return: The STIX ID of the observable if found, None otherwise
        """
        try:
            existing = self.helper.api.stix_cyber_observable.list(
                filters={
                    "mode": "and",
                    "filters": [{"key": "standard_id", "values": [standard_id]}],
                    "filterGroups": []
                }
            )
            if existing and len(existing) > 0:
                observable = existing[0]
                # Return the standard_id if it's already a proper STIX ID, otherwise construct it
                if "--" in observable.get("standard_id", ""):
                    return observable["standard_id"]
                else:
                    # Construct STIX ID from entity_type and UUID
                    entity_type = observable.get("entity_type", "artifact")
                    uuid_part = observable.get("id", "")
                    if uuid_part:
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
                            "Artifact": "artifact"
                        }
                        stix_object_type = entity_type_mapping.get(entity_type, "artifact")
                        return f"{stix_object_type}--{uuid_part}"
            return None
        except Exception as err:
            self.helper.connector_logger.warning(f"Error finding observable by standard_id {standard_id}: {err}")
            return None

    def _send_stix_batch(self, stix_objects: list) -> None:
        """
        Send a batch of STIX objects to OpenCTI
        :param stix_objects: List of STIX objects to send
        """
        try:
            if stix_objects:
                # Log what types of objects we're sending
                object_types = {}
                for obj in stix_objects:
                    obj_type = obj.get("type", "unknown")
                    object_types[obj_type] = object_types.get(obj_type, 0) + 1
                
                self.helper.connector_logger.info(
                    f"Sending batch of {len(stix_objects)} STIX objects: {object_types}"
                )
                
                # Create and send bundle
                bundle = self.helper.stix2_create_bundle(stix_objects)
                bundles_sent = self.helper.send_stix2_bundle(bundle)
                
                self.helper.connector_logger.info(
                    f"Successfully sent batch of {len(stix_objects)} STIX objects",
                    {"bundles_sent": len(bundles_sent), "object_types": object_types}
                )
        except Exception as err:
            self.helper.connector_logger.error(f"Error sending STIX batch: {err}")
            import traceback
            self.helper.connector_logger.error(f"Traceback: {traceback.format_exc()}")
