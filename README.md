### **Learnix – Learning Management System (LMS)**

Learnix is a Django-based Learning Management System designed to simplify and digitize online education. It provides a structured platform for managing courses, student enrollments, assignments, and grading, enabling efficient interaction between instructors and students.

---

## **Features**

* **Course Management**

  * Create, update, and manage courses
  * Organize course content and structure

* **Student Enrollment**

  * Students can enroll in available courses
  * Instructors can manage enrolled students

* **Assignment Submission**

  * Instructors can create assignments
  * Students can submit work online
  * Tracks deadlines and submission status

* **Grading & Feedback**

  * Evaluate assignments and assign grades
  * Provide feedback to students
  * Students can track their performance

---

## **User Roles**

* **Admin**

  * Manages platform settings and users
  * Controls roles and permissions

* **Instructor**

  * Creates and manages courses
  * Uploads materials and assignments
  * Grades student submissions

* **Student**

  * Enrolls in courses
  * Accesses learning materials
  * Submits assignments and views grades

---

## **Tech Stack**

* **Backend:** Django
* **Frontend:** HTML, CSS, JavaScript
* **Database:** SQLite / PostgreSQL
* **Authentication:** Django Auth System

---

## **Installation**

```bash
# Clone the repository
git clone https://github.com/HarshaSai1234/Learnix.git

# Navigate into the project folder
cd Learnix

# Create virtual environment
python -m venv venv

# Activate environment
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Run the server
python manage.py runserver
```

---

## **Usage**

1. Open `http://127.0.0.1:8000/` in your browser
2. Register as a student or instructor
3. Admin can configure roles and manage users
4. Start creating courses, enrolling, and submitting assignments

---

## **Project Structure (Basic)**

```
Learnix/
│── manage.py
│── requirements.txt
│── db.sqlite3
│
├── learnix/          # Main project settings
├── users/            # Authentication & roles
├── courses/          # Course management
├── assignments/      # Assignment handling
└── templates/        # HTML templates
```

---

## **Future Enhancements**

* Email notifications
* Real-time chat between students & instructors
* Dashboard analytics (progress graphs)
* File storage with cloud integration
* REST API support for mobile apps

---

## **Contributing**

Contributions are welcome. Fork the repository and submit a pull request.

---

## **License**

This project is for educational purposes.
