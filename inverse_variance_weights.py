##This function:
##1. Accepts multiple aligned images.
##2. Accepts their corresponding variance maps.
##3. Excludes invalid pixels.
##4. Calculates inverse-variance weights.
##5. Combines pixel values.
##6. Calculates the resulting uncertainty.

import numpy as np


def weighted_coadd(images, variances, masks=None):

    images = np.asarray(images, dtype=float)

    variances = np.asarray(variances, dtype=float)

    valid = (
        np.isfinite(images) &
        np.isfinite(variances) &
        (variances > 0)
    )

    if masks is not None:

        valid &= np.asarray(masks, dtype=bool)

    weights = np.zeros_like(variances)

    np.divide(
        1.0,
        variances,
        out=weights,
        where=valid
    )

    weighted_sum = np.sum(
        weights * np.where(valid, images, 0),
        axis=0
    )

    total_weight = np.sum(weights, axis=0)

    combined_image = np.full(
        total_weight.shape,
        np.nan
    )

    combined_variance = np.full(
        total_weight.shape,
        np.nan
    )

    valid_pixels = total_weight > 0

    combined_image[valid_pixels] = (
        weighted_sum[valid_pixels] /
        total_weight[valid_pixels]
    )

    combined_variance[valid_pixels] = (
        1.0 / total_weight[valid_pixels]
    )

    return combined_image, combined_variance