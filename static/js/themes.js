const toggleDarkTheme = () => {
  document.body.classList.toggle('dark-theme');
  const isDarkTheme = document.body.classList.contains('dark-theme');

  localStorage.setItem('theme', isDarkTheme ? 'dark' : 'light');
  
  updateThemeIcon(isDarkTheme);
};

const updateThemeIcon = (isDarkTheme) => {
  const themeIcon = document.getElementById('theme-icon');
  themeIcon.classList.toggle('fa-moon', !isDarkTheme);
  themeIcon.classList.toggle('fa-sun', isDarkTheme);
};

const initializeTheme = () => {
  const storedTheme = localStorage.getItem('theme');
  const isDarkTheme = storedTheme === 'dark';
  
  if (isDarkTheme) {
    document.body.classList.add('dark-theme');
  } else {
    document.body.classList.remove('dark-theme');
  }

  updateThemeIcon(isDarkTheme);

  const themeIcon = document.getElementById('theme-icon');
  themeIcon.style.display = 'inline';
};

document.addEventListener('DOMContentLoaded', initializeTheme);
document.getElementById('theme-icon').onclick = toggleDarkTheme;
