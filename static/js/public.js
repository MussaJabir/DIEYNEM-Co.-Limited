// Public site motion: subtle reveal-on-scroll + count-up stats.
// Pure IntersectionObserver, no dependencies; honours reduced-motion.
(function () {
  "use strict";
  var reduce =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function revealAll() {
    var els = document.querySelectorAll("[data-reveal]");
    if (!els.length) return;
    if (reduce || !("IntersectionObserver" in window)) {
      els.forEach(function (el) {
        el.classList.add("is-visible");
      });
      return;
    }
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var el = entry.target;
          var delay = el.getAttribute("data-reveal-delay");
          if (delay) el.style.transitionDelay = delay;
          el.classList.add("is-visible");
          io.unobserve(el);
        });
      },
      { threshold: 0.15 }
    );
    els.forEach(function (el) {
      io.observe(el);
    });
  }

  function countUpAll() {
    var els = document.querySelectorAll("[data-count-to]");
    if (!els.length) return;
    if (reduce || !("IntersectionObserver" in window)) {
      els.forEach(function (el) {
        el.textContent = el.getAttribute("data-count-to");
      });
      return;
    }
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var el = entry.target;
          io.unobserve(el);
          var target = parseInt(el.getAttribute("data-count-to"), 10) || 0;
          var duration = 1400;
          var startTime = null;
          function step(now) {
            if (!startTime) startTime = now;
            var p = Math.min((now - startTime) / duration, 1);
            var eased = 1 - Math.pow(1 - p, 3); // easeOutCubic
            el.textContent = Math.round(eased * target);
            if (p < 1) requestAnimationFrame(step);
            else el.textContent = target;
          }
          requestAnimationFrame(step);
        });
      },
      { threshold: 0.4 }
    );
    els.forEach(function (el) {
      io.observe(el);
    });
  }

  function progressBarsAll() {
    var els = document.querySelectorAll(".progress-bar");
    if (!els.length) return;
    if (reduce || !("IntersectionObserver" in window)) {
      els.forEach(function (el) {
        el.classList.add("is-filled");
      });
      return;
    }
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          io.unobserve(entry.target);
          entry.target.classList.add("is-filled");
        });
      },
      { threshold: 0.3 }
    );
    els.forEach(function (el) {
      io.observe(el);
    });
  }

  function run() {
    revealAll();
    countUpAll();
    progressBarsAll();
  }

  document.addEventListener("DOMContentLoaded", run);
  // Re-run after HTMX swaps so filtered/paged content still reveals and counts.
  // Harmless where HTMX is absent — the event simply never fires.
  document.addEventListener("htmx:afterSwap", run);
})();
