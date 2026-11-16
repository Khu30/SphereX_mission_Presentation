import requests


def download_fits(url, output_path):

    response = requests.get(
        url,
        timeout=120
    )

    response.raise_for_status()

    with open(output_path, "wb") as file:

        file.write(response.content)

    return output_path