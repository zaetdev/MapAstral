import math
from dataclasses import dataclass
from typing import Dict, Tuple

DEG = math.pi / 180.0

SIGNS = [
    "Áries",
    "Touro",
    "Gêmeos",
    "Câncer",
    "Leão",
    "Virgem",
    "Libra",
    "Escorpião",
    "Sagitário",
    "Capricórnio",
    "Aquário",
    "Peixes",
]

@dataclass
class PlanetElements:
    a: float  # Semi-major axis (AU)
    e: float  # Eccentricity
    i: float  # Inclination (deg)
    L: float  # Mean longitude (deg)
    long_peri: float  # Longitude of perihelion (deg)
    long_node: float  # Longitude of ascending node (deg)
    n: float  # Mean daily motion (deg/day)

PLANETARY_ELEMENTS: Dict[str, PlanetElements] = {
    "mercury": PlanetElements(0.38709893, 0.20563069, 7.00487, 252.25084, 77.45645, 48.33167, 4.09233445),
    "venus": PlanetElements(0.72333199, 0.00677323, 3.39471, 181.97973, 131.602467, 76.68069, 1.60213034),
    "earth": PlanetElements(1.00000011, 0.01671022, 0.00005, 100.46435, 102.94719, 0.0, 0.9856076686),
    "mars": PlanetElements(1.52366231, 0.09341233, 1.85061, 355.45332, 336.04084, 49.57854, 0.524033),
    "jupiter": PlanetElements(5.20336301, 0.04839266, 1.30530, 34.40438, 14.331309, 100.55615, 0.083086),
    "saturn": PlanetElements(9.53707032, 0.05415060, 2.48446, 50.077471, 92.861360, 113.71504, 0.033466),
    "uranus": PlanetElements(19.19126393, 0.04716771, 0.76986, 314.055005, 170.96424, 74.005947, 0.011734),
    "neptune": PlanetElements(30.06896348, 0.00858587, 1.76917, 304.348665, 44.97135, 131.784057, 0.005981),
    "pluto": PlanetElements(39.48211675, 0.24880766, 17.14175, 238.929038, 224.068916, 110.303936, 0.00396),
}


def julian_day(year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: int = 0) -> float:
    if month <= 2:
        year -= 1
        month += 12
    A = year // 100
    B = 2 - A + A // 4
    jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + B - 1524.5
    frac = (hour + minute / 60 + second / 3600) / 24
    return jd + frac


def solve_kepler(M_deg: float, e: float) -> float:
    M = math.radians(M_deg)
    E = M if e < 0.8 else math.pi
    delta = 1
    while abs(delta) > 1e-6:
        delta = (E - e * math.sin(E) - M) / (1 - e * math.cos(E))
        E -= delta
    return E


def heliocentric_coords(elements: PlanetElements, d: float) -> Tuple[float, float, float]:
    L = elements.L + elements.n * d
    M = L - elements.long_peri
    E = solve_kepler(M % 360, elements.e)
    v = 2 * math.atan2(math.sqrt(1 + elements.e) * math.sin(E / 2), math.sqrt(1 - elements.e) * math.cos(E / 2))
    r = elements.a * (1 - elements.e * math.cos(E))
    x_orb = r * math.cos(v)
    y_orb = r * math.sin(v)
    # Rotate to ecliptic coordinates
    omega = math.radians(elements.long_peri - elements.long_node)
    i = elements.i * DEG
    node = elements.long_node * DEG
    x = (
        (math.cos(node) * math.cos(omega) - math.sin(node) * math.sin(omega) * math.cos(i)) * x_orb
        + (-math.cos(node) * math.sin(omega) - math.sin(node) * math.cos(omega) * math.cos(i)) * y_orb
    )
    y = (
        (math.sin(node) * math.cos(omega) + math.cos(node) * math.sin(omega) * math.cos(i)) * x_orb
        + (-math.sin(node) * math.sin(omega) + math.cos(node) * math.cos(omega) * math.cos(i)) * y_orb
    )
    z = (math.sin(omega) * math.sin(i) * x_orb + math.cos(omega) * math.sin(i) * y_orb)
    return x, y, z


def geocentric_longitude(planet: str, jd: float) -> float:
    d = jd - 2451545.0
    if planet == "sun":
        xe, ye, ze = heliocentric_coords(PLANETARY_ELEMENTS["earth"], d)
        lon = (math.degrees(math.atan2(ye, xe)) + 180) % 360
        return lon
    if planet == "moon":
        return moon_longitude(d)
    x, y, z = heliocentric_coords(PLANETARY_ELEMENTS[planet], d)
    xe, ye, ze = heliocentric_coords(PLANETARY_ELEMENTS["earth"], d)
    xg = x - xe
    yg = y - ye
    zg = z - ze
    lon = math.degrees(math.atan2(yg, xg)) % 360
    return lon


def moon_longitude(d: float) -> float:
    L = 218.3164591 + 13.17639648 * d
    D = 297.8502042 + 12.19074912 * d
    M = 357.5291092 + 0.98560028 * d
    M_prime = 134.9634114 + 13.06499295 * d
    F = 93.2720993 + 13.22935024 * d
    lon = (
        L
        + 6.289 * math.sin(DEG * M_prime)
        + 1.274 * math.sin(DEG * (2 * D - M_prime))
        + 0.658 * math.sin(DEG * (2 * D))
        + 0.214 * math.sin(DEG * (2 * M_prime))
        + 0.186 * math.sin(DEG * M)
        - 0.059 * math.sin(DEG * (2 * D - 2 * M_prime))
        - 0.057 * math.sin(DEG * (2 * D - M - M_prime))
        + 0.053 * math.sin(DEG * (2 * D + M_prime))
        + 0.046 * math.sin(DEG * (2 * D - M))
        + 0.041 * math.sin(DEG * (M - M_prime))
    )
    return lon % 360


def sign_from_longitude(lon: float) -> str:
    idx = int(lon // 30) % 12
    return SIGNS[idx]


def sidereal_time(jd: float, lon_deg: float) -> float:
    T = (jd - 2451545.0) / 36525
    theta = 280.46061837 + 360.98564736629 * (jd - 2451545) + 0.000387933 * T ** 2 - T ** 3 / 38710000
    return (theta + lon_deg) % 360


def ascendant(jd: float, lat_deg: float, lon_deg: float) -> float:
    eps = 23.439291 * DEG
    lst = sidereal_time(jd, lon_deg) * DEG
    phi = lat_deg * DEG
    asc = math.atan2(math.sin(lst), math.cos(lst) * math.cos(eps) - math.tan(phi) * math.sin(eps))
    return (math.degrees(asc) + 360) % 360


def midheaven(jd: float, lat_deg: float, lon_deg: float) -> float:
    eps = 23.439291 * DEG
    lst = sidereal_time(jd, lon_deg) * DEG
    mc = math.atan2(math.sin(lst) * math.cos(eps), math.cos(lst))
    return (math.degrees(mc) + 360) % 360


def compute_chart(year: int, month: int, day: int, hour: int, minute: int, second: int, lat: float, lon: float) -> Dict[str, Tuple[float, str]]:
    jd = julian_day(year, month, day, hour, minute, second)
    bodies = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]
    result = {}
    for b in bodies:
        lon_b = geocentric_longitude(b, jd)
        result[b] = (lon_b, sign_from_longitude(lon_b))
    asc = ascendant(jd, lat, lon)
    result["ascendant"] = (asc, sign_from_longitude(asc))
    mc = midheaven(jd, lat, lon)
    result["midheaven"] = (mc, sign_from_longitude(mc))
    return result
