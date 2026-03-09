import os
import glob

html_files = glob.glob('templates/fitsync_app/*.html')

css_injection = """
    /* Mobile Responsive dynamically injected */
    @media (max-width: 1024px) {
        .sidebar { transform: translateX(-100%); transition: transform 0.3s ease; }
        .sidebar.open { transform: translateX(0); box-shadow: 10px 0 30px rgba(0,0,0,0.5); }
        .main-content, .main-area, .content-area { margin-left: 0 !important; padding: 1.5rem !important; padding-top: 4.5rem !important; }
        .page-header { flex-direction: column; align-items: flex-start; gap: 1rem; }
        .actions-bar { flex-direction: column; width: 100%; gap: 1rem; }
        .search-wrapper { max-width: 100%; width: 100%; }
        .premium-table { display: block; overflow-x: auto; white-space: nowrap; }
    }
    @media (max-width: 768px) {
        .main-content, .main-area, .content-area { padding: 1rem !important; padding-top: 4.5rem !important; }
        .page-title { font-size: 1.8rem; }
    }
"""

hamburger_html = """
    <!-- Mobile Hamburger Button -->
    <button class="hamburger-btn" id="hamburger-btn" aria-label="Toggle Menu">
        <i class="fa-solid fa-bars"></i>
    </button>

    <!-- Sidebar Overlay -->
    <div class="sidebar-overlay" id="sidebar-overlay"></div>
"""

js_script = """
<script>
    // Sidebar toggle for mobile
    const hamburgerBtn = document.getElementById('hamburger-btn');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    
    if (hamburgerBtn && sidebar && overlay) {
        const hamburgerIcon = hamburgerBtn.querySelector('i');

        function toggleSidebar() {
            sidebar.classList.toggle('open');
            overlay.classList.toggle('active');
            if (sidebar.classList.contains('open')) {
                hamburgerIcon.classList.replace('fa-bars', 'fa-xmark');
            } else {
                hamburgerIcon.classList.replace('fa-xmark', 'fa-bars');
            }
        }

        hamburgerBtn.addEventListener('click', toggleSidebar);
        overlay.addEventListener('click', toggleSidebar);
    }
</script>
"""

for file_path in html_files:
    if 'dashboard.html' in file_path:
        continue # Ignored
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if '<aside class="sidebar"' in content:
        orig = content

        # Add CSS at the end of the last </style>
        if css_injection.strip() not in content and '</style>' in content:
            parts = content.rsplit('</style>', 1)
            content = parts[0] + css_injection + '\n</style>' + parts[1]

        # Add JS script at the end of the last {% endblock %}
        if "toggleSidebar" not in content and '{% endblock %}' in content:
            parts = content.rsplit('{% endblock %}', 1)
            content = parts[0] + js_script + '\n{% endblock %}' + parts[1]

        # Add Hamburger HTML before the aside
        if 'id="hamburger-btn"' not in content:
            content = content.replace('<aside class="sidebar"', hamburger_html + '\n    <aside class="sidebar" id="sidebar"', 1)
        else:
            # Just add ID if missing
            content = content.replace('<aside class="sidebar"', '<aside class="sidebar" id="sidebar"', 1)

        # Update z-index
        content = content.replace('z-index: 100;', 'z-index: 1001; transition: transform 0.3s ease;')

        if orig != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated {file_path}")
