curl -X POST "https://opencti.netmanageit.com/graphql" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 56ed1bf8-c1e8-4a88-bcf5-a8519ad6e9a4" \
  -d @- <<'EOF'
{
  "query": "query StixCyberObservablesWithDetails($types: [String], $search: String, $count: Int!, $cursor: ID, $orderBy: StixCyberObservablesOrdering, $orderMode: OrderingMode, $filters: FilterGroup) { stixCyberObservables(types: $types, search: $search, first: $count, after: $cursor, orderBy: $orderBy, orderMode: $orderMode, filters: $filters) { edges { node { id standard_id entity_type observable_value created_at updated_at parent_types createdBy { id name entity_type } objectMarking { id definition x_opencti_color } objectLabel { id value color } creators { id name } ...StixCyberObservable_stixCyberObservable ...StixCyberObservableDetails_stixCyberObservable ...StixCyberObservableIndicators_stixCyberObservable ...StixCoreObjectContent_stixCoreObject __typename } cursor } pageInfo { endCursor hasNextPage globalCount } } } fragment StixCyberObservable_stixCyberObservable on StixCyberObservable { id entity_type standard_id x_opencti_stix_ids spec_version created_at updated_at } fragment StixCyberObservableDetails_stixCyberObservable on StixCyberObservable { id entity_type x_opencti_score x_opencti_description observable_value ... on IPv4Addr { value } ... on IPv6Addr { value } ... on DomainName { value } ... on Url { value } ... on EmailAddr { value display_name } ... on MacAddr { value } ... on AutonomousSystem { number rir } ... on Process { pid command_line } ... on UserAccount { account_login display_name } } fragment StixCyberObservableIndicators_stixCyberObservable on StixCyberObservable { id indicators(first: 50) { edges { node { id name pattern_type created_at updated_at } } } } fragment StixCoreObjectContent_stixCoreObject on StixCoreObject { id entity_type objectMarking { id definition x_opencti_color } objectLabel { id value color } externalReferences { edges { node { id source_name url description } } } importFiles(first: 10) { edges { node { id name uploadStatus } } } exportFiles(first: 10) { edges { node { id name uploadStatus } } } }",
  "variables": {
    "count": 1,
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
}
EOF
