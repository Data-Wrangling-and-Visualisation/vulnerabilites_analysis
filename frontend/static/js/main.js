// frontend/static/js/main.js
document.addEventListener('DOMContentLoaded', () => {
    const root = document.documentElement;
    const btn  = document.getElementById('theme-toggle');
    const icon = document.getElementById('theme-icon');
  
    // 1) Выбор темы: из localStorage или системная
    const stored = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const useDark = stored === 'dark' || (stored === null && prefersDark);
  
    // 2) Устанавливаем
    if (useDark) {
      root.classList.add('dark');
      icon.textContent = '☀️';
    } else {
      root.classList.remove('dark');
      icon.textContent = '🌙';
    }
  
    // 3) Клик по кнопке — просто toggle класса dark
    btn.onclick = () => {
      const isNowDark = root.classList.toggle('dark');
      localStorage.setItem('theme', isNowDark ? 'dark' : 'light');
      icon.textContent = isNowDark ? '☀️' : '🌙';
    };
  
    // 4) Загрузка метрик
    (async () => {
      try {
        const stats = await fetch('/api/stats').then(r => r.json());
        document.getElementById('total-cve').textContent     = stats.total_count;
        document.getElementById('weekly-cve').textContent    = stats.weekly_count || 0;
        document.getElementById('high-critical').textContent =
          (stats.severity_stats || [])
            .filter(d => ['HIGH','CRITICAL'].includes(d.severity))
            .reduce((s, d) => s + d.count, 0);
        document.getElementById('last-update').textContent   =
          new Date(stats.last_update).toLocaleDateString('ru-RU');
      } catch (e) {
        console.error('Ошибка metрик:', e);
      }
    })();
  });
  