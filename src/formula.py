import math

# calculate Z reference of each RC variation
def calculate_fmid(fstart, fend):
    fmid = (fstart + fend) / 2
    return fmid

def calculate_xc(f, c):
    xc = 1 / (2 * math.pi * f, c)
    return xc

def calculate_z(r, xc):
    akar = math.sqrt(1/r**2 + 1/xc**2)
    z = 1/ akar
    return z