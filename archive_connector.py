#Implementation note: This is a starting connector.
#Before deployment, verify the PyVO version and the archive's accepted SIA2 parameter syntax. Add pagination, retries, timeouts, and asynchronous job handling where required.

import pyvo
import pandas as pd

SIA_URL = "https://irsa.ipac.caltech.edu/SIA"


def query_spherex(ra, dec, radius=0.01):

    collections = [
        "spherex_dr1",
        "spherex_qr3"
    ]

    all_results = []

    service = pyvo.dal.SIA2Service(SIA_URL)

    for collection in collections:

        try:

            results = service.search(
                pos=(ra, dec, radius),
                COLLECTION=collection
            )

            table = results.to_table()

            if len(table) > 0:

                df = table.to_pandas()

                df["data_release"] = collection

                all_results.append(df)

        except Exception as error:

            print(
                f"Error querying {collection}: {error}"
            )

    if not all_results:

        return pd.DataFrame()

    observations = pd.concat(
        all_results,
        ignore_index=True
    )

    return observations