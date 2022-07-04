import math

# calculate Z reference of each RC variation
def calculate_fmid(fstart, fend):
    fmid = (fstart + fend) / 2
    return fmid

def calculate_xc(f, c):
    if c == 0:
        xc = math.inf
    else:
        xc = 1 / (2 * math.pi * f * c)
    return xc

def calculate_z(r, xc):
    akar = math.sqrt(1/r**2 + 1/xc**2)
    z = 1/ akar
    return z

def calculate_phase(f, r, c):
    param = 2 * math.pi * f * r * c
    phase = -math.atan(param) * 180/math.pi     # convert to degree
    return phase

def calculate_error(ref, value):
    err = abs(value - ref) / abs(ref) * 100.00
    return err