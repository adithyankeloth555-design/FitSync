import os
import glob

base_dir = r'c:\Users\adith\OneDrive\圖片\fit\templates\fitsync_app'

# Files that use .main-area layout (admin pages)
admin_pages = [
    'admin_dashboard.html',
    'subscription_plans.html', 
    'report_payments.html',
]

mobile_css_block = """
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
    }
"""

for page in admin_pages:
    filepath = os.path.join(base_dir, page)
    if not os.path.exists(filepath):
        print(f'SKIP: {page} not found')
        continue
    
    with open(filepath, 'r', encoding='utf-8') as fh:
        content = fh.read()
    
    # Check if already has mobile responsive in style block
    if '/* ---- Mobile Responsive ---- */' in content:
        print(f'SKIP: {page} already has mobile styles')
        continue
    
    # Check if has </style> to inject before
    if '</style>' in content:
        content = content.replace('</style>', mobile_css_block + '</style>', 1)
        with open(filepath, 'w', encoding='utf-8') as fh:
            fh.write(content)
        print(f'FIXED: {page}')
    else:
        print(f'SKIP: {page} has no </style> tag')

print('\nDone!')
