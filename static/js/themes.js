const toggleTheme = () => {
  document.body.classList.toggle('dark-theme');
  const isDarkTheme = document.body.classList.contains('dark-theme');
  localStorage.setItem('theme', isDarkTheme ? 'dark' : 'light');
};

const storedTheme = localStorage.getItem('theme');
if (storedTheme === 'dark') {
  document.body.classList.add('dark-theme');
}