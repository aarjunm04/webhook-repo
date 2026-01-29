## GitHub Webhook Monitor 🚀

A lightweight **GitHub webhook monitoring dashboard** built with **Flask**, **MongoDB Atlas**, and a **modern, minimal frontend**.  
It receives GitHub webhook events, stores them safely with **duplicate prevention**, and displays them in a live-updating UI for easy inspection and debugging.

---

## ✨ Features

- **Webhook Ingestion**: Receives GitHub webhook events via `POST /webhook`
- **Supported Events**:
  - Push events
  - Pull Request events
  - Merge (PR merged) events
- **MongoDB Atlas Storage**:
  - Persists events in a collection with a `request_id` field to prevent duplicates
- **Live Event Dashboard**:
  - Frontend polls the `/events` API every **15 seconds** to fetch and render new events
  - Beautiful gradient-based UI layout using pure HTML/CSS/JS
- **Readable Event Format**:
  - Events displayed as:  
    **`author action from_branch->to_branch on timestamp`**
- **Environment-Based Configuration** via `.env`
- **ngrok Integration** for local development and GitHub webhook delivery

---

## 🧱 Architecture Overview

The project follows a simple but clear separation of concerns between backend, database, and frontend.

```text
                GitHub
                  |
                  |  (Webhook: Push / PR / Merge)
                  v
         +-------------------+
         |  /webhook (Flask) |
         +-------------------+
                  |
                  |  Normalize & upsert by request_id
                  v
         +---------------------+
         |  MongoDB Atlas      |
         |  events collection  |
         +---------------------+
                  ^
                  |  GET /events (poll every 15s)
                  |
         +-----------------------------+
         |  Frontend (index.html)      |
         |  HTML5 + CSS3 + JavaScript  |
         +-----------------------------+
```

---

## 🧰 Tech Stack

- **Backend**: Python 3, Flask
- **Database**: MongoDB Atlas
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Deployment / Tunneling**: ngrok (for local development)
- **Config / Utilities**: `python-dotenv`, `flask-cors`, `pymongo`, `dnspython`

---

## 📁 Project Structure

```text
.
├── app.py                # Main Flask app, webhook handler, MongoDB integration, API endpoints
├── requirements.txt      # Python dependencies
├── test.py               # Optional test script / manual testing helpers
├── templates/
│   └── index.html        # Frontend UI (gradient design, auto-polling)
├── static/               # (Optional) Static assets (CSS, JS, images) if used
└── .env                  # Environment variables (not committed to Git)
```

---

## ⚙️ Environment Variables (`.env`)

Create a `.env` file in the project root with:

```bash
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>/<db>?retryWrites=true&w=majority
DB_NAME=github_webhooks_db
COLLECTION_NAME=events
PORT=5001
```

- **`MONGODB_URI`**: Your MongoDB Atlas connection string.
- **`DB_NAME`**: Database name for this project.
- **`COLLECTION_NAME`**: Collection where webhook events are stored.
- **`PORT`**: Port that Flask will listen on (matches your `app.py`).

---

## 🛠️ Setup Instructions

1. **Clone the repository**

   ```bash
   git clone https://github.com/<your-username>/webhook-repo.git
   cd webhook-repo
   ```

2. **Create and activate a virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS / Linux
   # On Windows:
   # venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   - Create a `.env` file in the project root.
   - Add `MONGODB_URI`, `DB_NAME`, `COLLECTION_NAME`, and `PORT` as described above.

5. **Run the Flask application**

   ```bash
   python app.py
   ```

   The app should start on `http://127.0.0.1:5001` (or the port defined in `PORT`).

6. **Expose the app to the internet with ngrok**

   In a separate terminal:

   ```bash
   ngrok http 5001
   ```

   Copy the **HTTPS** URL from ngrok, e.g. `https://abcd-1234.ngrok.io`.

7. **Configure the GitHub Webhook**

   - Go to your GitHub repository → **Settings** → **Webhooks** → **Add webhook**
   - **Payload URL**:  
     `https://<your-ngrok-subdomain>.ngrok.io/webhook`
   - **Content type**: `application/json`
   - **Secret**: (optional; if you add one, also configure verification in `app.py`)
   - **Events**: Select:
     - “Just the push event” and/or
     - “Pull requests”
   - Save the webhook and trigger a push or PR event.

---

## 🌐 API Endpoints

- **`POST /webhook`**
  - **Description**: Receives GitHub webhook events (Push, Pull Request, Merge).
  - **Body**: Raw GitHub webhook JSON payload.
  - **Behavior**:
    - Extracts:
      - `request_id` (commit hash or PR ID)
      - `author` (GitHub username)
      - `action` (`PUSH`, `PULL_REQUEST`, or `MERGE`)
      - `from_branch`
      - `to_branch`
      - `timestamp` (ISO 8601 UTC)
    - Inserts into MongoDB **only if** `request_id` is not already present.

