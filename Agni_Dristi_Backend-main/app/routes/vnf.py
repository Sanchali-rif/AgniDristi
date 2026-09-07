import io
import logging

import pandas as pd

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile
)

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.services.vnf.vnf_incremental_service import (
    process_incremental_vnf_upload
)


router = APIRouter(
    prefix="/vnf",
    tags=["VNF"]
)

logger = logging.getLogger(
    __name__
)


@router.post("/upload")
async def upload_vnf_data(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # ========================================================
    # 1. VALIDATE FILE
    # ========================================================

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided."
        )

    if not file.filename.lower().endswith(
        ".csv"
    ):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported."
        )

    try:
        logger.info(
            "VNF upload started | file=%s",
            file.filename
        )

        # ====================================================
        # 2. READ CSV
        # ====================================================

        contents = await file.read()

        df = pd.read_csv(
            io.BytesIO(contents),
            low_memory=False
        )

        if df.empty:
            raise HTTPException(
                status_code=400,
                detail="Uploaded VNF CSV is empty."
            )

        logger.info(
            "VNF CSV loaded | rows=%s",
            len(df)
        )

        # ====================================================
        # 3. RUN INCREMENTAL VNF WORKFLOW
        # ====================================================

        result = (
            process_incremental_vnf_upload(
                db,
                df,
                rolling_months=12
            )
        )

        # ====================================================
        # 4. RESPONSE
        # ====================================================

        return {
            "filename": file.filename,
            **result
        }

    except HTTPException:
        raise

    except Exception as exc:
        db.rollback()

        logger.exception(
            "VNF upload failed"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"VNF processing failed: "
                f"{str(exc)}"
            )
        )