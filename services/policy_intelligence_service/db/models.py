# MongoDB collections are schema-less; define example document structures

POLICY_COLLECTION = "policies"
# Example document: {"_id": ObjectId, "user_id": ObjectId, "policy_id": str, "insurer": str, ...}

USERS_COLLECTION = "users"  # In user_db database
# Example document: {"_id": ObjectId, "name": str, "email": str, ...}
