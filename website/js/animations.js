/**
 * animations.js — Scroll reveal and animated statistic counters.
 */

function initScrollReveal() {
  const reveals = document.querySelectorAll(".reveal");
  if (!reveals.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15, rootMargin: "0px 0px -40px 0px" }
  );

  reveals.forEach((el) => observer.observe(el));
}

function animateCounter(element, target, prefix = "", suffix = "") {
  const duration = 2000;
  const start = performance.now();

  function format(value) {
    return prefix + Math.floor(value).toLocaleString() + suffix;
  }

  function step(timestamp) {
    const progress = Math.min((timestamp - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    element.textContent = format(target * eased);

    if (progress < 1) {
      requestAnimationFrame(step);
    } else {
      element.textContent = prefix + target.toLocaleString() + suffix;
    }
  }

  requestAnimationFrame(step);
}

function initStatCounters() {
  const statNumbers = document.querySelectorAll("[data-count]");
  if (!statNumbers.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const el = entry.target;
          const target = parseFloat(el.dataset.count);
          const prefix = el.dataset.prefix || "";
          const suffix = el.dataset.suffix || "";
          animateCounter(el, target, prefix, suffix);
          observer.unobserve(el);
        }
      });
    },
    { threshold: 0.5 }
  );

  statNumbers.forEach((el) => observer.observe(el));
}

document.addEventListener("DOMContentLoaded", () => {
  initScrollReveal();
  initStatCounters();
});
