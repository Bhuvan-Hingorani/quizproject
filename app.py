import os
import tempfile

from flask import Flask, render_template, request, redirect, session, send_file, url_for
import mysql.connector

# PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-production")

# ─── DATABASE ────────────────────────────────────────────────────────────────

def get_db():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASS", "Bhuvan@1817"),
        database=os.environ.get("DB_NAME", "quiz_db")
    )

# ─── HOME / LOGIN PAGE ───────────────────────────────────────────────────────

@app.route('/')
def home():
    msg = session.pop('message', None)
    return render_template("login.html", msg=msg)

@app.route('/register_page')
def register_page():
    return render_template("register.html")

# ─── REGISTER ────────────────────────────────────────────────────────────────

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username', '').strip()
    email    = request.form.get('email', '').strip()
    password = request.form.get('password', '')

    if not username or not email or not password:
        return render_template("register.html", error="All fields are required.")

    db = get_db()
    cursor = db.cursor()

    # Check if username already exists
    cursor.execute("SELECT id FROM users WHERE username=%s", (username,))
    if cursor.fetchone():
        cursor.close(); db.close()
        return render_template("register.html", error="Username already taken.")

    cursor.execute(
        "INSERT INTO users(username, email, password) VALUES (%s, %s, %s)",
        (username, email, password)
    )
    db.commit()
    cursor.close(); db.close()

    session['message'] = "Registration successful! Please log in."
    return redirect('/')

# ─── LOGIN ───────────────────────────────────────────────────────────────────

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username=%s AND password=%s",
        (username, password)
    )
    user = cursor.fetchone()
    cursor.close(); db.close()

    if user:
        session['user_id']  = user[0]
        session['username'] = user[1]
        return redirect('/quiz')
    else:
        return render_template("login.html", error="Invalid username or password.")

# ─── QUIZ ────────────────────────────────────────────────────────────────────

@app.route('/quiz')
def quiz():
    if 'user_id' not in session:
        return redirect('/')

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM questions ORDER BY id")
    questions = cursor.fetchall()
    cursor.close(); db.close()

    time_limit = 1800  # 30 minutes in seconds

    return render_template(
        "quiz.html",
        questions=questions,
        time_limit=time_limit
    )

# ─── SUBMIT ──────────────────────────────────────────────────────────────────

@app.route('/submit', methods=['POST'])
def submit():
    if 'user_id' not in session:
        return redirect('/')

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM questions ORDER BY id")
    questions = cursor.fetchall()

    score = 0

    for q in questions:
        q_id    = q[0]
        correct = q[6]
        selected = request.form.get(str(q_id))
        selected = int(selected) if selected else 0
        if selected == correct:
            score += 1

    cursor.execute(
        "INSERT INTO attempts(user_id, score, total) VALUES (%s, %s, %s)",
        (session['user_id'], score, len(questions))
    )
    attempt_id = cursor.lastrowid

    for q in questions:
        q_id    = q[0]
        correct = q[6]
        selected = request.form.get(str(q_id))
        selected = int(selected) if selected else 0
        cursor.execute(
            "INSERT INTO answers(attempt_id, question_id, selected_answer, correct_answer) "
            "VALUES (%s, %s, %s, %s)",
            (attempt_id, q_id, selected, correct)
        )

    db.commit()
    cursor.close(); db.close()

    return redirect(f'/result/{attempt_id}')

# ─── RESULT ──────────────────────────────────────────────────────────────────

