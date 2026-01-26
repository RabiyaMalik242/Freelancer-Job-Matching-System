# Freelancer Job Matching System (FJMS)

## Project Overview

The **Freelancer Job Matching System (FJMS)** is a Python-based desktop application developed using the **Tkinter** GUI framework. It provides a role-based platform where **clients** can post jobs, **freelancers** can search and apply for jobs, and **administrators** can manage users, jobs, and applications.

The system emphasizes clean architecture, proper input validation, structured exception handling, reliable database management, and independent unit testing using a mock database.

---

## Technologies Used

* **Python 3**
* **Tkinter** (GUI)
* **SQL Server** (Production Database)
* **pyodbc** (Database Connectivity)
* **unittest & unittest.mock** (Unit Testing)

---

## Installation & Run Steps

1. **Clone the repository**

   ```bash
   git clone https://github.com/RabiyaMalik242/Freelancer-Job-Matching-System.git
   cd Freelancer-Job-Matching-System
   
   ```

2. **Install required packages**

   ```bash
   pip install pyodbc
   ```

3. **Set up SQL Server Database**

   * Create a database named `FJMS`
   * Execute the provided SQL scripts to create `Users`, `Jobs`, and `Applications` tables

4. **Run the application**

   ```bash
   python main.py
   ```

5. **Run unit tests**

   ```bash
   python -m unittest discover tests
   ```

---

## Project Structure

```
fjms/
├── database.py          # Database operations and connection handling
├── main.py              # GUI of the application
├── unit_tests.py        # Unit tests for all operations
└── README.md            # Project documentation
```

---

## User Roles and Features

### Admin

* View all users and jobs
* Edit user details (name, email, password, role)
* Delete users along with their jobs and applications
* View all job applications across the system

### Client

* Register and log in
* Post new jobs
* View and delete their own jobs
* View applicants for posted jobs

### Freelancer

* Register and log in
* Browse and search available jobs
* Apply for jobs by submitting name and skills

---

## Object-Oriented Design

* Common base class (**`AppPage`**) for shared GUI behavior
* Separate classes for each major screen:

  * Login Page
  * Registration Page
  * Admin Dashboard
  * Client Dashboard
  * Freelancer Dashboard
* All database operations encapsulated in **`Database`** class for separation of concerns

---

## Database Design and Management

### Tables

* **Users**: full name, email, password, role
* **Jobs**: title, description, budget, category, client email
* **Applications**: job ID, freelancer email, name, skills

### Database Handling

* Centralized CRUD operations in `database.py`
* Transactions use commit and rollback for integrity
* Referential integrity enforced on deletes
* Mock database used for unit tests

---

## Refactoring, Validation, and Exception Handling

* Centralized database access
* Modular GUI classes
* Reusable validation logic
* Input validation: required fields, email format, password length, role check
* Try–except blocks for database operations
* User-friendly error messages
* Rollbacks on database errors
* Graceful handling of unexpected errors

---

## Unit Testing

* **17 unit tests** passing
* Mock database used
* GUI popups patched
* Tests fully isolated and repeatable
* Coverage: user registration/login, job posting/deletion, freelancer applications, admin actions

---

## Future Enhancements

* Password hashing
* Email notifications
* Advanced job search/filter
* Web-based system

---

## Conclusion

The **Freelancer Job Matching System** demonstrates object-oriented design, robust validation, exception handling, database integrity, and independent unit testing. Its modular architecture makes it easy to maintain, extend, and evolve in the future.
