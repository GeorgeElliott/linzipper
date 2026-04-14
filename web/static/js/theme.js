const html = document.documentElement;
const toggleBtn = document.getElementById('themeToggle');

const storedTheme = localStorage.getItem('theme');
const mql = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)');
const prefersDark = mql ? mql.matches : false;

if (storedTheme === 'dark' || (!storedTheme && prefersDark)) {
    html.classList.add('dark-mode');
    toggleBtn.textContent = '☀️ Light Mode';
} else {
    toggleBtn.textContent = '🌙 Dark Mode';
}

toggleBtn.addEventListener('click', () => {
    html.classList.toggle('dark-mode');
    const isDark = html.classList.contains('dark-mode');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    toggleBtn.textContent = isDark ? '☀️ Light Mode' : '🌙 Dark Mode';
});

if (mql) {
    const systemChangeHandler = (e) => {
        if (!localStorage.getItem('theme')) {
            if (e.matches) {
                html.classList.add('dark-mode');
                toggleBtn.textContent = '☀️ Light Mode';
            } else {
                html.classList.remove('dark-mode');
                toggleBtn.textContent = '🌙 Dark Mode';
            }
        }
    };
    if (mql.addEventListener) {
        mql.addEventListener('change', systemChangeHandler);
    } else if (mql.addListener) {
        mql.addListener(systemChangeHandler);
    }
}
