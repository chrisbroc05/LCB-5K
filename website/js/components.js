/**
 * components.js — Loads shared nav and footer HTML into each page.
 * Keeps navigation in one place for easy yearly updates.
 */

async function loadComponent(elementId, filePath) {
  const target = document.getElementById(elementId);
  if (!target) return;

  try {
    const response = await fetch(filePath);
    if (!response.ok) throw new Error(`Failed to load ${filePath}`);
    target.innerHTML = await response.text();
  } catch (error) {
    console.error(error);
  }
}

function setActiveNavLink() {
  const page = document.body.dataset.page;
  if (!page) return;

  document.querySelectorAll(".nav-links a[data-page]").forEach((link) => {
    link.classList.toggle("active", link.dataset.page === page);
  });
}

function initMobileNav() {
  const toggle = document.querySelector(".nav-toggle");
  const links = document.querySelector(".nav-links");
  if (!toggle || !links) return;

  toggle.addEventListener("click", () => {
    const isOpen = links.classList.toggle("open");
    toggle.setAttribute("aria-expanded", isOpen);
  });

  links.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      links.classList.remove("open");
      toggle.setAttribute("aria-expanded", "false");
    });
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  await Promise.all([
    loadComponent("site-nav", "components/nav.html"),
    loadComponent("site-footer", "components/footer.html"),
  ]);

  setActiveNavLink();
  initMobileNav();
});
