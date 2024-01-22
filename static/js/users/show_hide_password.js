document.addEventListener('DOMContentLoaded', function () {
    const translate = (key) => {
      const translations = {
        'ro': {
          'Show': 'Afișează',
          'Hide': 'Ascunde',
        },
      };

      const pathSegments = window.location.pathname.split('/');
      const languageCode = pathSegments[1] || 'ro';

      return translations[languageCode]?.[key] || key;
    };

    const initShowHidePassword = (passwordInputId, toggleButtonId, eyeIconId, toggleTextId) => {
        const passwordInput = document.getElementById(passwordInputId);
        const toggleButton = document.getElementById(toggleButtonId);
        const eyeIcon = document.getElementById(eyeIconId);
        const toggleText = document.getElementById(toggleTextId);

        if (passwordInput && toggleButton && eyeIcon && toggleText) {
            toggleButton.addEventListener('click', function () {
                if (passwordInput.type === 'password') {
                    passwordInput.type = 'text';
                    eyeIcon.classList.remove('fa-eye');
                    eyeIcon.classList.add('fa-eye-slash');
                    toggleText.textContent = translate('Hide');
                } else {
                    passwordInput.type = 'password';
                    eyeIcon.classList.remove('fa-eye-slash');
                    eyeIcon.classList.add('fa-eye');
                    toggleText.textContent = translate('Show');
                }
            });
        }
    };

    if (window.passwordInputId1Register) {
        initShowHidePassword(
            window.passwordInputId1Register,
            'togglePassword1',
            'eye-icon1',
            'toggleText1'
        );
    }

    if (window.passwordInputId2Register) {
        initShowHidePassword(
            window.passwordInputId2Register,
            'togglePassword2',
            'eye-icon2',
            'toggleText2'
        );
    }

    if (window.passwordInputIdLogIn) {
        initShowHidePassword(
            window.passwordInputIdLogIn,
            'togglePassword',
            'eye-icon',
            'toggleText'
        );
    }

    if (window.passwordInputId1NewChange) {
        initShowHidePassword(
            window.passwordInputId1NewChange,
            'toggleNewPassword1',
            'eye-icon-new1',
            'toggleTextNew1'
        );
    }

    if (window.passwordInputId2NewChange) {
        initShowHidePassword(
            window.passwordInputId2NewChange,
            'toggleNewPassword2',
            'eye-icon-new2',
            'toggleTextNew2'
        );
    }


});
