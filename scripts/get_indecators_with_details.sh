curl -X POST "https://opencti.netmanageit.com/graphql" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 56ed1bf8-c1e8-4a88-bcf5-a8519ad6e9a4" \
  -d @- <<'EOF'
{
  "query": "query IndicatorsWithDetails($search: String, $count: Int!, $cursor: ID, $filters: FilterGroup, $orderBy: IndicatorsOrdering, $orderMode: OrderingMode) { indicators(search: $search, first: $count, after: $cursor, filters: $filters, orderBy: $orderBy, orderMode: $orderMode) { edges { node { id ...Indicator_indicator ...IndicatorDetails_indicator ...IndicatorObservables_indicator ...IndicatorExtraFields_indicator ...FileImportViewer_entity ...FileExportViewer_entity ...FileExternalReferencesViewer_entity ...WorkbenchFileViewer_entity ...StixCoreObjectContent_stixCoreObject ...StixCoreObjectSharingListFragment __typename } cursor } pageInfo { endCursor hasNextPage globalCount } } } fragment Indicator_indicator on Indicator { id standard_id entity_type x_opencti_stix_ids spec_version revoked confidence created modified created_at updated_at createdBy { __typename id name entity_type x_opencti_reliability } creators { id name } objectMarking { id definition_type definition x_opencti_order x_opencti_color } objectLabel { id value color } name pattern pattern_type status { id order template { id name color } } workflowEnabled } fragment IndicatorDetails_indicator on Indicator { id description pattern valid_from valid_until x_opencti_score x_opencti_detection x_mitre_platforms indicator_types decay_base_score decay_base_score_date decay_history { score updated_at } decay_applied_rule { decay_rule_id decay_lifetime decay_pound decay_points decay_revoke_score } decayLiveDetails { live_score live_points { score updated_at } } decayChartData { live_score_serie { updated_at score } } objectLabel { id value color } killChainPhases { id entity_type kill_chain_name phase_name x_opencti_order } } fragment IndicatorObservables_indicator on Indicator { id standard_id name parent_types entity_type observables(first: 100) { edges { node { __typename id standard_id entity_type parent_types observable_value created_at updated_at } } pageInfo { globalCount } } } fragment IndicatorExtraFields_indicator on Indicator { x_opencti_main_observable_type draftVersion { draft_id draft_operation } objectMarking { id definition_type definition x_opencti_order x_opencti_color } creators { id name } } fragment FileImportViewer_entity on StixCoreObject { id entity_type importFiles(first: 500) { edges { node { id name uploadStatus lastModified lastModifiedSinceMin metaData { mimetype } __typename } cursor } pageInfo { endCursor hasNextPage } } } fragment FileExportViewer_entity on StixCoreObject { id exportFiles(first: 500) { edges { node { id name uploadStatus lastModified lastModifiedSinceMin metaData { mimetype } __typename } cursor } pageInfo { endCursor hasNextPage } } } fragment FileExternalReferencesViewer_entity on StixCoreObject { id entity_type externalReferences { edges { node { source_name url description importFiles(first: 500) { edges { node { id name uploadStatus lastModified lastModifiedSinceMin metaData { mimetype } __typename } cursor } pageInfo { endCursor hasNextPage } } id } } } } fragment WorkbenchFileViewer_entity on StixCoreObject { id entity_type pendingFiles(first: 500) { edges { node { id name uploadStatus lastModified lastModifiedSinceMin metaData { mimetype } __typename } cursor } pageInfo { endCursor hasNextPage } } } fragment StixCoreObjectContent_stixCoreObject on StixCoreObject { id entity_type objectMarking { id definition_type definition x_opencti_order x_opencti_color } importFiles(first: 500) { edges { node { id name uploadStatus lastModified lastModifiedSinceMin __typename } cursor } pageInfo { endCursor hasNextPage } } exportFiles(first: 500) { edges { node { id name uploadStatus lastModified lastModifiedSinceMin __typename } cursor } pageInfo { endCursor hasNextPage } } externalReferences { edges { node { source_name url description id } } } } fragment StixCoreObjectSharingListFragment on StixCoreObject { id objectOrganization { id name } }",
  "variables": {
    "count": 5,
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
}
EOF
