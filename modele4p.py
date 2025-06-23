def temp(lat, lon):
    return [273 + (i % 24) for i in range(8760)]
