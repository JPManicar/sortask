# Sortask 
## A Task Management Web Application 

> A Collaborative Project for Self-Learning and Improving Practical Skills in Web Development
> by Marlo Tunggolh and Juan Paolo B. Manicar



## Backend Setup

### Prerequisites

* Python
* MySQL

### Backend Setup

1. **Navigate to the backend directory:**

   ```bash
   cd backend
   ```

2. **Create virtual environment**

    ```bash
    python -m venv .venv
    ```

3. **Activate virtual environment**

    *Windows*
    ```bash
    .venv\Scripts\activate
    ```
    
    *Mac*
    ```bash
    source .venv/bin/activate
    ```
4. **Install required packages**
    ```bash
    pip install -r requirements.txt
    ```

5. **Create sortask Database**

    Exceute the following SQL script in your MySQL environment:
    ```bash
    CREATE DATABASE sortask;
    ```

6. **Go to settings.py**
    ```bash
    backend/core/settings.py
    ```

7. **Change password to your MySQL password in line 97**


8. **Run command**
    ```bash
    python manage.py migrate
    ```

9. **Run backend server**
    ```bash
    python manage.py runserver
    ```



