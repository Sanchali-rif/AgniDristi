import pandas as pd

from app.services.vnf.vnf_pipeline_service import (
    process_vnf_data_with_members
)


CSV_PATH = "VNF_INDIA_2026.csv"


def main():
    df = pd.read_csv(
        CSV_PATH,
        low_memory=False
    )

    result = process_vnf_data_with_members(
        df
    )

    print(
        "\nObjects:",
        len(result["objects"])
    )

    print(
        "Persistent member detections:",
        len(result["detections"])
    )

    print(
        "Temporal detections:",
        len(result["temporal_detections"])
    )

    print(
        "\nPersistent columns:"
    )

    print(
        result["detections"]
        .columns
        .tolist()
    )


if __name__ == "__main__":
    main()