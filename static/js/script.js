document.addEventListener("DOMContentLoaded", function() {
  // Esconde o popup após 3 segundos
  const popup = document.getElementById("popup");
  if (popup) {
    setTimeout(() => {
      popup.style.display = "none";
    }, 6000);
  }

  // Confirmação de exclusão
  const formExcluir = document.getElementById("formExcluir");
  if (formExcluir) {
    formExcluir.addEventListener("submit", function(e) {
      if (!confirm("Tem certeza?")) {
        e.preventDefault();
      }
    });
  }

  
 
});
function toggleAll(source) {
  let checkboxes = document.getElementsByName('ids');

  for (let i = 0; i < checkboxes.length; i++) {
      checkboxes[i].checked = source.checked;
  }
}