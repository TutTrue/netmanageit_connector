import sys
from datetime import datetime
import time
import traceback

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
        
        # Create a mapping of standard_id to observable for relationship creation
        observable_mapping = {}
        
        # First, process all observables
        self.helper.connector_logger.info("Starting to fetch observables from OpenCTI NetManageIT...")
        
        for observable_data in self.client.get_observables():
            self.helper.connector_logger.info(
                f"Processing observable: {observable_data.get('observable_value', 'Unknown')}"
            )
            
            # Convert observable to STIX
            stix_converter = OpenCTISTIXConverter(self.helper)
            observable = stix_converter.create_observable_from_opencti(observable_data)
            
            if observable:
                stix_objects.append(observable)
                observable_count += 1
                
                # Store mapping for relationship creation
                standard_id = observable_data.get("standard_id")
                if standard_id:
                    observable_mapping[standard_id] = observable["id"]
                
                # Send in batches of 100
                if len(stix_objects) >= 100:
                    self._send_stix_batch(stix_objects)
                    stix_objects = []
        
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
            self.helper.connector_logger.info(
                f"Processing indicator: {indicator_data.get('name', 'Unknown')}"
            )
            
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
                    
                    if observable_standard_id and observable_standard_id in observable_mapping:
                        relationship = stix_converter.create_relationship(
                            indicator["id"], "indicates", observable_mapping[observable_standard_id]
                        )
                        stix_objects.append(relationship)
                        relationship_count += 1
                
                # Send in batches of 100
                if len(stix_objects) >= 100:
                    self._send_stix_batch(stix_objects)
                    stix_objects = []
        
        # Send remaining indicators and relationships
        if stix_objects:
            self._send_stix_batch(stix_objects)
        
        self.helper.connector_logger.info(
            f"Completed processing {indicator_count} indicators and {relationship_count} relationships"
        )
        
        return []  # Return empty list since we sent individually

    def _send_stix_batch(self, stix_objects: list) -> None:
        """
        Send a batch of STIX objects to OpenCTI
        :param stix_objects: List of STIX objects to send
        """
        try:
            if stix_objects:
                # Create and send bundle
                bundle = self.helper.stix2_create_bundle(stix_objects)
                bundles_sent = self.helper.send_stix2_bundle(bundle)
                
                self.helper.connector_logger.info(
                    f"Sent batch of {len(stix_objects)} STIX objects",
                    {"bundles_sent": len(bundles_sent)}
                )
        except Exception as err:
            self.helper.connector_logger.error(f"Error sending STIX batch: {err}")
