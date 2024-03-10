from pyproj import Proj


def latlon_to_xy(lat: float, lon: float) -> tuple[float, float]:
    """
    Convert latitude, longitude pair into x, y in NOAA/NSIDC projection for IMS polar stereographic.
    Lat/lon has to be in degrees, not radians.

    TODO: Check that MASIE has the same projection definition
    """
    proj = Proj(
        "+proj=stere +lat_0=90 +lat_ts=60 +lon_0=-80 +k=1 +x_0=0 +y_0=0 +a=6378137 +b=6356257 +units=m +no_defs"
    )
    return proj(lon, lat)


def xy_to_latlon(x: float, y: float) -> tuple[float, float]:
    """
    Convert x, y in NOAA/NSIDC projection for IMS polar stereographic to lat/lon pair.
    Lat/lon is in degrees, not radians.

    TODO: Check that MASIE has the same projection definition
    """
    proj = Proj(
        "+proj=stere +lat_0=90 +lat_ts=60 +lon_0=-80 +k=1 +x_0=0 +y_0=0 +a=6378137 +b=6356257 +units=m +no_defs"
    )
    return proj(x, y, inverse=True)