- **`GET /events`**
  - **Description**: Returns a list of stored webhook events.
  - **Used by**: Frontend UI, which polls this endpoint every **15 seconds**.
  - **Response**: JSON array of event objects (see MongoDB schema below).

- **`GET /`**
  - **Description**: Serves the main HTML dashboard (`index.html`).

> Note: Exact field names and response formats are defined in `app.py`.

---

## 🗄️ MongoDB Schema

Each webhook event is stored as a document with the following structure:

```json
{
  "request_id": "string",        // Commit hash or PR ID (used for duplicate prevention)
  "author": "string",            // GitHub username
  "action": "PUSH|PULL_REQUEST|MERGE",
  "from_branch": "string",       // Source branch
  "to_branch": "string",         // Target branch
  "timestamp": "string"          // ISO 8601 UTC datetime
}
```

- `request_id` is typically:
  - For Push: commit SHA
  - For Pull Request / Merge: PR ID or similar identifier
- An index or uniqueness check on `request_id` is used to prevent duplicates.

---

## 🖥️ Event Display Format (UI)

Events are rendered in a human-friendly format:

```text
author action from_branch->to_branch on timestamp
```

**Examples:**

- `alice PUSH feature/login->main on 2026-01-29T10:15:32Z`
- `bob PULL_REQUEST bugfix/header->develop on 2026-01-29T11:02:47Z`
- `carol MERGE feature/payments->main on 2026-01-29T12:45:10Z`

The frontend:

- Polls `/events` every **15 seconds**
- Updates the event list without reloading the page
- Uses a **gradient background** and clean typography for a visually appealing dashboard

---

## ✅ Testing Instructions

You can test the system end-to-end in several ways:

- **Using GitHub UI**
  - Make a commit and push to the configured repository.
  - Open / update a pull request.
  - Merge a pull request.
  - Watch the dashboard update as events arrive.

- **Using GitHub’s “Redeliver” and “Test delivery”**
  - In the repo’s **Settings → Webhooks → Your webhook**, use:
    - **“Redeliver”** to resend an existing payload.
    - **“Add webhook” → “Let me select individual events” → “Just the push event” → “Add webhook”** then **“Redeliver”** as needed.

- **Using `curl` (manual payloads)**

  ```bash
  curl -X POST "https://<your-ngrok-subdomain>.ngrok.io/webhook" \
    -H "Content-Type: application/json" \
    -d '{
      "fake": "payload-for-testing"
    }'
  ```

  Adapt the payload structure to mimic real GitHub webhook payloads depending on your parsing logic in `app.py`.

---

## 🧪 Local Development Tips

- Ensure your virtual environment is activated before running any Python commands.
- If you change environment variables, **restart** the Flask server.
- Use `print` or logging statements inside `app.py` to debug webhook payloads and storage logic.

---

## 🩹 Troubleshooting

- **No events showing in the UI**
  - Confirm the Flask server is running (`python app.py`).
  - Visit `http://localhost:5001/events` directly to see if any events are returned.
  - Check the GitHub webhook “Recent Deliveries” tab for errors.

- **GitHub webhook shows `502` / `404` / `connection failed`**
  - Ensure ngrok is running and the URL matches the configured webhook.
  - Double-check you are using the **HTTPS** ngrok URL.
  - Confirm the path in GitHub is exactly `/webhook`.

- **MongoDB connection errors**
  - Verify the `MONGODB_URI` in `.env` is correct and URL-encoded where necessary.
  - Make sure your IP is allowed in MongoDB Atlas Network Access settings.
  - Check that `DB_NAME` and `COLLECTION_NAME` are correctly set.

- **Duplicate events appearing**
  - Verify that `request_id` is being set correctly from the webhook payload.
  - Confirm the duplicate-prevention logic (e.g., uniqueness check or `upsert` on `request_id`) in `app.py`.

---

## 🧾 Requirements

Core dependencies (see `requirements.txt` for exact versions):

- **Flask**
- **pymongo**
- **python-dotenv**
- **flask-cors**
- **dnspython**

Install them via:

```bash
pip install -r requirements.txt
```

---

## 💼 Notes for Reviewers (Job Assessment Context)

- The project demonstrates:
  - Backend skills: Flask routing, JSON handling, webhooks, and MongoDB integration.
  - Data modeling: Clean, minimal schema with deduplication using `request_id`.
  - Frontend skills: A responsive, gradient-based dashboard with periodic polling.
  - DevOps practices: ngrok tunneling, environment-based configuration, and cloud DB usage.
- The codebase is intentionally lightweight and focused on **clarity**, **observability**, and **extensibility** for future enhancements (authentication, filtering, pagination, etc.).

Feel free to open issues or submit pull requests with suggestions or improvements. 🙌

