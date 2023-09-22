from pymongo import ReturnDocument

from credi.database import connections

def get_next_sequence( collection_ ):
    credibar_client = connections()
    credibar_db = credibar_client.connect()
    record = credibar_db.credibar_counters.find_one_and_update(
        { "collection": collection_ },
        { "$inc": { "sequence": 1 } },
        return_document= ReturnDocument.AFTER
    )
    if not record:
        record = {
            "collection": collection_,
            "sequence": 1
        }
        credibar_db.credibar_counters.insert_one( record )
    credibar_client.disconnect()
    return record["sequence"]