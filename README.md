# Bertram Labs Coffee Order App

A web app and API to help a group of coffee drinkers fairly decide whose turn it is to pay for coffee, taking into account each person's favorite drink and its cost.

---

## Deliverables

### 1. Instructions: How to Build and Run

#### **Preferred: Try It Online**

- Visit [https://bertram.jade.rip/](https://bertram.jade.rip/) to use the app instantly in your browser.

#### **Run with Docker (Alternative)**

1. Build the Docker image:

   ```sh
   docker build -t coffee-order .
   ```

2. Run the app:

   ```sh
   docker run -p 8000:8000 coffee-order
   ```

3. Open [http://localhost:8000](http://localhost:8000) in your browser.

#### **Requirements (for local development)**

- Python 3.13 (see `.python-version`)
- Nix (optional, for reproducible setup)
- Or use `pip` / `uv` to install dependencies

---

### 2. Assumptions

- Each person has a unique name (case-insensitive).
- Each person has a favorite drink and its cost, which can be updated at any time.
- Only one person pays for each round; the app tracks who should pay next based on net balance (what they've paid minus what they've consumed).
- All data is stored in a local JSON file (`coffee_pot.json`). No external database is required.
- The app is intended for small groups and is not designed for concurrent multi-user editing.

---

### 3. How to Enter Required Data

#### **Via the Web Interface**

- **Add a Drinker:** Use the "Add a New Drinker" form (left column). Enter the name, favorite drink, and its cost.
- **Update a Drinker:** Click a drinker in the list (center column) to pre-fill the update form (right column), then edit and submit.
- **Record a Coffee Round:** Click "Record Round" (left column) when someone pays for a round. The app will update balances and highlight the next payer.
- **Reset Balances:** Use the "Reset All Balances" button (right column) to set all balances to zero.

#### **Via the API**

- See [`rest-test.http`](rest-test.http) for example API requests (GET, POST, PUT, DELETE).
- Endpoints include:
  - `GET /drinkers` — List all drinkers
  - `POST /drinkers` — Add a new drinker
  - `PUT /drinkers/{id}` — Update a drinker
  - `POST /coffee-rounds` — Record a round
  - `POST /reset-balances` — Reset all balances

---

### 4. Running the Solution Locally or Online

- **Data Persistence:**  
  By default, all data is stored in `coffee_pot.json` in the project directory. This is suitable for proof-of-concept and small group use.  
  **For production or larger groups, you should migrate to a real database**
  To reset the current data, simply delete `coffee_pot.json` and restart the app.

---

## Project Structure

- `main.py` — FastAPI app and all backend logic
- `templates/index.html` — Main web UI (Jinja2)
- `static/` — CSS and JS for the frontend
- `rest-test.http` — Example API requests
- `coffee_pot.json` — Data file (auto-created)
