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

def calculate_percentage(ref, value):
    percentage = value / ref * 100
    return percentage

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


# related to body composition equation
# to calculate fat-free mass
def calculate_ffm_eq1(w, h, z, y, s):
    # Predicting body composition using foot-to-foot bioelectrical impedance analysis in healthy Asian individuals
    # https://www.researchgate.net/publication/277088052_Predicting_body_composition_using_foot-to-foot_bioelectrical_impedance_analysis_in_healthy_Asian_individuals#:~:text=13.055%20%2B%200.204%20w,y%20%2B%208.125%20S
    # w : weight (kg)
    # h : heigth (cm)
    # z : impedance (ohm)
    # y : age (years)
    # s : gender (male=1, female=0)
    ffm_kg = 13.055 + 0.204*w + 0.394*(h*h)/z - 0.136*y + 8.125*s
    return ffm_kg

# to calculate fat mass
def calculate_fm(w, ffm):
    fm_kg = w - ffm
    return fm_kg

# calculate total body water
def calculate_tbw(ffm, percentage=0.73):
    # NIHR | Cambridge Biomedical Research Centre
    # https://dapa-toolkit.mrc.ac.uk/anthropometry/objective-methods/bioelectric-impedence-analysis#:~:text=FFM)%2C%20assuming%20that-,73,-%25%20of%20the%20body%E2%80%99s
    tbw_kg = ffm * percentage
    return tbw_kg

# calculate body composition
def calculate_bc_kg(w, h, z, y, s):
    # using model 3-components (3C): fm, ffm, tbw
    ffm_kg = calculate_ffm_eq1(w, h, z, y, s)
    fm_kg = calculate_fm(w, ffm_kg)
    tbw_kg = calculate_tbw(ffm_kg)

    return ffm_kg, fm_kg, tbw_kg

# calculate BC percentage
def calculate_bc_percentage(w, ffm, fm, tbw):
    # using model 3-components (3C): fm, ffm, tbw
    ffm_percentage = calculate_percentage(w, ffm)
    fm_percentage = calculate_percentage(w, fm)
    tbw_percentage = calculate_percentage(w, tbw)

    return ffm_percentage, fm_percentage, tbw_percentage


# (END) SPECIAL FUNTION ==============================



# TESTING
if __name__ == "__main__":
    w = 57
    h = 168
    z = 800
    y = 21
    s = 1
    ffm_kg, fm_kg, tbw_kg = calculate_bc_kg(w, h, z, y, s)
    ffm_percentage, fm_percentage, tbw_percentage = calculate_bc_percentage(w, ffm_kg, fm_kg, tbw_kg)

    print( "ffm\t: {:.2f} kg / {:.2f} %".format(ffm_kg, ffm_percentage) )
    print( "fm\t: {:.2f} kg / {:.2f} %".format(fm_kg, fm_percentage) )
    print( "tbw\t: {:.2f} kg / {:.2f} %".format(tbw_kg, tbw_percentage) )