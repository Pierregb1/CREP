def temp(lat, lon, year=2024):
    return [273 + (i % 24) for i in range(8760)]
