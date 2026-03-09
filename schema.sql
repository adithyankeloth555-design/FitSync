-- FitSync Project SQL Schema & Sample Data
-- Optimized for MySQL Workbench

-- Create Database
CREATE DATABASE IF NOT EXISTS fitsync_db;
USE fitsync_db;

-- 1. User Profiles
CREATE TABLE IF NOT EXISTS user_profiles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(150) NOT NULL,
    email VARCHAR(255),
    role ENUM('member', 'trainer', 'admin') DEFAULT 'member',
    fitness_goal VARCHAR(255),
    weight_kg DECIMAL(5,2),
    height_cm DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Diet Plans
CREATE TABLE IF NOT EXISTS diet_plans (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    daily_calories INT,
    protein_g INT,
    carbs_g INT,
    fats_g INT,
    description TEXT
);

-- 3. Workout Programs
CREATE TABLE IF NOT EXISTS workout_programs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    difficulty ENUM('Beginner', 'Intermediate', 'Advanced'),
    frequency_per_week INT,
    details TEXT
);

-- 4. Attendance
CREATE TABLE IF NOT EXISTS attendance (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    workout_type VARCHAR(100),
    notes TEXT,
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profiles(id)
);

-- 5. Payments
CREATE TABLE IF NOT EXISTS payments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    transaction_id VARCHAR(100) UNIQUE,
    amount DECIMAL(10,2),
    status ENUM('success', 'pending', 'failed'),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profiles(id)
);

-- --- SAMPLE DATA ---

-- Insert Users
INSERT INTO user_profiles (username, email, role, fitness_goal, weight_kg, height_cm) VALUES 
('alex_fit', 'alex@example.com', 'member', 'Muscle Gain', 75.5, 180.0),
('sarah_trainer', 'sarah@fitsync.com', 'trainer', 'Help others', 65.0, 165.0),
('admin_main', 'admin@fitsync.com', 'admin', 'System Mgmt', 80.0, 175.0);

-- Insert Diet Plans
INSERT INTO diet_plans (name, daily_calories, protein_g, carbs_g, fats_g, description) VALUES 
('Lean Bulk Protocol', 2800, 200, 300, 80, 'High protein for muscle growth with moderate carbs.'),
('Keto Shred', 1800, 150, 30, 120, 'Low carb, high fat for rapid weight loss.');

-- Insert Workout Programs
INSERT INTO workout_programs (title, difficulty, frequency_per_week, details) VALUES 
('Strength Foundation', 'Intermediate', 4, 'Focus on Bench, Squat, and Deadlift.'),
('Couch to 5K', 'Beginner', 3, 'Running program for cardiovascular health.');

-- Insert Attendance
INSERT INTO attendance (user_id, workout_type, notes) VALUES 
(1, 'Weight Training', 'Hit a new PR on Bench Press!'),
(1, 'Cardio', 'Light 30min run on treadmill.');

-- Insert Payments
INSERT INTO payments (user_id, transaction_id, amount, status) VALUES 
(1, 'TXN-001928', 49.00, 'success'),
    (1, 'TXN-001930', 49.00, 'success');

-- 6. User Subscriptions
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT UNIQUE,
    plan_type ENUM('basic', 'premium', 'elite'),
    start_date DATE DEFAULT (CURRENT_DATE),
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES user_profiles(id)
);

-- 7. BMI History
CREATE TABLE IF NOT EXISTS bmi_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    weight_kg DECIMAL(5,2),
    height_cm DECIMAL(5,2),
    bmi_score DECIMAL(5,2),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profiles(id)
);

-- 8. Notifications
CREATE TABLE IF NOT EXISTS notifications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    title VARCHAR(255),
    message TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profiles(id)
);

-- 9. Goals
CREATE TABLE IF NOT EXISTS goals (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    title VARCHAR(255),
    description TEXT,
    target_date DATE,
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profiles(id)
);

-- 10. Daily Nutrition Log
CREATE TABLE IF NOT EXISTS nutrition_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    log_date Date DEFAULT (CURRENT_DATE),
    meal_type VARCHAR(50),
    food_item VARCHAR(255),
    calories INT,
    protein INT,
    carbs INT,
    fats INT,
    FOREIGN KEY (user_id) REFERENCES user_profiles(id)
);

-- 11. Messages
CREATE TABLE IF NOT EXISTS messages (
    id INT PRIMARY KEY AUTO_INCREMENT,
    sender_id INT,
    receiver_id INT,
    subject VARCHAR(255),
    body TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES user_profiles(id),
    FOREIGN KEY (receiver_id) REFERENCES user_profiles(id)
);

-- 12. Community Posts & Comments
CREATE TABLE IF NOT EXISTS community_posts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    author_id INT,
    content TEXT,
    image_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES user_profiles(id)
);

CREATE TABLE IF NOT EXISTS community_comments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    post_id INT,
    author_id INT,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES community_posts(id),
    FOREIGN KEY (author_id) REFERENCES user_profiles(id)
);
