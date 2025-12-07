from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['gen_eezes']

# Mark all users as subscribed
result = db['users'].update_many({}, {'$set': {'subscribed': True}})

print(f'\n✓ Updated {result.modified_count} user(s)')

# Show current state
users = list(db['users'].find({'subscribed': True}))
print(f'\nTotal subscribed users now: {len(users)}')
print('='*50)
for u in users:
    print(f"  - {u.get('name', 'Unknown')} ({u.get('email')})")
print('='*50 + '\n')
