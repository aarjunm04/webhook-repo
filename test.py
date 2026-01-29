from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['github_webhook_db']
collection = db['events']

# Insert test PUSH event
test_event = {
    'request_id': 'test_push_123',
    'author': 'TestUser',
    'action': 'PUSH',
    'from_branch': None,
    'to_branch': 'main',
    'timestamp': datetime.utcnow().isoformat() + 'Z'
}

collection.insert_one(test_event)
print("✅ Test event inserted!")

# Insert test PULL_REQUEST event
test_pr = {
    'request_id': 'test_pr_456',
    'author': 'TestUser',
    'action': 'PULL_REQUEST',
    'from_branch': 'feature',
    'to_branch': 'main',
    'timestamp': datetime.utcnow().isoformat() + 'Z'
}

collection.insert_one(test_pr)
print("✅ Test PR event inserted!")

exit()
