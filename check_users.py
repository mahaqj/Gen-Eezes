from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['gen_eezes']

subscribed = list(db['users'].find({'subscribed': True}))
all_users = list(db['users'].find({}))

print(f'\nTotal subscribed users: {len(subscribed)}')
print('='*50)
for u in subscribed:
    print(f"  - {u.get('name', 'Unknown')} ({u.get('email')}) [subscribed: {u.get('subscribed')}]")
print('='*50)

print(f'\nAll users in database: {len(all_users)}')
print('='*50)
for u in all_users:
    print(f"  - {u.get('name', 'Unknown')} ({u.get('email')}) [subscribed: {u.get('subscribed', False)}]")
print('='*50 + '\n')
