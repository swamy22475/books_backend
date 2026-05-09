# MindWhile ERP - Book Sales Backend

This is a modular FastAPI backend designed for the Book Sales system of the MindWhile ERP.

## Project Structure

```
app/
 ├── main.py              # Application entry point & router inclusion
 ├── database.py          # SQLAlchemy engine & session setup
 ├── modules/             # Business modules
 │    ├── dashboard/      # Summary analytics
 │    ├── vendors/        # Vendor management
 │    ├── inventory/      # Book inventory
 │    ├── stock/          # Stock-in entries & inventory updates
 │    ├── sales/          # Student book sales
 │    ├── returns/        # Book return management
 │    └── reports/        # Advanced reports & analytics
```

## Setup & Running

### 1. Database
- Create a MySQL database named `mindwhile_erp`.
- Update the connection string in `app/database.py` if needed (default: `root@localhost`).

### 2. Environment
- Create a virtual environment: `python -m venv venv`
- Activate it: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)
- Install dependencies: `pip install -r requirements.txt`

### 3. Run the Server
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://localhost:8000`.
Swagger documentation: `http://localhost:8000/docs`.

## Integration
The frontend uses `src/school/pages/BookSales/bookSalesApi.js` to communicate with this backend.
Currently, the **Vendors** page is fully integrated. You can use the same pattern to connect the remaining pages.
