def voltage_divider(r1, r2, vin):
    vout = (vin * r1)/(r1 + r2)
    return round(vout, 3)
