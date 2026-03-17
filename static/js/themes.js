/* ═══════════════════════════════════════════════════════════
   FITSYNC THEME ENGINE v2 — JavaScript Controller
   Full visual identity switching with mini-dashboard previews.
   ═══════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  const THEMES = [
    {
      id: 'natural-clay',
      name: 'Natural Clay',
      emoji: '🌿',
      desc: 'Warm beige background, organic rounded cards',
      tags: ['Fraunces Serif', 'Rounded 20px', 'Warm Neutrals'],
      preview: {
        bg: '#FAF7F2',
        sidebar: '#FFFCF8',
        sidebarText: '#3D3834',
        card: '#FFFFFF',
        cardRadius: '12px',
        cardShadow: '0 2px 8px rgba(100,90,80,0.08)',
        cardBorder: 'none',
        accent: '#8FAF8F',
        accentLight: '#B8D0B8',
        secondary: '#C9A96E',
        text: '#1A1A1A',
        textSoft: '#5E5854',
        banner: 'linear-gradient(135deg, #2D2D2D, #4A3A2A)',
        bar1: '#8FAF8F', bar2: '#C9A96E',
        font: "'Fraunces', serif",
        headingStyle: 'normal',
        headingTransform: 'none',
      },
    },
    {
      id: 'midnight',
      name: 'Midnight',
      emoji: '🌙',
      desc: 'Pitch black with glowing electric blue borders',
      tags: ['Space Mono', 'Sharp 8px', 'Glow Borders'],
      preview: {
        bg: '#050508',
        sidebar: '#0A0A10',
        sidebarText: '#64748B',
        card: '#0F0F18',
        cardRadius: '4px',
        cardShadow: '0 0 0 1px rgba(59,130,246,0.2)',
        cardBorder: '1px solid rgba(59,130,246,0.15)',
        accent: '#3B82F6',
        accentLight: '#60A5FA',
        secondary: '#818CF8',
        text: '#E2E8F0',
        textSoft: '#64748B',
        banner: 'linear-gradient(135deg, #0A1628, #0F172A)',
        bar1: '#3B82F6', bar2: '#818CF8',
        font: "'Space Mono', monospace",
        headingStyle: 'normal',
        headingTransform: 'uppercase',
      },
    },
    {
      id: 'blossom-rose',
      name: 'Blossom Rose',
      emoji: '🌸',
      desc: 'Dark crimson with glowing pink gradient banner',
      tags: ['Playfair Italic', 'Rounded 18px', 'Rose Glow'],
      preview: {
        bg: '#1A0A10',
        sidebar: '#140810',
        sidebarText: '#D4A0B0',
        card: '#1F0E16',
        cardRadius: '10px',
        cardShadow: '0 2px 12px rgba(244,63,94,0.06)',
        cardBorder: '1px solid rgba(244,63,94,0.1)',
        accent: '#F43F5E',
        accentLight: '#FB7185',
        secondary: '#FDA4AF',
        text: '#FDE8EF',
        textSoft: '#A87080',
        banner: 'linear-gradient(135deg, #F43F5E, #BE123C, #881337)',
        bar1: '#F43F5E', bar2: '#FDA4AF',
        font: "'Playfair Display', serif",
        headingStyle: 'italic',
        headingTransform: 'none',
      },
    },
    {
      id: 'ocean-minimal',
      name: 'Ocean Minimal',
      emoji: '🌊',
      desc: 'Light blue background, dark navy sidebar, sharp edges',
      tags: ['DM Sans Thin', 'Zero Radius', 'Navy Sidebar'],
      preview: {
        bg: '#EFF6FF',
        sidebar: '#0F172A',
        sidebarText: '#94A3B8',
        card: '#FFFFFF',
        cardRadius: '0px',
        cardShadow: '0 1px 3px rgba(0,0,0,0.06)',
        cardBorder: '1px solid #CBD5E1',
        accent: '#0284C7',
        accentLight: '#38BDF8',
        secondary: '#06B6D4',
        text: '#0C1824',
        textSoft: '#547080',
        banner: 'linear-gradient(135deg, #0C2D48, #164E6E)',
        bar1: '#0284C7', bar2: '#06B6D4',
        font: "'DM Sans', sans-serif",
        headingStyle: 'normal',
        headingTransform: 'none',
      },
    },
    {
      id: 'charcoal',
      name: 'Charcoal',
      emoji: '⚫',
      desc: 'Cream background, black sidebar, brutal box-shadows',
      tags: ['Bebas Neue Caps', 'Zero Radius', 'Brutal Shadow'],
      preview: {
        bg: '#F5F0EB',
        sidebar: '#111111',
        sidebarText: '#A3A3A3',
        card: '#FFFFFF',
        cardRadius: '0px',
        cardShadow: '3px 3px 0px #111111',
        cardBorder: '2px solid #111111',
        accent: '#111111',
        accentLight: '#333333',
        secondary: '#84CC16',
        text: '#111111',
        textSoft: '#666666',
        banner: 'linear-gradient(135deg, #111111, #1A1A1A)',
        bar1: '#111111', bar2: '#84CC16',
        font: "'Bebas Neue', sans-serif",
        headingStyle: 'normal',
        headingTransform: 'uppercase',
      },
    },
    {
      id: 'lavender',
      name: 'Lavender',
      emoji: '💜',
      desc: 'Soft purple background, pill shapes, gradient banner',
      tags: ['Cormorant Italic', 'Pill 50px', 'Gradient Banner'],
      preview: {
        bg: '#F3EEFF',
        sidebar: '#FDFBFF',
        sidebarText: '#5B4A78',
        card: '#FFFFFF',
        cardRadius: '16px',
        cardShadow: '0 4px 16px rgba(139,92,246,0.06)',
        cardBorder: 'none',
        accent: '#8B5CF6',
        accentLight: '#A78BFA',
        secondary: '#C4B5FD',
        text: '#1E1530',
        textSoft: '#6E5D88',
        banner: 'linear-gradient(135deg, #7C3AED, #5B21B6, #4C1D95)',
        bar1: '#8B5CF6', bar2: '#C4B5FD',
        font: "'Cormorant Garamond', serif",
        headingStyle: 'italic',
        headingTransform: 'none',
      },
    },
    {
      id: 'sunset',
      name: 'Sunset',
      emoji: '🌅',
      desc: 'Rich editorial feel with warm amber and terracotta',
      tags: ['Libre Baskerville', 'Warm Amber', 'Orange Shadow'],
      preview: {
        bg: '#FFF7ED',
        sidebar: '#FFEDD5',
        sidebarText: '#7C2D12',
        card: '#FFFFFF',
        cardRadius: '16px',
        cardShadow: '0 8px 32px rgba(234,88,12,0.15)',
        cardBorder: 'none',
        accent: '#EA580C',
        accentLight: '#F97316',
        secondary: '#F59E0B',
        text: '#431407',
        textSoft: '#9A3412',
        banner: 'linear-gradient(135deg, #EA580C, #9A3412)',
        bar1: '#EA580C', bar2: '#F59E0B',
        font: "'Libre Baskerville', serif",
        headingStyle: 'normal',
        headingTransform: 'none'
      }
    },
    {
      id: 'noir',
      name: 'Noir',
      emoji: '🖤',
      desc: 'Off-white vintage look with sharp red offset shadows',
      tags: ['Libre Italic', 'Offset Shadow', 'Red Accent'],
      preview: {
        bg: '#F8F9FA',
        sidebar: '#FFFFFF',
        sidebarText: '#495057',
        card: '#FFFFFF',
        cardRadius: '2px',
        cardShadow: '2px 2px 0px #212529',
        cardBorder: '1px solid #DEE2E6',
        accent: '#E03131',
        accentLight: '#FF6B6B',
        secondary: '#343A40',
        text: '#212529',
        textSoft: '#868E96',
        banner: 'linear-gradient(135deg, #212529, #121415)',
        bar1: '#E03131', bar2: '#343A40',
        font: "'Libre Baskerville', serif",
        headingStyle: 'italic',
        headingTransform: 'uppercase'
      }
    },
    {
      id: 'forest',
      name: 'Forest',
      emoji: '🌲',
      desc: 'Deep forest black with sharp Syne headings and green accents',
      tags: ['Syne Bold', 'Deep Black', 'Green Accent'],
      preview: {
        bg: '#0A110D',
        sidebar: '#0E1A14',
        sidebarText: '#6EE7B7',
        card: '#12221A',
        cardRadius: '12px',
        cardShadow: '0 10px 30px rgba(0,0,0,0.5)',
        cardBorder: '1px solid rgba(16,185,129,0.2)',
        accent: '#10B981',
        accentLight: '#34D399',
        secondary: '#059669',
        text: '#ECFDF5',
        textSoft: '#A7F3D0',
        banner: 'linear-gradient(135deg, #065F46, #064E3B)',
        bar1: '#10B981', bar2: '#059669',
        font: "'Syne', sans-serif",
        headingStyle: 'normal',
        headingTransform: 'none'
      }
    },
    {
      id: 'terracotta',
      name: 'Terracotta',
      emoji: '🍂',
      desc: 'Sandy warm backgrounds with earthy Italian editorial vibes',
      tags: ['Fraunces Italic', 'Sandy Warm', 'Full Pill'],
      preview: {
        bg: '#F5ECE3',
        sidebar: '#FAF4EF',
        sidebarText: '#5A4634',
        card: '#FFFFFF',
        cardRadius: '20px',
        cardShadow: '0 8px 30px rgba(184,136,108,0.15)',
        cardBorder: 'none',
        accent: '#B8886C',
        accentLight: '#D1A38A',
        secondary: '#9B6D53',
        text: '#3E2A1A',
        textSoft: '#7D624B',
        banner: 'linear-gradient(135deg, #A87056, #804F3B)',
        bar1: '#B8886C', bar2: '#9B6D53',
        font: "'Fraunces', serif",
        headingStyle: 'italic',
        headingTransform: 'none'
      }
    }
  ];

  const STORAGE_KEY = 'fitsync-theme';
  let currentTheme = localStorage.getItem(STORAGE_KEY) || 'natural-clay';
  let previewTheme = currentTheme;

  function applyTheme(themeId) {
    document.documentElement.setAttribute('data-theme', themeId);
  }

  function commitTheme(themeId) {
    currentTheme = themeId;
    previewTheme = themeId;
    localStorage.setItem(STORAGE_KEY, themeId);
    applyTheme(themeId);
  }

  // ── Build mini dashboard SVG preview ──
  function buildMiniPreview(p) {
    const r = p.cardRadius;
    const isDark = isColorDark(p.bg);
    return `
      <div style="
        width:100%; height:100%;
        background:${p.bg};
        display:flex;
        position:relative;
        overflow:hidden;
        font-family:${p.font};
      ">
        <!-- Mini sidebar -->
        <div style="
          width:52px; height:100%;
          background:${p.sidebar};
          border-right:1px solid rgba(${isDark?'255,255,255':'0,0,0'},0.08);
          padding:8px 6px;
          display:flex; flex-direction:column; gap:5px;
          flex-shrink:0;
        ">
          <div style="width:16px;height:16px;background:${p.accent};border-radius:5px;margin:0 auto 6px;"></div>
          <div style="width:32px;height:5px;background:${p.accent};opacity:0.3;border-radius:2px;margin:0 auto;"></div>
          <div style="width:32px;height:5px;background:${p.sidebarText};opacity:0.15;border-radius:2px;margin:0 auto;"></div>
          <div style="width:32px;height:5px;background:${p.sidebarText};opacity:0.15;border-radius:2px;margin:0 auto;"></div>
          <div style="width:32px;height:5px;background:${p.sidebarText};opacity:0.15;border-radius:2px;margin:0 auto;"></div>
        </div>

        <!-- Mini main content -->
        <div style="flex:1;padding:8px 10px;overflow:hidden;">
          <!-- Mini heading -->
          <div style="
            font-size:8px;font-weight:700;color:${p.text};
            margin-bottom:5px; white-space:nowrap;
            font-style:${p.headingStyle};
            text-transform:${p.headingTransform};
            letter-spacing:${p.headingTransform === 'uppercase' ? '1px' : '0'};
          ">Good morning 🌿</div>

          <!-- Mini streak banner -->
          <div style="
            background:${p.banner};
            border-radius:${r};
            padding:5px 8px;
            margin-bottom:6px;
            display:flex;align-items:center;gap:5px;
          ">
            <span style="font-size:10px;">🔥</span>
            <div style="flex:1;">
              <div style="font-size:6px;color:white;font-weight:700;font-style:${p.headingStyle};text-transform:${p.headingTransform};">5-Session Streak</div>
              <div style="font-size:5px;color:rgba(255,255,255,0.8);">Keep going!</div>
            </div>
          </div>

          <!-- Mini stat cards row -->
          <div style="display:flex;gap:4px;margin-bottom:6px;">
            ${[p.accent, p.secondary, p.accentLight].map(c => `
              <div style="
                flex:1;
                background:${p.card};
                border-radius:${r};
                padding:5px;
                box-shadow:${p.cardShadow};
                ${p.cardBorder !== 'none' ? 'border:' + p.cardBorder + ';' : ''}
              ">
                <div style="width:10px;height:10px;border-radius:3px;background:${c};opacity:0.15;margin-bottom:3px;"></div>
                <div style="font-size:9px;font-weight:700;color:${p.text};font-family:${p.font};font-style:${p.headingStyle};text-transform:${p.headingTransform};">24</div>
                <div style="font-size:5px;color:${p.textSoft};">Metric</div>
              </div>
            `).join('')}
          </div>

          <!-- Mini chart bars -->
          <div style="display:flex;gap:3px;align-items:flex-end;height:22px;margin-bottom:2px;">
            ${[14,20,10,22,16,18,12].map((h,i) => `
              <div style="flex:1;height:${h}px;background:${i%2===0?p.bar1:p.bar2};border-radius:${parseInt(r)*0.3}px ${parseInt(r)*0.3}px 0 0;opacity:${0.6+i*0.05};"></div>
            `).join('')}
          </div>
        </div>
      </div>
    `;
  }

  function isColorDark(hex) {
    if (hex.startsWith('#')) {
      const c = hex.substring(1);
      const r = parseInt(c.substring(0,2),16);
      const g = parseInt(c.substring(2,4),16);
      const b = parseInt(c.substring(4,6),16);
      return (r*0.299 + g*0.587 + b*0.114) < 128;
    }
    return false;
  }

  // ── Build panel ──
  function buildPanel() {
    const overlay = document.createElement('div');
    overlay.className = 'theme-panel-overlay';
    overlay.id = 'theme-panel-overlay';

    const panel = document.createElement('div');
    panel.className = 'theme-panel';

    panel.innerHTML = `
      <div class="theme-panel-header">
        <h2><i class="fa-solid fa-palette"></i> Dashboard Themes</h2>
        <button class="theme-panel-close" id="theme-close-btn" title="Close">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>
      <p class="theme-panel-subtitle">
        Each theme is a completely different visual identity — fonts, shapes, shadows, and layouts. Click to preview live.
      </p>
      <div class="theme-grid" id="theme-grid"></div>
      <div class="theme-panel-footer">
        <button class="theme-btn-cancel" id="theme-cancel-btn">Cancel</button>
        <button class="theme-btn-apply" id="theme-apply-btn">
          <i class="fa-solid fa-check" style="margin-right:4px;font-size:12px"></i> Apply Theme
        </button>
      </div>
    `;

    const grid = panel.querySelector('#theme-grid');

    THEMES.forEach(t => {
      const card = document.createElement('div');
      card.className = 'theme-card' + (t.id === currentTheme ? ' active' : '');
      card.setAttribute('data-theme-id', t.id);

      const tagsHtml = t.tags.map(tag => `<span class="theme-tag">${tag}</span>`).join('');

      card.innerHTML = `
        <div class="theme-preview">${buildMiniPreview(t.preview)}</div>
        <div class="theme-card-info">
          <div class="theme-card-name">${t.emoji} ${t.name}</div>
          <div class="theme-card-desc">${t.desc}</div>
          <div class="theme-card-tags">${tagsHtml}</div>
          ${t.id === currentTheme ? '<div class="theme-current-label"><i class="fa-solid fa-circle" style="font-size:5px"></i> Current</div>' : ''}
        </div>
      `;

      card.addEventListener('click', () => {
        previewTheme = t.id;
        applyTheme(t.id);
        grid.querySelectorAll('.theme-card').forEach(c => {
          c.classList.remove('active');
          const label = c.querySelector('.theme-current-label');
          if (label) label.remove();
        });
        card.classList.add('active');
      });

      grid.appendChild(card);
    });

    overlay.appendChild(panel);
    document.body.appendChild(overlay);

    // Events
    const closeBtn = panel.querySelector('#theme-close-btn');
    const cancelBtn = panel.querySelector('#theme-cancel-btn');
    const applyBtn = panel.querySelector('#theme-apply-btn');

    function closePanel() {
      overlay.classList.remove('open');
      if (previewTheme !== currentTheme) {
        applyTheme(currentTheme);
        previewTheme = currentTheme;
      }
    }

    closeBtn.addEventListener('click', closePanel);
    cancelBtn.addEventListener('click', closePanel);
    overlay.addEventListener('click', e => {
      if (e.target === overlay) closePanel();
    });

    applyBtn.addEventListener('click', () => {
      commitTheme(previewTheme);
      overlay.classList.remove('open');
      showThemeToast(THEMES.find(t => t.id === previewTheme));
    });

    return overlay;
  }

  function showThemeToast(theme) {
    const toast = document.createElement('div');
    toast.style.cssText = `
      position:fixed; bottom:30px; right:30px;
      background:var(--t-card-bg,white);
      border-radius:var(--t-card-radius,14px);
      padding:14px 22px;
      box-shadow:0 10px 40px rgba(0,0,0,0.2);
      display:flex; align-items:center; gap:10px;
      z-index:10002;
      animation:slideUpToast 0.4s cubic-bezier(0.34,1.56,0.64,1);
      font-family:var(--t-font-body,'DM Sans'),sans-serif;
      border-left:4px solid var(--t-accent,#8FAF8F);
    `;
    toast.innerHTML = `
      <span style="font-size:22px">${theme.emoji}</span>
      <div>
        <div style="font-size:13px;font-weight:700;color:var(--t-charcoal,#1A1A1A)">Theme Applied</div>
        <div style="font-size:11px;color:var(--t-text-soft,#5E5854);font-weight:500">${theme.name} is now active</div>
      </div>
    `;

    if (!document.getElementById('toast-anim-style')) {
      const style = document.createElement('style');
      style.id = 'toast-anim-style';
      style.textContent = `
        @keyframes slideUpToast {
          from { transform:translateY(40px); opacity:0; }
          to { transform:translateY(0); opacity:1; }
        }
      `;
      document.head.appendChild(style);
    }

    document.body.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 0.4s ease';
      setTimeout(() => toast.remove(), 400);
    }, 3000);
  }

  function openThemePanel() {
    let overlay = document.getElementById('theme-panel-overlay');
    if (!overlay) {
      overlay = buildPanel();
    } else {
      const grid = overlay.querySelector('#theme-grid');
      grid.querySelectorAll('.theme-card').forEach(card => {
        const id = card.getAttribute('data-theme-id');
        card.classList.toggle('active', id === currentTheme);
        const label = card.querySelector('.theme-current-label');
        if (label) label.remove();
        if (id === currentTheme) {
          const l = document.createElement('div');
          l.className = 'theme-current-label';
          l.innerHTML = '<i class="fa-solid fa-circle" style="font-size:5px"></i> Current';
          card.querySelector('.theme-card-info').appendChild(l);
        }
      });
    }
    previewTheme = currentTheme;
    overlay.classList.add('open');
  }

  function init() {
    applyTheme(currentTheme);

    document.addEventListener('click', e => {
      const trigger = e.target.closest('#theme-trigger-btn, #theme-trigger-sidebar');
      if (trigger) {
        e.preventDefault();
        openThemePanel();
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  window.openThemePanel = openThemePanel;
})();
