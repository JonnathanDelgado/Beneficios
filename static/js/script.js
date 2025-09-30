  // ===== FUNCIONES DEL SELECT PERSONALIZADO =====

  // Toggle para abrir/cerrar el select
  document.querySelector(".select-trigger").addEventListener("click", function() {
      document.querySelector(".custom-select").classList.toggle("open");
  });

  // Inicializar valores del select
  function initializeSelectValues() {
      const trigger = document.querySelector('.select-trigger span');
      
      // Siempre mostrar "Soy un proveedor" al inicio
      if (trigger) {
          trigger.textContent = "Soy un proveedor";
      }
      
      // Remover checked de todos los radios al inicio
      const allRadios = document.querySelectorAll('.option input[type="radio"]');
      allRadios.forEach(radio => {
          radio.checked = false;
      });
  }

  // Configurar eventos de los radio buttons
  function setupSelectOptions() {
      const options = document.querySelectorAll('.option input[type="radio"]');
      const trigger = document.querySelector('.select-trigger span');
      
      options.forEach(option => {
          option.addEventListener('change', function() {
              if (this.checked && trigger) {
                  // Remover checked de todos los otros radios
                  options.forEach(otherOption => {
                      if (otherOption !== this) {
                          otherOption.checked = false;
                      }
                  });
                  
                  const selectedText = this.closest('.option').querySelector('.text').textContent;
                  trigger.textContent = selectedText;
                  document.querySelector(".custom-select").classList.remove("open");
                  
                  console.log("Opción seleccionada - ID:", this.id, "Texto:", selectedText);
              }
          });
          
          // También manejar click en la opción completa
          const optionLabel = option.closest('.option');
          optionLabel.addEventListener('click', function(e) {
              // Prevenir que se active dos veces
              if (e.target !== option) {
                  // Remover checked de todos los otros radios
                  options.forEach(otherOption => {
                      otherOption.checked = false;
                  });
                  
                  // Seleccionar este radio
                  option.checked = true;
                  
                  // Actualizar el texto del trigger
                  const selectedText = option.closest('.option').querySelector('.text').textContent;
                  trigger.textContent = selectedText;
                  document.querySelector(".custom-select").classList.remove("open");
                  
                  console.log("Opción clickeada - ID:", option.id, "Texto:", selectedText);
              }
          });
      });
  }

  // Cerrar dropdown al hacer click fuera
  document.addEventListener("click", function(event) {
      const customSelect = document.querySelector(".custom-select");
      if (customSelect && !customSelect.contains(event.target)) {
          customSelect.classList.remove("open");
      }
  });

  // ===== FUNCIÓN DEL OJO DE CONTRASEÑA =====
  function setupPasswordToggle() {
      const passwordInput = document.getElementById("password");
      const eyeIcon = document.getElementById("eyeIcon");

      if (eyeIcon && passwordInput) {
          eyeIcon.addEventListener("click", function() {
              if (passwordInput.type === "password") {
                  passwordInput.type = "text";
                  eyeIcon.src = "/static/conten/eyeopen.png";
              } else {
                  passwordInput.type = "password";
                  eyeIcon.src = "/static/conten/eyeclose.svg";
              }
          });
      }
  }

  // ===== INICIALIZACIÓN AL CARGAR LA PÁGINA =====
  document.addEventListener("DOMContentLoaded", function() {
      initializeSelectValues();
      setupSelectOptions();
      setupPasswordToggle();
  });