  document.querySelector(".select-trigger").addEventListener("click", function() {
    document.querySelector(".custom-select").classList.toggle("open");
  });


  document.addEventListener("DOMContentLoaded", function() {
    const passwordInput = document.getElementById("password");
    const eyeIcon = document.getElementById("eyeIcon");

    eyeIcon.addEventListener("click", function() {
      if (passwordInput.type === "password") {
        passwordInput.type = "text";
        eyeIcon.src = "/static/conten/eyeopen.png"; // ícono ojo abierto
      } else {
        passwordInput.type = "password";
        eyeIcon.src = "/static/conten/eyeclose.svg"; // ícono ojo cerrado
      }
    });
  });