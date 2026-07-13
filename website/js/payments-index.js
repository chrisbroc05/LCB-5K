/**
 * payments-index.js — Step 1 adult count buttons.
 */

document.addEventListener("DOMContentLoaded", () => {
  const grid = document.getElementById("adult-count-grid");
  const config = window.LCB_PAYMENTS;
  if (!grid || !config) return;

  for (let adults = 1; adults <= 6; adults += 1) {
    const btn = document.createElement("a");
    btn.href = `/payments/checkout.html?adults=${adults}`;
    btn.className = "adult-count-btn";
    btn.innerHTML = `
      <span class="adult-count-number">${adults}</span>
      <span class="adult-count-label">${adults === 1 ? "Adult" : "Adults"}</span>
    `;
    grid.appendChild(btn);
  }
});
