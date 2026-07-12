/* ──────────────────────────────────────────────────────────────
   chrome.js — runtime page furniture for stone-theme runbooks.

   Wraps every .cmd block in a .code-panel with a header bar
   (language label left, ⧉ COPY right), moving the existing inline
   copy button into it. This means a runbook adopts the new code
   panel with zero edits to its code blocks — the markup written
   for the old theme still works.

   Language label: set data-lang on the .cmd to override.
   Defaults to "shell".
   ────────────────────────────────────────────────────────────── */

(function () {
  'use strict';

  function copyText(cmd, btn) {
    navigator.clipboard.writeText(cmd.innerText.trim()).then(function () {
      btn.textContent = '⧉ COPIED';
      btn.classList.add('copied');
      setTimeout(function () {
        btn.textContent = '⧉ COPY';
        btn.classList.remove('copied');
      }, 1800);
    });
  }

  function buildPanels() {
    document.querySelectorAll('.cmd').forEach(function (cmd) {
      if (cmd.closest('.code-panel')) return;

      var panel = document.createElement('div');
      panel.className = 'code-panel';
      cmd.parentNode.insertBefore(panel, cmd);

      var head = document.createElement('div');
      head.className = 'code-head';

      var lang = document.createElement('span');
      lang.className = 'code-lang';
      lang.textContent = cmd.dataset.lang || 'shell';
      head.appendChild(lang);

      /* Reuse the button already in the markup if there is one, so the
         old onclick="copy(id,this)" pages keep a working button either way. */
      var btn = cmd.querySelector('.copy-btn');
      if (btn) {
        btn.removeAttribute('onclick');
      } else {
        btn = document.createElement('button');
        btn.className = 'copy-btn';
      }
      btn.type = 'button';
      btn.textContent = '⧉ COPY';
      btn.addEventListener('click', function () { copyText(cmd, btn); });
      head.appendChild(btn);

      panel.appendChild(head);
      panel.appendChild(cmd);
    });
  }

  function bindSteps() {
    document.querySelectorAll('.step-header').forEach(function (h) {
      h.removeAttribute('onclick');
      h.addEventListener('click', function () {
        h.parentElement.classList.toggle('open');
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      buildPanels(); bindSteps();
    });
  } else {
    buildPanels(); bindSteps();
  }
})();
