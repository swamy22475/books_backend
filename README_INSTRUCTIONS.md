# Books Management Backend

This is the separated backend for the Book Sales module.

## Setup Instructions

1. **Prerequisites**:
   - Python 3.8+
   - MySQL Server

2. **Database Setup**:
   - Create a MySQL database named `mindwhile_erp`.
   - Update `app/database.py` with your MySQL credentials (user/password).

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Server**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

## Connection to Frontend

The frontend in `mindwhileerp-fe-master` has been configured to connect to this backend at `http://localhost:8000/api/v1`.
