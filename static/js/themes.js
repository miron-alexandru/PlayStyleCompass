const updateChatBackgroundColors = (isDarkTheme) => {
  const chatMessages = document.querySelector(".chat-messages");
  const form = document.querySelector("form");
  const chatContainer = document.querySelector(".chat-container");

  if (chatMessages && form && chatContainer) {
    if (isDarkTheme) {
      const darkThemeColor = "#2a2a2a";
      chatMessages.style.backgroundColor = darkThemeColor;
      form.style.backgroundColor = darkThemeColor;
      chatContainer.style.backgroundColor = darkThemeColor;
    } else {
      const savedColor = localStorage.getItem("chatBackgroundColor");
      const defaultColor = savedColor || "#e6f7ff";
      chatMessages.style.backgroundColor = defaultColor;
      form.style.backgroundColor = defaultColor;
      chatContainer.style.backgroundColor = defaultColor;
    }
  }
};

const toggleDarkTheme = () => {
  document.body.classList.toggle("dark-theme");
  const isDarkTheme = document.body.classList.contains("dark-theme");

  localStorage.setItem("theme", isDarkTheme ? "dark" : "light");

  updateChatBackgroundColors(isDarkTheme);

  updateThemeIcon(isDarkTheme);
  updateLogoImage(isDarkTheme);
};

const updateThemeIcon = (isDarkTheme) => {
  const themeIcon = document.getElementById('theme-icon');
  themeIcon.classList.toggle('fa-moon', !isDarkTheme);
  themeIcon.classList.toggle('fa-sun', isDarkTheme);
};

const updateLogoImage = (isDarkTheme) => {
  const logoImage = document.getElementById('logo-image');
  const lightSrc = logoImage.getAttribute('data-light-src');
  const darkSrc = logoImage.getAttribute('data-dark-src');
  logoImage.src = isDarkTheme ? darkSrc : lightSrc;
  logoImage.style.visibility = 'visible';
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
  updateLogoImage(isDarkTheme);

  const themeIcon = document.getElementById('theme-icon');
  themeIcon.style.display = 'inline';
};

document.addEventListener('DOMContentLoaded', initializeTheme);
document.getElementById('theme-icon').onclick = toggleDarkTheme;
