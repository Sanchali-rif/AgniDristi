import pickle
from pathlib import Path

import numpy as np
import pandas as pd


class SavedIndustrialClassifier:
    def __init__(self, model_file):
        model_path = Path(model_file)

        if not model_path.exists():
            raise FileNotFoundError(
                f"Model file not found: {model_file}"
            )

        with open(model_path, "rb") as f:
            package = pickle.load(f)

        if not isinstance(package, dict):
            raise ValueError(
                "Expected model pickle to contain a model package dictionary."
            )

        required_keys = [
            "model",
            "features",
            "label_encoder"
        ]

        missing_keys = [
            key
            for key in required_keys
            if key not in package
        ]

        if missing_keys:
            raise ValueError(
                f"Model package missing keys: {missing_keys}"
            )

        self.package = package
        self.model = package["model"]
        self.features = list(package["features"])
        self.label_encoder = package["label_encoder"]

    def _prepare_features(self, df):
        missing = [
            feature
            for feature in self.features
            if feature not in df.columns
        ]

        if missing:
            raise ValueError(
                "Missing model features:\n"
                + "\n".join(missing)
            )

        x = df[
            self.features
        ].copy()

        x = x.apply(
            pd.to_numeric,
            errors="coerce"
        )

        x = x.replace(
            [np.inf, -np.inf],
            np.nan
        )

        return x

    def predict(self, df):
        if df.empty:
            out = df.copy()

            out["predicted_label"] = pd.Series(
                dtype="object"
            )

            out["predicted_label_confidence"] = pd.Series(
                dtype="float"
            )

            return out

        x = self._prepare_features(df)

        pred_encoded = np.asarray(
            self.model.predict(x)
        ).astype(int)

        pred_labels = (
            self.label_encoder
            .inverse_transform(pred_encoded)
        )

        probabilities = (
            self.model
            .predict_proba(x)
        )

        confidence = probabilities.max(
            axis=1
        )

        out = df.copy()

        out["predicted_label"] = pred_labels

        out[
            "predicted_label_confidence"
        ] = confidence

        for class_id, class_name in enumerate(
            self.label_encoder.classes_
        ):
            safe_name = str(
                class_name
            ).replace(" ", "_")

            out[
                f"prob_{safe_name}"
            ] = probabilities[:, class_id]

        return out