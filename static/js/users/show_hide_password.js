document.addEventListener("DOMContentLoaded", function () {
  const togglePasswords = (passwordIds, eyeIconIds, toggleTextIds) => {
    const passwordInputs = passwordIds
      .map(id => document.getElementById(id))
      .filter(el => el);
    const eyeIcons = eyeIconIds
      .map(id => document.getElementById(id))
      .filter(el => el);
    const toggleTexts = toggleTextIds
      .map(id => document.getElementById(id))
      .filter(el => el);

    if (!passwordInputs.length) return;

    const show = passwordInputs[0].type === "password";

    passwordInputs.forEach(input => {
      input.type = show ? "text" : "password";
    });

    eyeIcons.forEach(icon => {
      icon.classList.toggle("fa-eye", !show);
      icon.classList.toggle("fa-eye-slash", show);
    });

    toggleTexts.forEach(text => {
      text.textContent = translate(show ? "Hide" : "Show");
    });
  };

  const passwordIdsRegister = [
    window.passwordInputId1Register,
    window.passwordInputId2Register
  ];
  const eyeIconIdsRegister = ["eye-icon1", "eye-icon2"];
  const toggleTextIdsRegister = ["toggleText1", "toggleText2"];
  const toggleButtonsRegister = ["togglePassword1", "togglePassword2"]
    .map(id => document.getElementById(id))
    .filter(el => el);

  toggleButtonsRegister.forEach(button => {
    button.addEventListener("click", () => {
      togglePasswords(passwordIdsRegister, eyeIconIdsRegister, toggleTextIdsRegister);
    });
  });

  if (window.passwordInputIdLogIn) {
    initShowHidePassword(
      window.passwordInputIdLogIn,
      "togglePassword",
      "eye-icon",
      "toggleText"
    );
  }

  if (window.passwordInputId1NewChange) {
    initShowHidePassword(
      window.passwordInputId1NewChange,
      "toggleNewPassword1",
      "eye-icon-new1",
      "toggleTextNew1"
    );
  }

  if (window.passwordInputId2NewChange) {
    initShowHidePassword(
      window.passwordInputId2NewChange,
      "toggleNewPassword2",
      "eye-icon-new2",
      "toggleTextNew2"
    );
  }

  function initShowHidePassword(passwordInputId, toggleButtonId, eyeIconId, toggleTextId) {
    const passwordInput = document.getElementById(passwordInputId);
    const toggleButton = document.getElementById(toggleButtonId);
    const eyeIcon = document.getElementById(eyeIconId);
    const toggleText = document.getElementById(toggleTextId);

    if (passwordInput && toggleButton && eyeIcon && toggleText) {
      toggleButton.addEventListener("click", function () {
        if (passwordInput.type === "password") {
          passwordInput.type = "text";
          eyeIcon.classList.remove("fa-eye");
          eyeIcon.classList.add("fa-eye-slash");
          toggleText.textContent = translate("Hide");
        } else {
          passwordInput.type = "password";
          eyeIcon.classList.remove("fa-eye-slash");
          eyeIcon.classList.add("fa-eye");
          toggleText.textContent = translate("Show");
        }
      });
    }
  }
});
