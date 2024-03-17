import numpy as np

from icedyno.preprocess import geolocation


def test_xy_to_latlon_inversion():
    """Test that xy to latlon and latlon to xy invert each other"""
    lats = [77.508333, 80, 67, 55]
    lons = [-164.754167, -80, 90, 155]

    for i in range(len(lats)):
        lat = lats[i]
        lon = lons[i]
        xy_converted_coordinates = geolocation.polar_lonlat_to_xy(
            longitude=lon, latitude=lat
        )

        reverted_lat_lon = geolocation.polar_xy_to_lonlat(*xy_converted_coordinates)
        assert np.allclose((lon, lat), reverted_lat_lon)
