import json
import logging
from collections import Counter

import numpy as np
import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session


logger = logging.getLogger(__name__)

MODEL_SOURCE = "VNF_XGBOOST"
GEM_SOURCE = "GEM_DATABASE"


def _valid_coordinate(value, minimum, maximum):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    if not np.isfinite(number) or not minimum <= number <= maximum:
        return None

    return number


def _find_nearby_gem_categories(
    db: Session,
    objects: pd.DataFrame,
    primary_radius_m: float,
    fallback_radius_m: float,
    max_radius_m: float,
    extended_radius_m: float
):
    payload = []

    for row_id, (_, row) in enumerate(objects.iterrows()):
        latitude = _valid_coordinate(row.get("latitude"), -90.0, 90.0)
        longitude = _valid_coordinate(row.get("longitude"), -180.0, 180.0)

        if latitude is None or longitude is None:
            continue

        payload.append({
            "row_id": row_id,
            "latitude": latitude,
            "longitude": longitude
        })

    if not payload:
        return {}

    rows = (
        db.execute(
            text("""
                WITH incoming AS (
                    SELECT
                        row_id,
                        ST_SetSRID(
                            ST_MakePoint(longitude, latitude),
                            4326
                        )::geography AS location
                    FROM jsonb_to_recordset(
                        CAST(:payload AS jsonb)
                    ) AS x(
                        row_id integer,
                        latitude double precision,
                        longitude double precision
                    )
                )
                , nearby AS (
                    SELECT
                        i.row_id,
                        g.category,
                        g.gem_id,
                        g.facility_name,
                        g.exact_type,
                        ST_Distance(g.location, i.location) AS distance_m,
                        CASE
                            WHEN ST_DWithin(
                                g.location,
                                i.location,
                                :primary_radius_m
                            ) THEN :primary_radius_m
                            WHEN ST_DWithin(
                                g.location,
                                i.location,
                                :fallback_radius_m
                            ) THEN :fallback_radius_m
                            WHEN ST_DWithin(
                                g.location,
                                i.location,
                                :max_radius_m
                            ) THEN :max_radius_m
                            ELSE :extended_radius_m
                        END AS match_radius_m
                    FROM incoming i
                    JOIN public.gem_data g
                      ON g.location IS NOT NULL
                     AND ST_DWithin(
                            g.location,
                            i.location,
                            :extended_radius_m
                         )
                    WHERE g.category IS NOT NULL
                      AND BTRIM(g.category) <> ''
                )
                SELECT
                    row_id,
                    category,
                    match_radius_m,
                    COUNT(*) AS category_count,
                    (ARRAY_AGG(
                        facility_name
                        ORDER BY distance_m, gem_id
                    ))[1] AS nearest_facility_name,
                    (ARRAY_AGG(
                        exact_type
                        ORDER BY distance_m, gem_id
                    ))[1] AS nearest_exact_type
                FROM nearby
                GROUP BY row_id, category, match_radius_m
            """),
            {
                "payload": json.dumps(payload),
                "primary_radius_m": primary_radius_m,
                "fallback_radius_m": fallback_radius_m,
                "max_radius_m": max_radius_m,
                "extended_radius_m": extended_radius_m
            }
        )
        .mappings()
        .all()
    )

    matches = {}
    for row in rows:
        matches.setdefault(int(row["row_id"]), {}).setdefault(
            float(row["match_radius_m"]),
            {}
        )[str(row["category"])] = {
            "count": int(row["category_count"]),
            "facility_name": row["nearest_facility_name"],
            "exact_type": row["nearest_exact_type"]
        }

    return matches


def _model_classify(classifier, objects: pd.DataFrame):
    classified = classifier.predict(objects)
    classified["classification_source"] = MODEL_SOURCE
    classified["gem_match_count"] = 0
    classified["gem_category_vote_count"] = 0
    classified["gem_match_radius_m"] = np.nan
    classified["gem_facility_name"] = None
    classified["gem_industry_exact_type"] = None
    return classified


