from bson import ObjectId

def serialize_doc(doc):
    if not doc:
        return None
    doc["_id"] = str(doc["_id"]) if "_id" in doc else None   # convert ObjectId to string
    return doc
