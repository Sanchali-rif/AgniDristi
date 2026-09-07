import pandas as pd

from sklearn.base import BaseEstimator, TransformerMixin


def parse_date_series(series):
    return pd.to_datetime(
        series,
        format="mixed",
        errors="coerce"
    )


def preprocess_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # -------------------------------------------------
    # MSCAN DATETIME
    # -------------------------------------------------

    if "Date_Mscan" in df.columns:
        dt = pd.to_datetime(
            df["Date_Mscan"],
            format="mixed",
            errors="coerce",
            utc=True
        )

        df["Mscan_date"] = dt.dt.strftime("%Y-%m-%d")
        df["Mscan_time"] = dt.dt.strftime("%H:%M:%S.%f")

    elif "Mscan_date" in df.columns:
        dt = pd.to_datetime(
            df["Mscan_date"],
            format="mixed",
            errors="coerce",
            utc=True
        )

        if "Mscan_time" not in df.columns:
            df["Mscan_time"] = dt.dt.strftime("%H:%M:%S.%f")

        df["Mscan_date"] = dt.dt.strftime("%Y-%m-%d")

    # -------------------------------------------------
    # LTZ DATETIME
    # -------------------------------------------------

    if "Date_LTZ" in df.columns:
        dt = pd.to_datetime(
            df["Date_LTZ"],
            format="mixed",
            errors="coerce",
            utc=True
        )

        df["LTZ_date"] = dt.dt.strftime("%Y-%m-%d")
        df["LTZ_time"] = dt.dt.strftime("%H:%M:%S.%f")

    elif "LTZ_date" in df.columns:
        dt = pd.to_datetime(
            df["LTZ_date"],
            format="mixed",
            errors="coerce",
            utc=True
        )

        if "LTZ_time" not in df.columns:
            df["LTZ_time"] = dt.dt.strftime("%H:%M:%S.%f")

        df["LTZ_date"] = dt.dt.strftime("%Y-%m-%d")

    return df


class CleanSentinelValues(BaseEstimator, TransformerMixin):
    def __init__(
        self,
        temp_col="Temp_primary",
        sentinel=999999,
        lat_col="Lat_GMTCO",
        lon_col="Lon_GMTCO",
        date_col="Mscan_date",
        aoi_bounds=None,
        start_date=None,
        end_date=None
    ):
        self.temp_col = temp_col
        self.sentinel = sentinel
        self.lat_col = lat_col
        self.lon_col = lon_col
        self.date_col = date_col
        self.aoi_bounds = aoi_bounds
        self.start_date = start_date
        self.end_date = end_date

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        df = X.copy()
        before = len(df)

        df[self.temp_col] = pd.to_numeric(df[self.temp_col], errors="coerce")
        df[self.lat_col] = pd.to_numeric(df[self.lat_col], errors="coerce")
        df[self.lon_col] = pd.to_numeric(df[self.lon_col], errors="coerce")

        df = df[df[self.temp_col] != self.sentinel]

        df = df.dropna(
            subset=[
                self.temp_col,
                self.lat_col,
                self.lon_col,
                self.date_col
            ]
        )

        dt = parse_date_series(df[self.date_col])

        df = df.loc[dt.notna()].copy()
        df["_parsed_datetime"] = dt.loc[df.index]

        if self.aoi_bounds is not None:
            south, north, west, east = self.aoi_bounds

            df = df[
                df[self.lat_col].between(south, north)
                & df[self.lon_col].between(west, east)
            ].copy()

        if self.start_date is not None:
            df = df[
                df["_parsed_datetime"]
                >= pd.Timestamp(self.start_date)
            ].copy()

        if self.end_date is not None:
            df = df[
                df["_parsed_datetime"]
                <= pd.Timestamp(self.end_date)
            ].copy()

        df = (
            df
            .drop(columns=["_parsed_datetime"])
            .reset_index(drop=True)
        )

        print(
            f"[Clean] {before:,} -> "
            f"{len(df):,} valid detections"
        )

        return df