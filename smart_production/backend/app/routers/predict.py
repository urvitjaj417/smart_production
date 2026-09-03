from fastapi import APIRouter
from .. import schemas
from ..ml.predict import predict_risk

router = APIRouter(prefix="/api/predict", tags=["ml"])


@router.post("/", response_model=schemas.PredictionResponse)
def predict(req: schemas.PredictionRequest):
    """Run the trained RandomForest model on live sensor values."""
    result = predict_risk(
        temperature=req.temperature,
        pressure=req.pressure,
        operating_time=req.operating_time,
        output_rate=req.output_rate,
    )
    return schemas.PredictionResponse(**result)
