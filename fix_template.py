import re

f = r'c:\Users\adith\OneDrive\圖片\fit\templates\fitsync_app\edit_subscription_plan.html'

with open(f, 'r', encoding='utf-8') as fh:
    content = fh.read()

# Add mobile responsive overrides before the closing </style> tag
mobile_css = """
    /* ---- Mobile Responsive ---- */
    @media (max-width: 1024px) {
        .sidebar {
            transform: translateX(-100%);
            transition: transform 0.3s ease;
        }

        .sidebar.open {
            transform: translateX(0);
            box-shadow: 10px 0 30px rgba(0, 0, 0, 0.5);
        }

        .main-area {
            margin-left: 0;
        }

        .dashboard-content {
            padding: 1rem;
            padding-top: 1rem;
        }
    }

    @media (max-width: 768px) {
        .main-area {
            margin-left: 0;
        }

        .top-bar {
            padding: 0.5rem 1rem;
        }

        .dashboard-content {
            padding: 1rem;
        }

        .dashboard-content > header {
            flex-direction: column;
            align-items: flex-start;
        }

        .dashboard-content > header h1 {
            font-size: 1.4rem;
        }

        .edit-container {
            max-width: 100%;
        }

        .edit-card {
            padding: 1.5rem;
        }

        .btn-save {
            width: 100%;
            justify-content: center;
        }
    }
"""

# Insert before </style>
content = content.replace('</style>', mobile_css + '</style>', 1)

with open(f, 'w', encoding='utf-8') as fh:
    fh.write(content)

print('Mobile styles added to edit_subscription_plan.html')
