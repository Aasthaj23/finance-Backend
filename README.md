
#  Finance Backend API with RBAC & JWT

##  Overview

This project is a backend system for a finance dashboard that manages financial records with **role-based access control (RBAC)** and **JWT authentication**.

It allows different types of users (Viewer, Analyst, Admin) to interact with financial data based on their permissions. The system also provides summary-level analytics for dashboard visualization.

##  Tech Stack

* **Backend Framework:** FastAPI
* **Database:** SQLite
* **ORM:** SQLAlchemy
* **Authentication:** JWT (OAuth2 Password Flow)
* **Validation:** Pydantic

##  Authentication & Authorization

###  Authentication

* JWT-based authentication using OAuth2
* Secure password hashing using bcrypt
* Token expiration support

###  Role-Based Access Control (RBAC)

| Role    | Permissions                   |
| ------- | ----------------------------- |
| Viewer  | View dashboard only           |
| Analyst | View records + analytics      |
| Admin   | Full access (users + records) |

## 👤 User Management APIs

| Method | Endpoint           | Description                         |
| ------ | ------------------ | ----------------------------------- |
| POST   | `/auth/register`   | Register new user (default: viewer) |
| POST   | `/auth/login`      | Login and get JWT token             |
| GET    | `/auth/me`         | Get current user info               |
| GET    | `/users`           | Get all users (Admin only)          |
| PUT    | `/users/{id}/role` | Update user role (Admin)            |
| DELETE | `/users/{id}`      | Deactivate user                     |


##  Financial Records APIs

| Method | Endpoint        | Description                       |
| ------ | --------------- | --------------------------------- |
| POST   | `/records`      | Create record (Admin)             |
| GET    | `/records`      | Get records (filter + pagination) |
| GET    | `/records/{id}` | Get single record                 |
| PATCH  | `/records/{id}` | Update record                     |
| DELETE | `/records/{id}` | Delete record                     |

###  Filtering Options

```bash
/records?record_type=income
/records?category=food
/records?search=rent
/records?date_from=2025-01-01
```

###  Pagination

```bash
/records?skip=0&limit=10
```
---

##  Dashboard APIs

| Endpoint                | Description                        |
| ----------------------- | ---------------------------------- |
| `/dashboard/summary`    | Total income, expense, net balance |
| `/dashboard/categories` | Category-wise totals               |
| `/dashboard/trends`     | Monthly trends (income/expense)    |
| `/dashboard/recent`     | Recent transactions                |

##  Project Structure

```
finance-backend/
│── main.py
│── models.py
│── schemas.py
│── database.py
│── requirements.txt
│── README.md
```

##  Setup Instructions

### 1. Clone Repository

```bash
git clone <your-repo-link>
cd finance-backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Server

```bash
uvicorn main:app --reload
```

##  API Documentation

* Swagger UI → http://127.0.0.1:8000/docs
* ReDoc → http://127.0.0.1:8000/redoc

---

##  How to Use JWT

1. Register user → `/auth/register`
2. Login → `/auth/login`
3. Copy access token
4. Click **Authorize ** in Swagger
5. Enter:

```
Bearer <your-token>
```

##  Validation & Error Handling

* Input validation using Pydantic
* Proper HTTP status codes
* Meaningful error messages
* Protection against invalid roles and values

##  Key Design Decisions

* Used dependency injection for RBAC
* Separated schemas for create, update, and response
* Applied database-level constraints for data integrity
* Implemented filtering, search, and pagination for scalability

##  Possible Improvements

* Docker containerization
* PostgreSQL integration
* Unit & integration testing
* API rate limiting
* Deployment (Render / Railway)

##  Conclusion

This project demonstrates:

* Backend API design
* Secure authentication (JWT)
* Role-based access control
* Data validation and modeling
* Aggregation and analytics logic

The focus is on building a clean, scalable, and maintainable backend system.