def classify_industrial_objects(
    db: Session | None,
    objects: pd.DataFrame,
    classifier,
    primary_radius_m: float,
    fallback_radius_m: float,
    max_radius_m: float,
    extended_radius_m: float
):
    """Classify objects from nearby GEM facilities, falling back to the model.

    The 1st, 2nd, and 3rd radii are considered in order. A wider tier is used
    only when all narrower tiers contain no facilities. A GEM category is
    accepted only when it has a unique highest vote count. No nearby facilities,
    invalid coordinates, or a tie invoke the model.
    """
    if objects.empty:
        return _model_classify(classifier, objects)

    if primary_radius_m <= 0:
        raise ValueError("GEM primary radius must be greater than zero.")

    if fallback_radius_m <= primary_radius_m:
        raise ValueError(
            "GEM fallback radius must be greater than the primary radius."
        )

    if max_radius_m <= fallback_radius_m:
        raise ValueError(
            "GEM maximum radius must be greater than the fallback radius."
        )

    if extended_radius_m <= max_radius_m:
        raise ValueError(
            "GEM extended radius must be greater than the maximum radius."
        )

    if db is None:
        return _model_classify(classifier, objects)

    matches = _find_nearby_gem_categories(
        db,
        objects,
        primary_radius_m,
        fallback_radius_m,
        max_radius_m,
        extended_radius_m
    )
    database_decisions = {}
    model_positions = []

    for row_id in range(len(objects)):
        radius_matches = matches.get(row_id, {})
        match_radius_m = None

        if radius_matches.get(primary_radius_m):
            match_radius_m = primary_radius_m
        elif radius_matches.get(fallback_radius_m):
            match_radius_m = fallback_radius_m
        elif radius_matches.get(max_radius_m):
            match_radius_m = max_radius_m
        elif radius_matches.get(extended_radius_m):
            match_radius_m = extended_radius_m

        category_matches = (
            radius_matches.get(match_radius_m, {})
            if match_radius_m is not None
            else {}
        )
        category_counts = Counter({
            category: metadata["count"]
            for category, metadata in category_matches.items()
        })

        if not category_counts:
            model_positions.append(row_id)
            continue

        highest_count = max(category_counts.values())
        winners = [
            category
            for category, count in category_counts.items()
            if count == highest_count
        ]

        if len(winners) != 1:
            model_positions.append(row_id)
            continue

        winning_category = winners[0]
        winning_match = category_matches[winning_category]
        database_decisions[row_id] = {
            "category": winning_category,
            "winner_count": highest_count,
            "total_count": sum(category_counts.values()),
            "counts": category_counts,
            "match_radius_m": match_radius_m,
            "facility_name": winning_match["facility_name"],
            "exact_type": winning_match["exact_type"]
        }

    output = objects.copy()
    output["predicted_label"] = pd.Series(index=output.index, dtype="object")
    output["predicted_label_confidence"] = pd.Series(
        index=output.index,
        dtype="float"
    )
    output["classification_source"] = pd.Series(
        index=output.index,
        dtype="object"
    )
    output["gem_match_count"] = 0
    output["gem_category_vote_count"] = 0
    output["gem_match_radius_m"] = np.nan
    output["gem_facility_name"] = None
    output["gem_industry_exact_type"] = None

    model_classes = [str(value) for value in classifier.label_encoder.classes_]
    probability_columns = {
        category: f"prob_{category.replace(' ', '_')}"
        for category in model_classes
    }
    for column in probability_columns.values():
        output[column] = 0.0

    for row_id, decision in database_decisions.items():
        index = output.index[row_id]
        total_count = decision["total_count"]
        output.at[index, "predicted_label"] = decision["category"]
        output.at[index, "predicted_label_confidence"] = (
            decision["winner_count"] / total_count
        )
        output.at[index, "classification_source"] = GEM_SOURCE
        output.at[index, "gem_match_count"] = total_count
        output.at[index, "gem_category_vote_count"] = decision["winner_count"]
        output.at[index, "gem_match_radius_m"] = decision["match_radius_m"]
        output.at[index, "gem_facility_name"] = decision["facility_name"]
        output.at[index, "gem_industry_exact_type"] = decision["exact_type"]

        for category, count in decision["counts"].items():
            column = probability_columns.get(category)
            if column is not None:
                output.at[index, column] = count / total_count

    if model_positions:
        model_input = objects.iloc[model_positions].copy()
        model_output = _model_classify(classifier, model_input)

        for column in model_output.columns:
            if column not in output.columns:
                output[column] = np.nan

        output.loc[model_output.index, model_output.columns] = model_output

    primary_count = sum(
        decision["match_radius_m"] == primary_radius_m
        for decision in database_decisions.values()
    )
    fallback_count = sum(
        decision["match_radius_m"] == fallback_radius_m
        for decision in database_decisions.values()
    )
    max_count = sum(
        decision["match_radius_m"] == max_radius_m
        for decision in database_decisions.values()
    )
    extended_count = sum(
        decision["match_radius_m"] == extended_radius_m
        for decision in database_decisions.values()
    )

    logger.info(
        "Industrial classification completed | total=%s | gem=%s | gem_primary=%s | "
        "gem_fallback=%s | gem_max=%s | gem_extended=%s | model=%s | "
        "primary_radius_m=%s | fallback_radius_m=%s | max_radius_m=%s | "
        "extended_radius_m=%s",
        len(objects),
        len(database_decisions),
        primary_count,
        fallback_count,
        max_count,
        extended_count,
        len(model_positions),
        primary_radius_m,
        fallback_radius_m,
        max_radius_m,
        extended_radius_m
    )

    return output
