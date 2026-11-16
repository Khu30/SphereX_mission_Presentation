from astropy.io import fits


def extract_fits_data(file_path):

    with fits.open(file_path) as hdul:

        image = hdul["IMAGE"].data.copy()

        variance = hdul["VARIANCE"].data.copy()

        header = hdul["IMAGE"].header.copy()

    return image, variance, header