import requests
import json  # facultatif, utile pour déboguer les réponses


def get_mean_albedo(lat, lon, start="20220101", end="20231231"):
    """
    Renvoie l'albédo moyen sur la période donnée pour un point donné (lat, lon).
    start, end : dates au format 'YYYYMMDD'
    """
    url = f"https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "parameters": "ALLSKY_SFC_SW_DWN,ALLSKY_SFC_SW_UP",
        "community": "AG",
        "longitude": lon,
        "latitude": lat,
        "start": start,
        "end": end,
        "format": "JSON"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        allsky = data['properties']['parameter']['ALLSKY_SFC_SW_DWN']
        upsky = data['properties']['parameter']['ALLSKY_SFC_SW_UP']

        albedo_values = [
            upsky[day] / allsky[day]
            for day in allsky if allsky[day] > 0 and upsky[day] is not None
        ]
        return sum(albedo_values) / len(albedo_values) if albedo_values else None

    except Exception as e:
        print("Erreur lors de la récupération de l'albédo :", e)
        return None
