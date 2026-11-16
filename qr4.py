## These are illustrative records, not actual archive results.
## Important consideration
##Do not assume that every observation is available at six-month intervals.

##SPHEREx data is ingested into IRSA on a weekly basis, and SIA2 availability may lag the latest archive ingestion by approximately one day. IRSA

##Our application must dynamically retrieve whatever observations are available.

import yaml


def load_releases():

    with open("releases.yaml", "r") as file:

        config = yaml.safe_load(file)

    active_collections = []

    for release, settings in config["releases"].items():

        if settings["enabled"]:

            active_collections.extend(
                settings["collections"]
            )

    return active_collections