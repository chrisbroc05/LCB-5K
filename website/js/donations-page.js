/**
 * donations-page.js — Renders donation tier buttons on the Donate page.
 */

document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("donation-tiers");
  const donations = window.LCB_DONATIONS;

  if (!container || !donations) return;

  donations.forEach((tier, index) => {
    const a = document.createElement("a");
    a.href = tier.url;
    a.className = "donation-tier-btn" + (index === 2 ? " featured" : "");
    a.textContent = `$${tier.amount.toLocaleString()} Support`;
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    container.appendChild(a);
  });
});
