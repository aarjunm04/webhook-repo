"""
GitHub Webhook Monitor
======================
A Flask application that receives GitHub webhook events (Push, Pull Request, Merge),
stores them in MongoDB, and displays them in a real-time polling UI.

Author: [Your Name]
Created for: Techstax Developer Assessment
Date: January 29, 2026
"""

from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# MongoDB connection
MONGODB_URI = os.getenv('MONGODB_URI')
DB_NAME = os.getenv('DB_NAME', 'github_webhook_db')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'events')

try:
    client = MongoClient(MONGODB_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    print(f"✅ Connected to MongoDB: {DB_NAME}.{COLLECTION_NAME}")
except Exception as e:
    print(f"❌ MongoDB connection error: {e}")

# Home route - serves the UI
@app.route('/')
def index():
    return render_template('index.html')

# Webhook endpoint - receives GitHub events
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Get the event type from GitHub headers
        event_type = request.headers.get('X-GitHub-Event')
        payload = request.json
        
        print(f"📥 Received event: {event_type}")
        
        # Process different event types
        if event_type == 'push':
            handle_push_event(payload)
        elif event_type == 'pull_request':
            handle_pull_request_event(payload)
        else:
            print(f"⚠️ Unhandled event type: {event_type}")
        
        return jsonify({'status': 'success'}), 200
    
    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Handle PUSH events
def handle_push_event(payload):
    """
    Extract data from push event and store to MongoDB
    """
    try:
        # Extract required fields
        request_id = payload['head_commit']['id']  # Commit hash
        author = payload['pusher']['name']
        to_branch = payload['ref'].split('/')[-1]  # Extract branch name from refs/heads/main
        timestamp = payload['head_commit']['timestamp']
        
        # Create event document
        event_doc = {
            'request_id': request_id,
            'author': author,
            'action': 'PUSH',
            'from_branch': None,  # Not applicable for push
            'to_branch': to_branch,
            'timestamp': timestamp
        }
        
        # Check if event already exists (prevent duplicates)
        if collection.find_one({'request_id': request_id}):
            print(f"⚠️ Event {request_id} already exists, skipping...")
            return
        
        # Insert into MongoDB
        collection.insert_one(event_doc)
        print(f"✅ PUSH event stored: {author} -> {to_branch}")
    
    except Exception as e:
        print(f"❌ Error handling push event: {e}")

# Handle PULL_REQUEST events
def handle_pull_request_event(payload):
    """
    Extract data from pull request event and store to MongoDB
    Handles both PR creation and PR merge
    """
    try:
        action = payload['action']  # opened, closed, etc.
        pull_request = payload['pull_request']
        
        request_id = str(pull_request['id'])  # PR ID
        author = pull_request['user']['login']
        from_branch = pull_request['head']['ref']
        to_branch = pull_request['base']['ref']
        timestamp = pull_request['created_at'] if action == 'opened' else pull_request.get('merged_at', pull_request['updated_at'])
        
        # Determine if it's a merge or just a pull request
        if action == 'closed' and pull_request.get('merged', False):
            # This is a MERGE event (brownie points!)
            event_type = 'MERGE'
            request_id = f"merge_{request_id}"  # Unique ID for merge
        elif action == 'opened':
            # This is a PULL_REQUEST event
            event_type = 'PULL_REQUEST'
            request_id = f"pr_{request_id}"  # Unique ID for PR
        else:
            # Other PR actions we don't care about
            print(f"⚠️ PR action '{action}' ignored")
            return
        
        # Create event document
        event_doc = {
            'request_id': request_id,
            'author': author,
            'action': event_type,
            'from_branch': from_branch,
            'to_branch': to_branch,
            'timestamp': timestamp
        }
        
        # Check if event already exists
        if collection.find_one({'request_id': request_id}):
            print(f"⚠️ Event {request_id} already exists, skipping...")
            return
        
        # Insert into MongoDB
        collection.insert_one(event_doc)
        print(f"✅ {event_type} event stored: {author} -> {from_branch} to {to_branch}")
    
    except Exception as e:
        print(f"❌ Error handling pull request event: {e}")

# API endpoint - returns events for UI polling
@app.route('/events', methods=['GET'])
def get_events():
    """
    Returns all events from MongoDB sorted by timestamp (newest first)
    """
    try:
        # Get all events sorted by timestamp descending
        events = list(collection.find({}, {'_id': 0}).sort('timestamp', -1))
        
        # Format timestamps for display
        for event in events:
            event['formatted_timestamp'] = format_timestamp(event['timestamp'])
        
        return jsonify(events), 200
    
    except Exception as e:
        print(f"❌ Error fetching events: {e}")
        return jsonify({'error': str(e)}), 500

def format_timestamp(timestamp_str):
    """
    Convert ISO timestamp to human-readable format
    Example: "1st April 2021 - 9:30 PM UTC"
    """
    try:
        # Parse ISO timestamp
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        
        # Format day with ordinal suffix (1st, 2nd, 3rd, 4th, etc.)
        day = dt.day
        if 10 <= day % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
        
        # Format the full timestamp
        formatted = dt.strftime(f"%d{suffix} %B %Y - %I:%M %p UTC")
        formatted = formatted.replace(f"{day}{suffix}", f"{day}{suffix}")
        
        return formatted
    
    except Exception as e:
        print(f"❌ Error formatting timestamp: {e}")
        return timestamp_str

# Run the Flask app
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
