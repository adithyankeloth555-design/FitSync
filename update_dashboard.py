
import os

file_path = r"c:\Users\adith\OneDrive\圖片\fit\templates\fitsync_app\user_dashboard.html"

new_content = r"""{% extends 'fitsync_app/base.html' %}
{% load static %}

{% block title %}Dashboard | FitSync Elite{% endblock %}

{% block header %}{% endblock %}
{% block footer %}{% endblock %}

{% block extra_css %}
<style>
    :root {
        --sidebar-bg: #1e293b;
        --sidebar-hover: rgba(255, 255, 255, 0.05);
        --accent-orange: #f97316;
        --content-bg: #f5f7f9;
        --text-main: #1e293b;
        --text-muted: #64748b;
        --white: #ffffff;
        --card-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    }

    body {
        background-color: var(--content-bg);
        color: var(--text-main);
        font-family: 'Outfit', sans-serif;
        margin: 0;
        display: flex;
        min-height: 100vh;
    }

    .sidebar {
        width: 250px;
        background: var(--sidebar-bg);
        color: #fff;
        display: flex;
        flex-direction: column;
        position: fixed;
        height: 100vh;
        z-index: 1000;
        padding: 0;
        overflow-y: auto;
    }

    .sidebar::-webkit-scrollbar {
        width: 6px;
    }

    .sidebar::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
    }

    .sidebar::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 3px;
    }

    .sidebar-profile {
        padding: 2rem 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }

    .profile-img {
        width: 38px;
        height: 38px;
        border-radius: 8px;
        object-fit: cover;
    }

    .profile-name {
        font-weight: 700;
        font-size: 0.95rem;
        color: #fff;
    }

    .sidebar-nav {
        flex-grow: 1;
        padding: 0 1rem 1rem 1rem;
    }

    .nav-section {
        margin-bottom: 1.5rem;
    }

    .nav-section-title {
        font-size: 0.7rem;
        text-transform: uppercase;
        color: #64748b;
        font-weight: 800;
        letter-spacing: 1.5px;
        padding: 0 1rem;
        margin-bottom: 0.5rem;
    }

    .nav-link {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 0.8rem 1rem;
        color: #94a3b8;
        text-decoration: none;
        font-size: 0.9rem;
        font-weight: 500;
        border-radius: 8px;
        margin-bottom: 0.3rem;
        transition: 0.2s;
    }

    .nav-link:hover {
        background: var(--sidebar-hover);
        color: #fff;
    }

    .nav-link.active {
        background: var(--accent-orange);
        color: #fff;
    }

    .nav-link i {
        width: 20px;
        text-align: center;
        font-size: 1.1rem;
    }

    .sidebar-footer {
        padding: 1.5rem;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
    }

    .logout-btn {
        display: flex;
        align-items: center;
        gap: 1rem;
        color: #94a3b8;
        text-decoration: none;
        font-size: 0.9rem;
        font-weight: 500;
        background: none;
        border: none;
        width: 100%;
        cursor: pointer;
        padding: 0.8rem 1rem;
    }

    .logout-btn:hover {
        color: #fff;
    }

    .main-wrapper {
        margin-left: 250px;
        flex-grow: 1;
        padding: 3rem 4rem;
    }

    .page-title {
        font-family: 'Cinzel', serif;
        font-size: 2.2rem;
        font-weight: 700;
        color: var(--accent-orange);
        text-transform: uppercase;
        margin: 0 0 0.5rem 0;
    }

    .page-subtitle {
        color: var(--text-muted);
        font-size: 1.1rem;
        margin-bottom: 3rem;
    }

    .stats-row {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 2rem;
        margin-bottom: 3rem;
    }

    .stat-card {
        background: var(--white);
        padding: 2rem;
        border-radius: 16px;
        box-shadow: var(--card-shadow);
        border: 1px solid rgba(0, 0, 0, 0.02);
    }

    .stat-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        color: var(--text-muted);
        font-weight: 700;
        letter-spacing: 1px;
        display: block;
        margin-bottom: 1rem;
    }

    .stat-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: var(--text-main);
        display: block;
        margin-bottom: 1rem;
    }

    .status-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 800;
        background: #f1f5f9;
        color: var(--text-muted);
    }

    .status-optimal {
        background: #dcfce7;
        color: #15803d;
    }

    .status-alert {
        background: #fee2e2;
        color: #991b1b;
    }

    .section-header {
        font-family: 'Cinzel', serif;
        font-size: 1.5rem;
        margin: 3rem 0 2rem 0;
        color: #1e293b;
        letter-spacing: 1px;
    }

    .actions-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
        gap: 1.5rem;
        margin-bottom: 3rem;
    }

    .action-card {
        background: var(--white);
        padding: 2rem;
        border-radius: 16px;
        text-decoration: none;
        color: inherit;
        box-shadow: var(--card-shadow);
        text-align: center;
        transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid transparent;
    }

    .action-card:hover {
        transform: translateY(-8px);
        border-color: var(--accent-orange);
        box-shadow: 0 15px 35px rgba(249, 115, 22, 0.1);
    }

    .action-card i {
        font-size: 2.5rem;
        color: var(--accent-orange);
        margin-bottom: 1rem;
    }

    .action-card h3 {
        font-size: 1.1rem;
        font-weight: 800;
        margin: 0 0 0.5rem 0;
    }

    .action-card p {
        color: var(--text-muted);
        font-size: 0.85rem;
        margin: 0;
        line-height: 1.5;
    }

    .btn-update {
        display: inline-block;
        margin-top: 1rem;
        padding: 0.6rem 1.2rem;
        background: var(--accent-orange);
        color: #fff;
        text-decoration: none;
        border-radius: 8px;
        font-weight: 700;
        font-size: 0.85rem;
    }
</style>
{% endblock %}

{% block content %}
<aside class="sidebar">
    <div class="sidebar-profile">
        <img src="https://i.pravatar.cc/150?u={{ user.username }}" class="profile-img" alt="Profile">
        <span class="profile-name">{{ user.username|title }}</span>
    </div>

    <nav class="sidebar-nav">
        <div class="nav-section">
            <div class="nav-section-title">Main</div>
            <a href="{% url 'user_dashboard' %}" class="nav-link active">
                <i class="fa-solid fa-house"></i> Home
            </a>
            <a href="{% url 'progress' %}" class="nav-link">
                <i class="fa-solid fa-chart-line"></i> Progress
            </a>
        </div>

        <div class="nav-section">
            <div class="nav-section-title">Fitness</div>
            <a href="{% url 'workout_list' %}" class="nav-link">
                <i class="fa-solid fa-dumbbell"></i> My Workouts
            </a>
            <a href="{% url 'diet_list' %}" class="nav-link">
                <i class="fa-solid fa-utensils"></i> Diet Plan
            </a>
            <a href="{% url 'nutrition' %}" class="nav-link">
                <i class="fa-solid fa-droplet"></i> Nutrition
            </a>
            <a href="{% url 'bmi_history' %}" class="nav-link">
                <i class="fa-solid fa-heart-pulse"></i> Vitality
            </a>
            <a href="{% url 'goals' %}" class="nav-link">
                <i class="fa-solid fa-bullseye"></i> Goals
            </a>
        </div>

        <div class="nav-section">
            <div class="nav-section-title">Membership</div>
            <a href="{% url 'attendance' %}" class="nav-link">
                <i class="fa-solid fa-calendar-check"></i> Attendance
            </a>
            <a href="{% url 'membership' %}" class="nav-link">
                <i class="fa-solid fa-crown"></i> Membership
            </a>
        </div>

        <div class="nav-section">
            <div class="nav-section-title">Connect</div>
            <a href="{% url 'trainer_list' %}" class="nav-link">
                <i class="fa-solid fa-user-tie"></i> Trainers
            </a>
            <a href="{% url 'messages' %}" class="nav-link">
                <i class="fa-solid fa-comments"></i> Messages
            </a>
            <a href="{% url 'community' %}" class="nav-link">
                <i class="fa-solid fa-users"></i> Community
            </a>
            <a href="{% url 'chatbot' %}" class="nav-link">
                <i class="fa-solid fa-robot"></i> AI Coach
            </a>
        </div>

        <div class="nav-section">
            <div class="nav-section-title">Support</div>
            <a href="{% url 'settings' %}" class="nav-link">
                <i class="fa-solid fa-gear"></i> Settings
            </a>
            <a href="{% url 'help' %}" class="nav-link">
                <i class="fa-solid fa-circle-question"></i> Help
            </a>
        </div>
    </nav>

    <div class="sidebar-footer">
        <form action="{% url 'logout' %}" method="post">
            {% csrf_token %}
            <button type="submit" class="logout-btn">
                <i class="fa-solid fa-right-from-bracket"></i> Logout
            </button>
        </form>
    </div>
</aside>

<main class="main-wrapper">
    <header class="page-header">
        <h1 class="page-title">Performance Dashboard</h1>
        <p class="page-subtitle">Welcome back, {{ user.username|title }}. Your current physiological status is
            summarized below.</p>
    </header>

    <div class="stats-row">
        <div class="stat-card">
            {% with last_bmi=user.bmi_records.first %}
            <span class="stat-label">Biometric Index</span>
            <div class="stat-value">{{ last_bmi.bmi_score|default:"--" }}</div>
            {% if last_bmi %}
            <span class="status-pill {% if last_bmi.bmi_score < 18.5 or last_bmi.bmi_score >= 25 %}status-alert{% else %}status-optimal{% endif %}">
                {% if last_bmi.bmi_score < 18.5 %}Underweight{% elif last_bmi.bmi_score < 25 %}Optimal{% elif last_bmi.bmi_score < 30 %}Overweight{% else %}Obese{% endif %}
            </span>
            {% else %}
            <span class="status-pill">No Data Available</span>
            {% endif %}
            {% endwith %}
            <a href="{% url 'bmi_calculator' %}" class="btn-update" style="display:block;text-align:center;margin-top:1.5rem">Update Vitals</a>
        </div>

        <div class="stat-card">
            <span class="stat-label">Deployment Consistency</span>
            <div class="stat-value">{{ user.attendance_logs.count }}</div>
            <span class="status-pill status-optimal">Active Enrollment</span>
            <p class="text-muted" style="font-size:0.85rem;margin-top:1rem">Sessions completed in current cycle.</p>
        </div>

        <div class="stat-card">
            <span class="stat-label">Access Level</span>
            <div class="stat-value" style="font-size:1.8rem;margin-top:0.4rem">{{ user.userprofile.get_role_display|default:"Standard" }}</div>
            <span class="status-pill" style="background:#fff7ed;color:#c2410c">Premium Access Active</span>
            <p class="text-muted" style="font-size:0.85rem;margin-top:1rem">Full suite of AI tools unlocked.</p>
        </div>
    </div>

    <h2 class="section-header">Core Training Modules</h2>
    <div class="actions-grid">
        <a href="{% url 'workout_list' %}" class="action-card">
            <i class="fa-solid fa-dumbbell"></i>
            <h3>Training</h3>
            <p>Access workout protocols and AI generators</p>
        </a>
        <a href="{% url 'diet_list' %}" class="action-card">
            <i class="fa-solid fa-leaf"></i>
            <h3>Nutrition</h3>
            <p>Optimize meal scheduling and macros</p>
        </a>
        <a href="{% url 'chatbot' %}" class="action-card">
            <i class="fa-solid fa-brain"></i>
            <h3>Neural Link (AI)</h3>
            <p>Real-time training adjustments</p>
        </a>
        <a href="{% url 'progress' %}" class="action-card">
            <i class="fa-solid fa-chart-line"></i>
            <h3>Progress</h3>
            <p>Activity charts and workout analytics</p>
        </a>
    </div>

    <h2 class="section-header">Tracking & Goals</h2>
    <div class="actions-grid">
        <a href="{% url 'attendance' %}" class="action-card">
            <i class="fa-solid fa-calendar-check"></i>
            <h3>Attendance</h3>
            <p>Daily check-ins, streaks, and history</p>
        </a>
        <a href="{% url 'nutrition' %}" class="action-card">
            <i class="fa-solid fa-droplet"></i>
            <h3>Nutrition Tracker</h3>
            <p>Water intake, calories, and protein</p>
        </a>
        <a href="{% url 'goals' %}" class="action-card">
            <i class="fa-solid fa-bullseye"></i>
            <h3>Goals</h3>
            <p>Weight loss, muscle gain, daily targets</p>
        </a>
        <a href="{% url 'bmi_history' %}" class="action-card">
            <i class="fa-solid fa-heart-pulse"></i>
            <h3>Vitality</h3>
            <p>BMI tracking and health metrics</p>
        </a>
    </div>

    <h2 class="section-header">Membership & Community</h2>
    <div class="actions-grid">
        <a href="{% url 'membership' %}" class="action-card">
            <i class="fa-solid fa-crown"></i>
            <h3>Membership</h3>
            <p>Plan details, expiry, and upgrades</p>
        </a>
        <a href="{% url 'trainer_list' %}" class="action-card">
            <i class="fa-solid fa-user-tie"></i>
            <h3>Trainers</h3>
            <p>Connect with fitness professionals</p>
        </a>
        <a href="{% url 'messages' %}" class="action-card">
            <i class="fa-solid fa-comments"></i>
            <h3>Messages</h3>
            <p>Chat with your trainer</p>
        </a>
        <a href="{% url 'community' %}" class="action-card">
            <i class="fa-solid fa-users"></i>
            <h3>Community</h3>
            <p>Groups, challenges, and friends</p>
        </a>
    </div>

    <h2 class="section-header">Settings & Support</h2>
    <div class="actions-grid">
        <a href="{% url 'settings' %}" class="action-card">
            <i class="fa-solid fa-gear"></i>
            <h3>Settings</h3>
            <p>Profile, privacy, and preferences</p>
        </a>
        <a href="{% url 'help' %}" class="action-card">
            <i class="fa-solid fa-circle-question"></i>
            <h3>Help Center</h3>
            <p>Support and documentation</p>
        </a>
    </div>
</main>
{% endblock %}
"""

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"Successfully updated {file_path}")
