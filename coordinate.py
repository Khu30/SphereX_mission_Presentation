from astropy.coordinates import SkyCoord
import astropy.units as u


def validate_coordinates(ra, dec, unit="deg"):

    try:

        if unit == "hourangle":

            coordinate = SkyCoord(
                ra=ra,
                dec=dec,
                unit=(u.hourangle, u.deg),
                frame="icrs"
            )

        else:

            coordinate = SkyCoord(
                ra=float(ra),
                dec=float(dec),
                unit=(u.deg, u.deg),
                frame="icrs"
            )

        return {
            "valid": True,
            "ra": coordinate.ra.deg,
            "dec": coordinate.dec.deg
        }

    except Exception as error:

        return {
            "valid": False,
            "error": str(error)
        }