import time
import json
from typing import Generator, Any, Dict, List
from httpx import Client, ReadTimeout, ConnectTimeout, RequestError
from src.utils.config_variables import Config
from pycti import OpenCTIConnectorHelper


class OpenCTINetManageITClient:
    """
    OpenCTI NetManageIT Client to interact with OpenCTI GraphQL API
    """

    def __init__(self, helper: OpenCTIConnectorHelper, config: Config):
        """
        Initialize the OpenCTI NetManageIT client with necessary configurations
        """
        self.helper = helper
        self.config = config
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.netmanageit_token}",
        }
        self.base_url = self.config.netmanageit_url
        self.cooldown_seconds = 1
        self.max_retries = 50
        self.retry_delay = 10  # seconds

    def _make_request_with_retry(self, query: str, variables: Dict, operation_name: str) -> Dict:
        """
        Make HTTP request with retry logic for timeout and connection errors
        :param query: GraphQL query string
        :param variables: GraphQL variables
        :param operation_name: Name of the operation for logging
        :return: Response data
        """
        for attempt in range(self.max_retries):
            try:
                with Client() as client:
                    response = client.post(
                        f"{self.base_url}/graphql",
                        headers=self.headers,
                        json={"query": query, "variables": variables},
                        timeout=60.0  # Increased timeout to 60 seconds
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    if "errors" in data:
                        self.helper.connector_logger.error(f"GraphQL errors in {operation_name}: {data['errors']}")
                        return data
                    
                    return data
                    
            except (ReadTimeout, ConnectTimeout) as err:
                self.helper.connector_logger.warning(
                    f"Timeout error in {operation_name} (attempt {attempt + 1}/{self.max_retries}): {err}"
                )
                if attempt < self.max_retries - 1:
                    self.helper.connector_logger.info(f"Retrying {operation_name} in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    self.helper.connector_logger.error(f"Max retries exceeded for {operation_name}. Giving up.")
                    raise
                    
            except RequestError as err:
                self.helper.connector_logger.warning(
                    f"Request error in {operation_name} (attempt {attempt + 1}/{self.max_retries}): {err}"
                )
                if attempt < self.max_retries - 1:
                    self.helper.connector_logger.info(f"Retrying {operation_name} in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    self.helper.connector_logger.error(f"Max retries exceeded for {operation_name}. Giving up.")
                    raise
                    
            except Exception as err:
                self.helper.connector_logger.error(f"Unexpected error in {operation_name}: {err}")
                raise

    def get_observables(self) -> Generator[Dict, Any, None]:
        """
        Fetch observables from OpenCTI NetManageIT instance
        :return: Generator of observable data
        """
        query = """
        query StixCyberObservablesWithDetails($types: [String], $search: String, $count: Int!, $cursor: ID, $orderBy: StixCyberObservablesOrdering, $orderMode: OrderingMode, $filters: FilterGroup) { 
            stixCyberObservables(types: $types, search: $search, first: $count, after: $cursor, orderBy: $orderBy, orderMode: $orderMode, filters: $filters) { 
                edges { 
                    node { 
                        id 
                        standard_id 
                        entity_type 
                        observable_value 
                        created_at 
                        updated_at 
                        parent_types 
                        createdBy { 
                            id 
                            name 
                            entity_type 
                        } 
                        objectMarking { 
                            id 
                            definition 
                            x_opencti_color 
                        } 
                        objectLabel { 
                            id 
                            value 
                            color 
                        } 
                        creators { 
                            id 
                            name 
                        } 
                        ...StixCyberObservable_stixCyberObservable 
                        ...StixCyberObservableDetails_stixCyberObservable 
                        ...StixCyberObservableIndicators_stixCyberObservable 
                        ...StixCoreObjectContent_stixCoreObject 
                        __typename 
                    } 
                    cursor 
                } 
                pageInfo { 
                    endCursor 
                    hasNextPage 
                    globalCount 
                } 
            } 
        }
        fragment StixCyberObservable_stixCyberObservable on StixCyberObservable { 
            id 
            entity_type 
            standard_id 
            x_opencti_stix_ids 
            spec_version 
            created_at 
            updated_at 
        } 
        fragment StixCyberObservableDetails_stixCyberObservable on StixCyberObservable { 
            id 
            entity_type 
            x_opencti_score 
            x_opencti_description 
            observable_value 
            ... on IPv4Addr { 
                value 
            } 
            ... on IPv6Addr { 
                value 
            } 
            ... on DomainName { 
                value 
            } 
            ... on Url { 
                value 
            } 
            ... on EmailAddr { 
                value 
                display_name 
            } 
            ... on MacAddr { 
                value 
            } 
            ... on AutonomousSystem { 
                number 
                rir 
            } 
            ... on Process { 
                pid 
                command_line 
            } 
            ... on UserAccount { 
                account_login 
                display_name 
            } 
        } 
        fragment StixCyberObservableIndicators_stixCyberObservable on StixCyberObservable { 
            id 
            indicators(first: 50) { 
                edges { 
                    node { 
                        id 
                        name 
                        pattern_type 
                        created_at 
                        updated_at 
                    } 
                } 
            } 
        } 
        fragment StixCoreObjectContent_stixCoreObject on StixCoreObject { 
            id 
            entity_type 
            objectMarking { 
                id 
                definition 
                x_opencti_color 
            } 
            objectLabel { 
                id 
                value 
                color 
            } 
            externalReferences { 
                edges { 
                    node { 
                        id 
                        source_name 
                        url 
                        description 
                    } 
                } 
            } 
            importFiles(first: 10) { 
                edges { 
                    node { 
                        id 
                        name 
                        uploadStatus 
                    } 
                } 
            } 
            exportFiles(first: 10) { 
                edges { 
                    node { 
                        id 
                        name 
                        uploadStatus 
                    } 
                } 
            } 
        }
        """
        
        variables = {
            "count": 1000,  # Fetch in batches of 1000
            "orderMode": "desc",
            "orderBy": "created_at",
            "filters": {
                "mode": "and",
                "filters": [
                    {
                        "key": "entity_type",
                        "values": ["Stix-Cyber-Observable"],
                        "operator": "eq",
                        "mode": "or"
                    }
                ],
                "filterGroups": []
            }
        }
        
        cursor = None
        has_next_page = True
        
        while has_next_page:
            if cursor:
                variables["cursor"] = cursor
                
            try:
                data = self._make_request_with_retry(query, variables, "get_observables")
                
                if "errors" in data:
                    self.helper.connector_logger.error(f"GraphQL errors: {data['errors']}")
                    break
                
                observables_data = data.get("data", {}).get("stixCyberObservables", {})
                edges = observables_data.get("edges", [])
                page_info = observables_data.get("pageInfo", {})
                
                for edge in edges:
                    yield edge["node"]
                
                has_next_page = page_info.get("hasNextPage", False)
                cursor = page_info.get("endCursor")
                
                self.helper.connector_logger.info(
                    f"Fetched {len(edges)} observables, hasNextPage: {has_next_page}"
                )
                
                if has_next_page:
                    time.sleep(self.cooldown_seconds)
                    
            except (ReadTimeout, ConnectTimeout, RequestError) as err:
                self.helper.connector_logger.error(f"Failed to fetch observables after retries: {err}")
                # Don't break the loop, just log the error and continue with next iteration
                # This prevents the connector from exiting completely
                self.helper.connector_logger.info("Continuing with next batch of observables...")
                break
            except Exception as err:
                self.helper.connector_logger.error(f"Unexpected error fetching observables: {err}")
                break

    def get_indicators(self) -> Generator[Dict, Any, None]:
        """
        Fetch indicators from OpenCTI NetManageIT instance
        :return: Generator of indicator data
        """
        query = """
        query IndicatorsWithDetails($search: String, $count: Int!, $cursor: ID, $filters: FilterGroup, $orderBy: IndicatorsOrdering, $orderMode: OrderingMode) { 
            indicators(search: $search, first: $count, after: $cursor, filters: $filters, orderBy: $orderBy, orderMode: $orderMode) { 
                edges { 
                    node { 
                        id 
                        ...Indicator_indicator 
                        ...IndicatorDetails_indicator 
                        ...IndicatorObservables_indicator 
                        ...IndicatorExtraFields_indicator 
                        ...FileImportViewer_entity 
                        ...FileExportViewer_entity 
                        ...FileExternalReferencesViewer_entity 
                        ...WorkbenchFileViewer_entity 
                        ...StixCoreObjectContent_stixCoreObject 
                        ...StixCoreObjectSharingListFragment 
                        __typename 
                    } 
                    cursor 
                } 
                pageInfo { 
                    endCursor 
                    hasNextPage 
                    globalCount 
                } 
            } 
        }
        fragment Indicator_indicator on Indicator { 
            id 
            standard_id 
            entity_type 
            x_opencti_stix_ids 
            spec_version 
            revoked 
            confidence 
            created 
            modified 
            created_at 
            updated_at 
            createdBy { 
                __typename 
                id 
                name 
                entity_type 
                x_opencti_reliability 
            } 
            creators { 
                id 
                name 
            } 
            objectMarking { 
                id 
                definition_type 
                definition 
                x_opencti_order 
                x_opencti_color 
            } 
            objectLabel { 
                id 
                value 
                color 
            } 
            name 
            pattern 
            pattern_type 
            status { 
                id 
                order 
                template { 
                    id 
                    name 
                    color 
                } 
            } 
            workflowEnabled 
        } 
        fragment IndicatorDetails_indicator on Indicator { 
            id 
            description 
            pattern 
            valid_from 
            valid_until 
            x_opencti_score 
            x_opencti_detection 
            x_mitre_platforms 
            indicator_types 
            decay_base_score 
            decay_base_score_date 
            decay_history { 
                score 
                updated_at 
            } 
            decay_applied_rule { 
                decay_rule_id 
                decay_lifetime 
                decay_pound 
                decay_points 
                decay_revoke_score 
            } 
            decayLiveDetails { 
                live_score 
                live_points { 
                    score 
                    updated_at 
                } 
            } 
            decayChartData { 
                live_score_serie { 
                    updated_at 
                    score 
                } 
            } 
            objectLabel { 
                id 
                value 
                color 
            } 
            killChainPhases { 
                id 
                entity_type 
                kill_chain_name 
                phase_name 
                x_opencti_order 
            } 
        } 
        fragment IndicatorObservables_indicator on Indicator { 
            id 
            standard_id 
            name 
            parent_types 
            entity_type 
            observables(first: 100) { 
                edges { 
                    node { 
                        __typename 
                        id 
                        standard_id 
                        entity_type 
                        parent_types 
                        observable_value 
                        created_at 
                        updated_at 
                    } 
                } 
                pageInfo { 
                    globalCount 
                } 
            } 
        } 
        fragment IndicatorExtraFields_indicator on Indicator { 
            x_opencti_main_observable_type 
            draftVersion { 
                draft_id 
                draft_operation 
            } 
            objectMarking { 
                id 
                definition_type 
                definition 
                x_opencti_order 
                x_opencti_color 
            } 
            creators { 
                id 
                name 
            } 
        } 
        fragment FileImportViewer_entity on StixCoreObject { 
            id 
            entity_type 
            importFiles(first: 500) { 
                edges { 
                    node { 
                        id 
                        name 
                        uploadStatus 
                        lastModified 
                        lastModifiedSinceMin 
                        metaData { 
                            mimetype 
                        } 
                        __typename 
                    } 
                    cursor 
                } 
                pageInfo { 
                    endCursor 
                    hasNextPage 
                } 
            } 
        } 
        fragment FileExportViewer_entity on StixCoreObject { 
            id 
            exportFiles(first: 500) { 
                edges { 
                    node { 
                        id 
                        name 
                        uploadStatus 
                        lastModified 
                        lastModifiedSinceMin 
                        metaData { 
                            mimetype 
                        } 
                        __typename 
                    } 
                    cursor 
                } 
                pageInfo { 
                    endCursor 
                    hasNextPage 
                } 
            } 
        } 
        fragment FileExternalReferencesViewer_entity on StixCoreObject { 
            id 
            entity_type 
            externalReferences { 
                edges { 
                    node { 
                        source_name 
                        url 
                        description 
                        importFiles(first: 500) { 
                            edges { 
                                node { 
                                    id 
                                    name 
                                    uploadStatus 
                                    lastModified 
                                    lastModifiedSinceMin 
                                    metaData { 
                                        mimetype 
                                    } 
                                    __typename 
                                } 
                                cursor 
                            } 
                            pageInfo { 
                                endCursor 
                                hasNextPage 
                            } 
                        } 
                        id 
                    } 
                } 
            } 
        } 
        fragment WorkbenchFileViewer_entity on StixCoreObject { 
            id 
            entity_type 
            pendingFiles(first: 500) { 
                edges { 
                    node { 
                        id 
                        name 
                        uploadStatus 
                        lastModified 
                        lastModifiedSinceMin 
                        metaData { 
                            mimetype 
                        } 
                        __typename 
                    } 
                    cursor 
                } 
                pageInfo { 
                    endCursor 
                    hasNextPage 
                } 
            } 
        } 
        fragment StixCoreObjectContent_stixCoreObject on StixCoreObject { 
            id 
            entity_type 
            objectMarking { 
                id 
                definition_type 
                definition 
                x_opencti_order 
                x_opencti_color 
            } 
            importFiles(first: 500) { 
                edges { 
                    node { 
                        id 
                        name 
                        uploadStatus 
                        lastModified 
                        lastModifiedSinceMin 
                        __typename 
                    } 
                    cursor 
                } 
                pageInfo { 
                    endCursor 
                    hasNextPage 
                } 
            } 
            exportFiles(first: 500) { 
                edges { 
                    node { 
                        id 
                        name 
                        uploadStatus 
                        lastModified 
                        lastModifiedSinceMin 
                        __typename 
                    } 
                    cursor 
                } 
                pageInfo { 
                    endCursor 
                    hasNextPage 
                } 
            } 
            externalReferences { 
                edges { 
                    node { 
                        source_name 
                        url 
                        description 
                        id 
                    } 
                } 
            } 
        } 
        fragment StixCoreObjectSharingListFragment on StixCoreObject { 
            id 
            objectOrganization { 
                id 
                name 
            } 
        }
        """
        
        variables = {
            "count": 1000,  # Fetch in batches of 1000
            "orderMode": "desc",
            "orderBy": "created",
            "filters": {
                "mode": "and",
                "filters": [
                    {
                        "key": "entity_type",
                        "values": ["Indicator"],
                        "operator": "eq",
                        "mode": "or"
                    }
                ],
                "filterGroups": []
            }
        }
        
        cursor = None
        has_next_page = True
        
        while has_next_page:
            if cursor:
                variables["cursor"] = cursor
                
            try:
                data = self._make_request_with_retry(query, variables, "get_indicators")
                
                if "errors" in data:
                    self.helper.connector_logger.error(f"GraphQL errors: {data['errors']}")
                    break
                
                indicators_data = data.get("data", {}).get("indicators", {})
                edges = indicators_data.get("edges", [])
                page_info = indicators_data.get("pageInfo", {})
                
                for edge in edges:
                    yield edge["node"]
                
                has_next_page = page_info.get("hasNextPage", False)
                cursor = page_info.get("endCursor")
                
                self.helper.connector_logger.info(
                    f"Fetched {len(edges)} indicators, hasNextPage: {has_next_page}"
                )
                
                if has_next_page:
                    time.sleep(self.cooldown_seconds)
                    
            except (ReadTimeout, ConnectTimeout, RequestError) as err:
                self.helper.connector_logger.error(f"Failed to fetch indicators after retries: {err}")
                # Don't break the loop, just log the error and continue with next iteration
                # This prevents the connector from exiting completely
                self.helper.connector_logger.info("Continuing with next batch of indicators...")
                break
            except Exception as err:
                self.helper.connector_logger.error(f"Unexpected error fetching indicators: {err}")
                break
