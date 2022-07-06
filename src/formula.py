import math


# GENERAL FUNCTION ===================================
def calculate_error(ref, value):
    if abs(ref) == 0: 
        err = math.inf
    else:
        err = abs(value - ref) / abs(ref) * 100.00
    return err

def calculate_avg(arr=[]):
    sum = 0
    for n in arr:
        sum += n
    avg = sum / len(arr)
    return avg

# (END) GENERAL FUNCTION =============================


# SPECIAL FUNTION ====================================
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

def calculate_r(z, phase):
    phase *= math.pi / 180      # convert to radian
    param = 1 + math.tan(phase)**2
    r = z * math.sqrt(param)
    return r

def calculate_c(z, phase, f):
    phase *= math.pi / 180      # convert to radian
    if abs(phase) == 0:
        param = math.inf
    else:
        param = 1 + 1/math.tan(phase)**2
    c = 1 / ( 2 * math.pi * f * z * math.sqrt(param) )
    return c

# (END) SPECIAL FUNTION ==============================