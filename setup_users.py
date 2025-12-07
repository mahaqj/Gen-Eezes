"""Quick script to check and update users"""
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['gen_eezes']
users_col = db['users']

print("Current users:")
users = list(users_col.find())
for user in users:
    print(f"  - {user.get('email')}: subscribed={user.get('subscribed', True)}")

# Mark all existing users as subscribed
if users:
    print("\nMarking all users as subscribed...")
    result = users_col.update_many({}, {'$set': {'subscribed': True}})
    print(f"Updated {result.modified_count} users")
else:
    print("\nNo users found in database")

print("\nFinal users list:")
for user in users_col.find():
    print(f"  - {user.get('email')}: subscribed={user.get('subscribed', True)}")
