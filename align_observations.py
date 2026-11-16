##This creates an image aligned to the reference WCS.
##In production, the variance maps and quality masks must be reprojected consistently as well.

from reproject import reproject_interp
from astropy.wcs import WCS


def align_image(
    image,
    source_header,
    target_header,
    target_shape
):

    source_wcs = WCS(source_header)

    target_wcs = WCS(target_header)

    aligned, footprint = reproject_interp(
        (image, source_wcs),
        target_wcs,
        shape_out=target_shape
    )

    return aligned, footprint