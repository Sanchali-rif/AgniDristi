-- Object counts and TCI ranges for industrial/ambiguous segregation.
SELECT
    COALESCE(temporal_source_hint, 'unlabeled') AS temporal_source_hint,
    COUNT(*) AS object_count,
    ROUND(AVG(tci)::numeric, 4) AS average_tci,
    ROUND(MIN(tci)::numeric, 4) AS minimum_tci,
    ROUND(MAX(tci)::numeric, 4) AS maximum_tci,
    ROUND(AVG(seasonal_concentration)::numeric, 4)
        AS average_seasonal_concentration
FROM thermal_objects
GROUP BY COALESCE(temporal_source_hint, 'unlabeled')
ORDER BY object_count DESC;

-- Inspect individual persistent objects and the evidence behind each hint.
SELECT
    object_uid,
    temporal_source_hint,
    ROUND(tci::numeric, 4) AS tci,
    active_months,
    ROUND(persistence_ratio::numeric, 4) AS persistence_ratio,
    ROUND(source_persistence_ratio::numeric, 4)
        AS source_persistence_ratio,
    longest_active_run,
    max_inactive_gap,
    ROUND(seasonal_concentration::numeric, 4)
        AS seasonal_concentration,
    detection_count,
    latitude,
    longitude
FROM thermal_objects
WHERE temporal_source_hint IN (
    'industrial',
    'ambiguous'
)
ORDER BY temporal_source_hint, tci DESC NULLS LAST;
