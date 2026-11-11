/* Copy complete code blocks, preserving indentation and line breaks. */
(function () {
  "use strict";

  async function copyText(text) {
    if (window.isSecureContext && navigator.clipboard && navigator.clipboard.writeText) {
      try {
        await navigator.clipboard.writeText(text);
        return;
      } catch (_) {
        // Older browsers or denied Clipboard API: try the selection-based path.
      }
    }
    var active = document.activeElement;
    var field = document.createElement("textarea");
    field.value = text;
    field.readOnly = true;
    field.style.position = "fixed";
    field.style.left = "-9999px";
    field.style.top = "0";
    document.body.appendChild(field);
    try {
      field.focus({ preventScroll: true });
      field.select();
      field.setSelectionRange(0, field.value.length);
      if (!document.execCommand("copy")) {
        throw new Error("Copy was not accepted");
      }
    } finally {
      field.remove();
      if (active && typeof active.focus === "function") {
        active.focus({ preventScroll: true });
      }
    }
  }

  function installButtons() {
    document.querySelectorAll(".main-content pre").forEach(function (pre, index) {
      var code = pre.querySelector("code");
      if (!code || pre.dataset.copyReady === "true") return;
      pre.dataset.copyReady = "true";

      var shell = document.createElement("div");
      shell.className = "code-copy-shell";
      var toolbar = document.createElement("div");
      toolbar.className = "code-copy-toolbar";
      var status = document.createElement("span");
      status.className = "code-copy-status";
      status.setAttribute("role", "status");
      status.setAttribute("aria-live", "polite");
      status.setAttribute("aria-atomic", "true");
      var button = document.createElement("button");
      button.type = "button";
      button.className = "code-copy-button";
      button.textContent = "Copiar";
      button.setAttribute("aria-label", "Copiar código del bloque " + (index + 1));

      pre.parentNode.insertBefore(shell, pre);
      shell.appendChild(toolbar);
      shell.appendChild(pre);
      toolbar.appendChild(status);
      toolbar.appendChild(button);
      var resetTimer;
      button.addEventListener("click", async function () {
        window.clearTimeout(resetTimer);
        button.disabled = true;
        status.textContent = "";
        try {
          // Read the code, not the wrapper: do not copy the toolbar or its label.
          await copyText(code.textContent);
          button.textContent = "Copiado";
          status.textContent = "Código copiado.";
        } catch (_) {
          button.textContent = "Copiar";
          status.textContent = "No se pudo copiar. Selecciona el código y usa Ctrl+C.";
        } finally {
          button.disabled = false;
        }
        resetTimer = window.setTimeout(function () {
          button.textContent = "Copiar";
          status.textContent = "";
        }, 3500);
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", installButtons);
  } else {
    installButtons();
  }
})();
