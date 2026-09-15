/**
 * main.js — Global site initialization.
 */

function initPartnerShopLinks() {
  const partners = window.LCB_PARTNERS;
  if (!partners) return;

  document.querySelectorAll("[data-partner-shop]").forEach((link) => {
    const key = link.getAttribute("data-partner-shop");
    const url = partners[key]?.shopUrl?.trim();
    if (!url) return;

    link.href = url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initPartnerShopLinks();

  // Smooth scroll for in-page anchor links
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", (e) => {
      const targetId = anchor.getAttribute("href");
      if (targetId === "#") return;

      const target = document.querySelector(targetId);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });
});
