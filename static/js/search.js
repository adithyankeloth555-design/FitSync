/* ═══════════════════════════════════════════════════════════
   FITSYNC DASHBOARD SEARCH
   Quick-search across all dashboard pages and features.
   Supports keyboard navigation (↑↓ Enter Esc) and Ctrl+K shortcut.
   ═══════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  // All searchable pages — label, url, icon, keywords, category
  const PAGES = [
    { label: 'Dashboard',        url: '/dashboard/user/', icon: 'fa-house',                  cat: 'Overview',  kw: 'home main overview' },
    { label: 'Progress',         url: '/progress/',       icon: 'fa-chart-line',             cat: 'Overview',  kw: 'stats analytics charts report' },
    { label: 'Attendance',       url: '/attendance/',      icon: 'fa-calendar-check',         cat: 'Overview',  kw: 'checkin streak sessions calendar' },
    { label: 'Workouts',         url: '/workout/',         icon: 'fa-dumbbell',               cat: 'Training',  kw: 'exercise gym routine plan training' },
    { label: 'Fitness Guides',   url: '/fitness-guides/',  icon: 'fa-book-open',              cat: 'Training',  kw: 'articles guides tips tutorial how-to' },
    { label: 'Workout Videos',   url: '/videos/',          icon: 'fa-play',                   cat: 'Training',  kw: 'video watch tutorial' },
    { label: 'Live Sessions',    url: '/live-session/',    icon: 'fa-video',                  cat: 'Training',  kw: 'live stream class session zoom meet' },
    { label: 'Diet Plan',        url: '/diet/',            icon: 'fa-utensils',               cat: 'Training',  kw: 'diet food meal plan eating' },
    { label: 'Nutrition',        url: '/nutrition/',       icon: 'fa-apple-whole',            cat: 'Training',  kw: 'calories protein carbs macros food water' },
    { label: 'Goals',            url: '/goals/',           icon: 'fa-bullseye',               cat: 'Training',  kw: 'target objective fitness goal deadline' },
    { label: 'Trainers',         url: '/trainers/',        icon: 'fa-user-tie',               cat: 'Training',  kw: 'coach trainer personal hire' },
    { label: 'BMI Tracker',      url: '/bmi/history/',     icon: 'fa-weight-scale',           cat: 'Wellness',  kw: 'bmi weight height body mass index' },
    { label: 'BMI Calculator',   url: '/bmi/calculator/',  icon: 'fa-calculator',             cat: 'Wellness',  kw: 'bmi calculate weight' },
    { label: 'AI Neural Hub',    url: '/ai-hub/',          icon: 'fa-robot',                  cat: 'Wellness',  kw: 'ai chatbot nova artificial intelligence' },
    { label: 'AI Workout Plan',  url: '/ai-workout/',      icon: 'fa-brain',                  cat: 'Wellness',  kw: 'ai generate workout plan' },
    { label: 'AI Diet Plan',     url: '/ai-diet/',         icon: 'fa-wand-magic-sparkles',    cat: 'Wellness',  kw: 'ai generate diet plan nutrition' },
    { label: 'Meal Scanner',     url: '/meal-scanner/',    icon: 'fa-camera',                 cat: 'Wellness',  kw: 'scan food photo camera calories' },
    { label: 'Exercise Detection', url: '/exercise-detection/', icon: 'fa-person-running',    cat: 'Wellness',  kw: 'detect exercise camera pose' },
    { label: 'Fitness Score',    url: '/fitness-score/',   icon: 'fa-ranking-star',           cat: 'Wellness',  kw: 'score rating fitness assessment' },
    { label: 'Fitness Assessment', url: '/fitness-assessment/', icon: 'fa-clipboard-list',    cat: 'Wellness',  kw: 'assessment test quiz evaluate' },
    { label: 'Community',        url: '/community/',       icon: 'fa-users',                  cat: 'Wellness',  kw: 'forum posts discuss social' },
    { label: 'Store',            url: '/store/',           icon: 'fa-bag-shopping',           cat: 'Wellness',  kw: 'shop buy products supplements' },
    { label: 'Cart',             url: '/store/cart/',      icon: 'fa-cart-shopping',          cat: 'Wellness',  kw: 'cart checkout shopping bag' },
    { label: 'Orders',           url: '/store/orders/',    icon: 'fa-box',                    cat: 'Wellness',  kw: 'orders purchase history' },
    { label: 'Messages',         url: '/messages/',        icon: 'fa-message',                cat: 'Wellness',  kw: 'chat message notification inbox' },
    { label: 'Membership',       url: '/membership/',      icon: 'fa-crown',                  cat: 'Account',   kw: 'subscription plan premium elite' },
    { label: 'Settings',         url: '/settings/',        icon: 'fa-gear',                   cat: 'Account',   kw: 'settings profile account password email' },
    { label: 'Achievements',     url: '/achievements/',    icon: 'fa-trophy',                 cat: 'Account',   kw: 'badges achievements rewards trophy' },
    { label: 'Help Center',      url: '/help/',            icon: 'fa-circle-question',        cat: 'Account',   kw: 'help support faq ticket' },
    { label: 'Change Theme',     url: '#theme',            icon: 'fa-palette',                cat: 'Account',   kw: 'theme appearance color dark light' },
  ];

  const searchInput = document.getElementById('dashboard-search');
  const searchResults = document.getElementById('search-results');
  const searchWrapper = document.getElementById('search-wrapper');

  if (!searchInput || !searchResults) return;

  let activeIndex = -1;

  function search(query) {
    if (!query.trim()) {
      searchResults.innerHTML = '';
      searchResults.classList.remove('open');
      activeIndex = -1;
      return;
    }

    const q = query.toLowerCase().trim();
    const filtered = PAGES.filter(p => {
      return p.label.toLowerCase().includes(q) ||
             p.cat.toLowerCase().includes(q) ||
             p.kw.includes(q);
    });

    if (filtered.length === 0) {
      searchResults.innerHTML = `
        <div class="search-empty">
          <i class="fa-solid fa-search" style="font-size:18px;color:var(--t-text-soft, #999);margin-bottom:6px;"></i>
          <div style="font-size:13px;font-weight:600;color:var(--t-text-mid, #555);">No results for "${query}"</div>
          <div style="font-size:11px;color:var(--t-text-soft, #999);margin-top:2px;">Try searching for pages like "workouts" or "goals"</div>
        </div>
      `;
      searchResults.classList.add('open');
      activeIndex = -1;
      return;
    }

    // Group by category
    const groups = {};
    filtered.forEach(p => {
      if (!groups[p.cat]) groups[p.cat] = [];
      groups[p.cat].push(p);
    });

    let html = '';
    let idx = 0;
    for (const cat of Object.keys(groups)) {
      html += `<div class="search-group-label">${cat}</div>`;
      groups[cat].forEach(p => {
        const hl = highlightMatch(p.label, q);
        html += `
          <a href="${p.url}" class="search-result-item" data-index="${idx}" data-url="${p.url}">
            <div class="search-result-icon"><i class="fa-solid ${p.icon}"></i></div>
            <div class="search-result-text">
              <div class="search-result-label">${hl}</div>
            </div>
            <i class="fa-solid fa-arrow-right search-result-arrow"></i>
          </a>
        `;
        idx++;
      });
    }

    searchResults.innerHTML = html;
    searchResults.classList.add('open');
    activeIndex = -1;

    // Click handler for theme
    searchResults.querySelectorAll('.search-result-item').forEach(item => {
      item.addEventListener('click', e => {
        const url = item.getAttribute('data-url');
        if (url === '#theme') {
          e.preventDefault();
          closeSearch();
          if (window.openThemePanel) window.openThemePanel();
        }
      });
    });
  }

  function highlightMatch(text, query) {
    const idx = text.toLowerCase().indexOf(query);
    if (idx === -1) return text;
    return text.substring(0, idx) +
           '<mark>' + text.substring(idx, idx + query.length) + '</mark>' +
           text.substring(idx + query.length);
  }

  function setActive(index) {
    const items = searchResults.querySelectorAll('.search-result-item');
    items.forEach(i => i.classList.remove('active'));
    if (index >= 0 && index < items.length) {
      items[index].classList.add('active');
      items[index].scrollIntoView({ block: 'nearest' });
      activeIndex = index;
    }
  }

  function closeSearch() {
    searchResults.innerHTML = '';
    searchResults.classList.remove('open');
    searchInput.value = '';
    searchInput.blur();
    activeIndex = -1;
  }

  // Input event
  searchInput.addEventListener('input', () => search(searchInput.value));

  // Keyboard nav
  searchInput.addEventListener('keydown', e => {
    const items = searchResults.querySelectorAll('.search-result-item');
    const count = items.length;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActive(activeIndex < count - 1 ? activeIndex + 1 : 0);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActive(activeIndex > 0 ? activeIndex - 1 : count - 1);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (activeIndex >= 0 && items[activeIndex]) {
        const url = items[activeIndex].getAttribute('data-url');
        if (url === '#theme') {
          closeSearch();
          if (window.openThemePanel) window.openThemePanel();
        } else {
          window.location.href = url;
        }
      }
    } else if (e.key === 'Escape') {
      closeSearch();
    }
  });

  // Click outside to close
  document.addEventListener('click', e => {
    if (!searchWrapper.contains(e.target)) {
      closeSearch();
    }
  });

  // Ctrl+K / Cmd+K shortcut
  document.addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      searchInput.focus();
      searchInput.select();
    }
  });

  // Focus styling
  searchInput.addEventListener('focus', () => {
    searchWrapper.classList.add('focused');
    if (searchInput.value.trim()) search(searchInput.value);
  });
  searchInput.addEventListener('blur', () => {
    setTimeout(() => searchWrapper.classList.remove('focused'), 200);
  });

})();
