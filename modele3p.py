def temp(lat, lon):
    return [273 + 0.1*lat - 0.05*lon for _ in range(8760)]
