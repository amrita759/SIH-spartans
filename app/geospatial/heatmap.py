from typing import List, Dict, Any


def generate_geojson_heatmap(predictions_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    features = []
    for pred in predictions_data:
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [pred["longitude"], pred["latitude"]]
            },
            "properties": {
                "risk_score": pred["risk_score"],
                "risk_level": pred["risk_level"],
                "confidence": pred.get("confidence", 0.0),
                "predicted_time": str(pred.get("predicted_time", ""))
            }
        }
        features.append(feature)

    return {
        "type": "FeatureCollection",
        "features": features
    }