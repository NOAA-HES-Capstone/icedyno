"""
Since polarstereo-lonlat-convert-py is not available as a pypi or conda package, this
was the simplest method to utilize what IceDyno needed, with some minor modifications for the IMS 1km dataset.

Credit:
This software was developed by the NASA National Snow and Ice Data Center Distributed Active Archive Center.
Author: Chris Torrence, September 2019
https://github.com/nsidc/polarstereo-lonlat-convert-py/tree/main
"""
import numpy as np

# Earth-parameter defualts
TRUE_SCALE_LATITUDE = 60
EARTH_RADIUS_KM = 6378.137
# Derived from proj4 string: a=6378137, b=6356257 in IMS user guide
EARTH_ECCENTRICITY = 0.08275970933894519


def polar_xy_to_lonlat(
    x: float,
    y: float,
    true_scale_lat: float = TRUE_SCALE_LATITUDE,
    re: float = EARTH_RADIUS_KM,
    e: float = EARTH_ECCENTRICITY,
) -> tuple[float, float]:
    """Convert from Polar Stereographic (x, y) coordinates to
    geodetic longitude and latitude.

    Credit: https://github.com/nsidc/polarstereo-lonlat-convert-py/tree/main

    Args:
        x (float): X coordinate(s) in **meters**
        y (float): Y coordinate(s) in **meters**
        true_scale_lat (float): true-scale latitude in degrees
        re (float): Earth radius in km
        e (float): Earth eccentricity

    Returns:
        If x and y are scalars then the result is a
        two-element list containing [longitude, latitude].
        If x and y are numpy arrays then the result will be a two-element
        list where the first element is a numpy array containing
        the longitudes and the second element is a numpy array containing
        the latitudes.
    """
    # Convert x, y back to km for the conversion, since it was derived for km.
    x = x / 1000.0
    y = y / 1000.0

    e2 = e * e
    slat = true_scale_lat * np.pi / 180
    rho = np.sqrt(x**2 + y**2)

    if abs(true_scale_lat - 90.0) < 1e-5:
        t = rho * np.sqrt((1 + e) ** (1 + e) * (1 - e) ** (1 - e)) / (2 * re)
    else:
        cm = np.cos(slat) / np.sqrt(1 - e2 * (np.sin(slat) ** 2))
        t = np.tan((np.pi / 4) - (slat / 2)) / (
            (1 - e * np.sin(slat)) / (1 + e * np.sin(slat))
        ) ** (e / 2)
        t = rho * t / (re * cm)

    chi = (np.pi / 2) - 2 * np.arctan(t)
    lat = (
        chi
        + ((e2 / 2) + (5 * e2**2 / 24) + (e2**3 / 12)) * np.sin(2 * chi)
        + ((7 * e2**2 / 48) + (29 * e2**3 / 240)) * np.sin(4 * chi)
        + (7 * e2**3 / 120) * np.sin(6 * chi)
    )
    lat = lat * 180 / np.pi
    lon = np.arctan2(x, -y)
    lon = lon * 180 / np.pi

    return lon, lat


def polar_lonlat_to_xy(
    longitude: float,
    latitude: float,
    true_scale_lat: float = TRUE_SCALE_LATITUDE,
    re: float = EARTH_RADIUS_KM,
    e: float = EARTH_ECCENTRICITY,
) -> tuple[float, float]:
    """Convert from geodetic longitude and latitude to Polar Stereographic
    (X, Y) coordinates in km.

    Credit: https://github.com/nsidc/polarstereo-lonlat-convert-py/tree/main

    Args:
        longitude (float): longitude or longitude array in degrees
        latitude (float): latitude or latitude array in degrees (positive)
        true_scale_lat (float): true-scale latitude in degrees
        re (float): Earth radius in km
        e (float): Earth eccentricity

    Returns:
        If longitude and latitude are scalars then the result is a
        two-element list containing [X, Y] in meters.
        If longitude and latitude are numpy arrays then the result will be a
        two-element list where the first element is a numpy array containing
        the X coordinates and the second element is a numpy array containing
        the Y coordinates.
    """
    lat = abs(latitude) * np.pi / 180
    lon = longitude * np.pi / 180
    slat = true_scale_lat * np.pi / 180

    e2 = e * e

    # Snyder (1987) p. 161 Eqn 15-9
    t = np.tan(np.pi / 4 - lat / 2) / (
        (1 - e * np.sin(lat)) / (1 + e * np.sin(lat))
    ) ** (e / 2)

    if abs(90 - true_scale_lat) < 1e-5:
        # Snyder (1987) p. 161 Eqn 21-33
        rho = 2 * re * t / np.sqrt((1 + e) ** (1 + e) * (1 - e) ** (1 - e))
    else:
        # Snyder (1987) p. 161 Eqn 21-34
        tc = np.tan(np.pi / 4 - slat / 2) / (
            (1 - e * np.sin(slat)) / (1 + e * np.sin(slat))
        ) ** (e / 2)
        mc = np.cos(slat) / np.sqrt(1 - e2 * (np.sin(slat) ** 2))
        rho = re * mc * t / tc

    x = 1000 * rho * np.sin(lon)
    y = -1000 * rho * np.cos(lon)
    return x, y
