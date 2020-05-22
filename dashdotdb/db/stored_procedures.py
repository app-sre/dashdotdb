VULNERABILITIES = """
DROP FUNCTION IF EXISTS get_vulnerabilities(cluster_name text, namespace_name text);
CREATE FUNCTION get_vulnerabilities(cluster_name text, namespace_name text)
    RETURNS TABLE(repository VARCHAR,
                  name VARCHAR,
                  manifest TEXT,
                  affected_pods BIGINT,
                  vulnerability VARCHAR,
                  severity VARCHAR,
                  package VARCHAR,
                  current_version VARCHAR,
                  fixed_in_version VARCHAR,
                  link VARCHAR)
AS $$
BEGIN
    RETURN QUERY
        WITH last_token as (
            SELECT token.id as id
            FROM token, pod, namespace, cluster
            WHERE pod.token_id = token.id
              AND namespace.id = pod.namespace_id
              AND cluster.name = cluster_name
              AND namespace.name = namespace_name
              AND cluster.id = namespace.cluster_id
            ORDER BY token.timestamp DESC
            LIMIT 1)
        SELECT
            image.name as repository,
            feature.namespacename as name,
            SUBSTR(image.manifest, 1, 14) as manifest,
            COUNT(pod.name) as affected_pods,
            vulnerability.name as vulnerability,
            severity.name as severity,
            feature.name as package,
            feature.version as current_version,
            vulnerability.fixedby as fixed_in_version,
            vulnerability.link as link
        FROM cluster,
             namespace,
             pod,
             image,
             imagefeature,
             feature,
             vulnerability,
             severity,
             last_token
        WHERE pod.namespace_id = namespace.id
          AND namespace.cluster_id = cluster.id
          AND cluster.id = namespace.cluster_id
          AND pod.image_id = image.id
          AND image.id = imagefeature.image_id
          AND imagefeature.feature_id = feature.id
          AND feature.id = vulnerability.feature_id
          AND vulnerability.severity_id = severity.id
          AND pod.token_id = last_token.id
          AND cluster.name = cluster_name
          AND namespace.name = namespace_name
        GROUP BY
            image.name,
            feature.namespacename,
            image.manifest,
            vulnerability.name,
            severity.name,
            feature.name,
            feature.version,
            vulnerability.fixedby,
            vulnerability.link;
END;
$$ LANGUAGE 'plpgsql';

DROP FUNCTION IF EXISTS get_severity_count(cluster_name text, namespace_name text, severity_name text);
CREATE FUNCTION get_severity_count(cluster_name text, namespace_name text, severity_name text)
    RETURNS TABLE(vulnerability VARCHAR,
                  feature VARCHAR,
                  severity TEXT)
AS $$
BEGIN
    RETURN QUERY
        WITH last_token as (
            SELECT token.id
            FROM token, pod, namespace, cluster
            WHERE pod.token_id = token.id
              AND namespace.id = pod.namespace_id
              AND cluster.name = cluster_name
              AND namespace.name = namespace_name
              AND cluster.id = namespace.cluster_id
            ORDER BY token.timestamp DESC
            LIMIT 1)
        SELECT
            DISTINCT vulnerability.name as vulnerability,
                     feature.name as feature,
                     severity_name as severity
        FROM cluster,
             namespace,
             pod,
             image,
             imagefeature,
             feature,
             vulnerability,
             severity,
             last_token
        WHERE pod.namespace_id = namespace.id
          AND namespace.cluster_id = cluster.id
          AND cluster.id = namespace.cluster_id
          AND pod.image_id = image.id
          AND image.id = imagefeature.image_id
          AND imagefeature.feature_id = feature.id
          AND feature.id = vulnerability.feature_id
          AND vulnerability.severity_id = severity.id
          AND cluster.name = cluster_name
          AND namespace.name = namespace_name
          AND severity.name = severity_name
        GROUP BY feature.name,
                 vulnerability.name,
                 severity.name;
END;
$$ LANGUAGE 'plpgsql';
"""
