-- ─── CREATE & USE DATABASE ──────────────────────────────────────────────────
CREATE DATABASE IF NOT EXISTS quiz_db;
USE quiz_db;

-- ─── DROP TABLES (clean reset) ───────────────────────────────────────────────
DROP TABLE IF EXISTS answers;
DROP TABLE IF EXISTS attempts;
DROP TABLE IF EXISTS questions;
DROP TABLE IF EXISTS users;

-- ─── CREATE TABLES ───────────────────────────────────────────────────────────

CREATE TABLE users (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email    VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE questions (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    question       TEXT NOT NULL,
    option1        TEXT NOT NULL,
    option2        TEXT NOT NULL,
    option3        TEXT NOT NULL,
    option4        TEXT NOT NULL,
    correct_answer INT  NOT NULL
);

CREATE TABLE attempts (
    id      INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    score   INT NOT NULL,
    total   INT NOT NULL,
    date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE answers (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    attempt_id      INT NOT NULL,
    question_id     INT NOT NULL,
    selected_answer INT NOT NULL DEFAULT 0,
    correct_answer  INT NOT NULL,
    FOREIGN KEY (attempt_id)  REFERENCES attempts(id)  ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);

-- ─── INSERT 20 PYTHON QUESTIONS ──────────────────────────────────────────────

INSERT INTO questions (question, option1, option2, option3, option4, correct_answer) VALUES

('What is the output of print(2**3)?',
 '6', '8', '9', '5', 2),

('Which keyword is used to define a function in Python?',
 'func', 'define', 'def', 'function', 3),

('Which data type is immutable?',
 'List', 'Dictionary', 'Set', 'Tuple', 4),

('What is the output of print(type([]))?',
 'list', '<class list>', '<class "list">', 'array', 3),

('Which symbol is used for single-line comments in Python?',
 '//', '#', '/* */', '--', 2),

('What is the output of len("Python")?',
 '5', '6', '7', 'Error', 2),

('Which operator is used for floor division?',
 '/', '//', '%', '**', 2),

('Which built-in function is used to take user input?',
 'get()', 'scan()', 'input()', 'read()', 3),

('What is the output of print(10 % 3)?',
 '1', '2', '3', '0', 1),

('Which keyword is used to create a for-loop?',
 'loop', 'iterate', 'for', 'repeat', 3),

('Which data type represents True/False values?',
 'int', 'str', 'bool', 'float', 3),

('What is the output of print("Hello" + "World")?',
 'Hello World', 'HelloWorld', 'Error', 'None', 2),

('Which function converts a string to an integer?',
 'int()', 'str()', 'float()', 'chr()', 1),

('Which keyword is used for a conditional statement?',
 'if', 'when', 'case', 'check', 1),

('What is the output of print(5 == 5)?',
 'True', 'False', 'Error', '0', 1),

('Which built-in collection type is unordered and unique?',
 'List', 'Tuple', 'Set', 'Array', 3),

('Which list method adds an element to the end?',
 'add()', 'append()', 'insert()', 'push()', 2),

('What is the output of print(3*3*3)?',
 '9', '6', '27', '18', 3),

('Which keyword is used to exit a loop immediately?',
 'stop', 'break', 'exit', 'end', 2),

('Which function returns the length of a list?',
 'count()', 'size()', 'len()', 'length()', 3);

-- ─── VERIFY ──────────────────────────────────────────────────────────────────
SELECT COUNT(*) AS total_questions FROM questions;
