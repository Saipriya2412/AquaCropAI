
def analyze_water(crop, soil_moisture, rainfall, forecast_rainfall=0, crop_stage=""):

    # Calculate water risk
    if soil_moisture < 20:
        risk = "High"

    elif soil_moisture < 40:
        risk = "Medium"

    else:
        risk = "Low"

    # Crop-specific recommendations
    crop_recommendations = {
        "Paddy": {
            "High": "Check field water availability immediately.",
            "Medium": "Monitor field moisture and irrigation requirements.",
            "Low": "Continue monitoring field water levels."
        },
        "Cotton": {
            "High": "Check root-zone moisture and irrigation availability.",
            "Medium": "Monitor soil moisture and plan irrigation if needed.",
            "Low": "Continue monitoring soil moisture."
        },
        "Maize": {
            "High": "Check root-zone moisture and arrange irrigation if needed.",
            "Medium": "Monitor moisture and rainfall conditions.",
            "Low": "Continue monitoring crop water conditions."
        },
        "Wheat": {
            "High": "Check root-zone moisture and irrigation availability.",
            "Medium": "Monitor soil moisture and crop conditions.",
            "Low": "Continue monitoring soil moisture."
        }
    }

    recommendations = crop_recommendations.get(
        crop,
        {
            "High": "Check soil moisture and irrigation availability.",
            "Medium": "Monitor soil moisture and irrigation needs.",
            "Low": "Continue monitoring soil moisture."
        }
    )

    recommendation = recommendations[risk]

    # Growth-stage recommendations
    stage = crop_stage.lower()

    if "seed" in stage:
        recommendation += " Monitor moisture carefully during seed establishment."

    elif "veget" in stage or "tiller" in stage:
        recommendation += " Monitor crop growth and root-zone moisture."

    elif "flower" in stage:
        recommendation += " Monitor water conditions carefully during flowering."

    elif "harvest" in stage or "matur" in stage:
        recommendation += " Monitor crop maturity and avoid unnecessary irrigation."

    # Rainfall information
    if rainfall >= 20:
        recommendation += " Recent rainfall is significant. Check field conditions."

    if forecast_rainfall >= 10:
        recommendation += " Rain is expected. Check the forecast before irrigation."

    elif forecast_rainfall < 5:
        recommendation += " Little rainfall is forecast. Continue monitoring."

    return {
        "crop": crop,
        "crop_stage": crop_stage,
        "soil_moisture": soil_moisture,
        "rainfall": rainfall,
        "forecast_rainfall": forecast_rainfall,
        "risk": risk,
        "recommendation": recommendation
    }
