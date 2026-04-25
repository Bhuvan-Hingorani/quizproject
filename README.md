# Python Quiz App

## Setup

1. **Database**
   ```bash
   mysql -u root -p < init_db.sql
   ```

2. **Install Python dependencies**
   ```bash
   pip install flask mysql-connector-python reportlab
   ```

3. **Configure DB credentials** (optional — edit app.py or set env vars)
   ```bash
   export DB_HOST=localhost
   export DB_USER=root
   export DB_PASS=your_password
   export DB_NAME=quiz_db
   ```

4. **Run**
   ```bash
   python app.py
   ```

5. Open `http://localhost:5000`

## File Structure
```
quiz_app/
├── app.py              ← Flask backend
├── init_db.sql         ← DB setup + 20 questions
├── README.md
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── quiz.html
│   └── result.html
└── static/
    ├── style.css
    └── script.js
```
