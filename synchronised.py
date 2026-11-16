def synchronize_observations(new_records, database):

    for record in new_records:

        observation_id = record["observation_id"]

        existing = database.find_one({
            "observation_id": observation_id
        })

        if existing:

            continue

        database.insert_one(record)

        print(
            f"New observation registered: {observation_id}"
        )