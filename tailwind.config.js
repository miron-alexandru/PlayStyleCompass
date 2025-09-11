/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './**/templates/**/*.html',
    './static/js/**/*.js',
  ],
  theme: {
    extend: {
      transitionDuration: {
        600: '600ms',
      },
    },
  },
  plugins: [],
}