@app.route('/result/<int:attempt_id>')
def result(attempt_id):
    if 'user_id' not in session:
        return redirect('/')

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT q.question, q.option1, q.option2, q.option3, q.option4,
               a.selected_answer, a.correct_answer
        FROM answers a
        JOIN questions q ON a.question_id = q.id
        WHERE a.attempt_id = %s
        ORDER BY q.id
    """, (attempt_id,))
    results = cursor.fetchall()

    cursor.execute(
        "SELECT score, total FROM attempts WHERE id=%s",
        (attempt_id,)
    )
    attempt = cursor.fetchone()
    cursor.close(); db.close()

    # Pre-compute stats for the template
    correct_count = sum(1 for r in results if r[5] == r[6] and r[5] != 0)
    skip_count    = sum(1 for r in results if r[5] == 0)
    wrong_count   = len(results) - correct_count - skip_count

    return render_template(
        "result.html",
        results=results,
        score=attempt[0],
        total=attempt[1],
        attempt_id=attempt_id,
        username=session.get('username', 'User'),
        correct_count=correct_count,
        wrong_count=wrong_count,
        skip_count=skip_count
    )

# ─── PDF DOWNLOAD ─────────────────────────────────────────────────────────────

@app.route('/download/<int:attempt_id>')
def download_pdf(attempt_id):
    if 'user_id' not in session:
        return redirect('/')

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "SELECT score, total FROM attempts WHERE id=%s",
        (attempt_id,)
    )
    attempt = cursor.fetchone()

    cursor.execute("""
        SELECT q.question, q.option1, q.option2, q.option3, q.option4,
               a.selected_answer, a.correct_answer
        FROM answers a
        JOIN questions q ON a.question_id = q.id
        WHERE a.attempt_id = %s
        ORDER BY q.id
    """, (attempt_id,))
    results = cursor.fetchall()
    cursor.close(); db.close()

    username = session.get('username', 'User')
    score, total = attempt[0], attempt[1]

    # Build PDF in a temp file (not in CWD)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    tmp.close()
    file_path = tmp.name

    doc    = SimpleDocTemplate(file_path, pagesize=A4,
                               leftMargin=2*cm, rightMargin=2*cm,
                               topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('Title2', parent=styles['Title'],
                                 fontSize=20, spaceAfter=6)
    h3_style    = ParagraphStyle('H3', parent=styles['Heading3'],
                                 fontSize=12, textColor=colors.HexColor('#6c63ff'))
    body_style  = styles['Normal']
    correct_style = ParagraphStyle('Correct', parent=body_style,
                                   textColor=colors.HexColor('#16a34a'), fontName='Helvetica-Bold')
    wrong_style   = ParagraphStyle('Wrong',   parent=body_style,
                                   textColor=colors.HexColor('#dc2626'), fontName='Helvetica-Bold')

    content = []

    content.append(Paragraph("🐍 Python Quiz Result", title_style))
    content.append(Spacer(1, 10))

    # Score table
    options_map_fn = lambda r, idx: {1: r[1], 2: r[2], 3: r[3], 4: r[4]}.get(idx, "—")

    info_data = [
        ["Name",  username],
        ["Score", f"{score} / {total}"],
        ["Percentage", f"{round(score/total*100)}%"],
        ["Result", "Pass ✓" if score >= total * 0.4 else "Fail ✗"],
    ]
    info_table = Table(info_data, colWidths=[4*cm, 12*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f3f4f6')),
        ('FONTNAME',   (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTSIZE',   (0,0), (-1,-1), 11),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, colors.HexColor('#fafafa')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e5e7eb')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    content.append(info_table)
    content.append(Spacer(1, 20))
    content.append(Paragraph("Detailed Review", h3_style))
    content.append(Spacer(1, 10))

    for i, r in enumerate(results):
        user_ans    = options_map_fn(r, r[5]) if r[5] != 0 else "Not Answered"
        correct_ans = options_map_fn(r, r[6])

        if r[5] == 0:
            verdict = "⚠ Skipped"
            v_style = wrong_style
        elif r[5] == r[6]:
            verdict = "✔ Correct"
            v_style = correct_style
        else:
            verdict = "✘ Wrong"
            v_style = wrong_style

        q_data = [
            [Paragraph(f"Q{i+1}. {r[0]}", body_style), ""],
            ["Your Answer:", Paragraph(user_ans, body_style)],
            ["Correct Answer:", Paragraph(correct_ans, correct_style)],
            ["", Paragraph(verdict, v_style)],
        ]
        q_table = Table(q_data, colWidths=[5*cm, 11*cm])
        q_table.setStyle(TableStyle([
            ('SPAN', (0,0), (1,0)),
            ('BACKGROUND', (0,0), (1,0), colors.HexColor('#f5f3ff')),
            ('FONTNAME', (0,1), (0,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#e5e7eb')),
            ('PADDING', (0,0), (-1,-1), 7),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        content.append(q_table)
        content.append(Spacer(1, 8))

    doc.build(content)

    return send_file(
        file_path,
        as_attachment=True,
        download_name=f"quiz_result_{username}_{attempt_id}.pdf",
        mimetype='application/pdf'
    )

# ─── LOGOUT ──────────────────────────────────────────────────────────────────

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ─── RUN ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)

app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
