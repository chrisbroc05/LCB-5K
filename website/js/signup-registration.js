/**
 * signup-registration.js — Adult count selection and dynamic total on Sign Up page.
 */

document.addEventListener("DOMContentLoaded", () => {
  const grid = document.getElementById("signup-adult-count-grid");
  const totalEl = document.getElementById("signup-registration-total");
  const continueBtn = document.getElementById("signup-continue-payment");
  const config = window.LCB_PAYMENTS;

  if (!grid || !config) return;

  let selectedAdults = null;
  let selectedBtn = null;

  function renderTotal(adults) {
    const entryTotal = getEntryFeeTotal(adults, config);
    if (!totalEl) return;

    totalEl.hidden = false;
    totalEl.innerHTML =
      `<span class="payment-total-label">Registration Total:</span> ` +
      `<span class="payment-total-amount">${formatMoney(entryTotal)}</span>`;
  }

  function setSelectedAdults(adults, btn) {
    selectedAdults = adults;

    if (selectedBtn) {
      selectedBtn.classList.remove("is-selected");
    }

    selectedBtn = btn;
    selectedBtn.classList.add("is-selected");

    renderTotal(adults);

    if (continueBtn) {
      continueBtn.href = `/payments/checkout.html?adults=${adults}`;
      continueBtn.removeAttribute("aria-disabled");
      continueBtn.classList.remove("is-disabled");
    }
  }

  for (let adults = 1; adults <= 6; adults += 1) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "adult-count-btn";
    btn.setAttribute("aria-pressed", "false");
    btn.innerHTML = `
      <span class="adult-count-number">${adults}</span>
      <span class="adult-count-label">${adults === 1 ? "Adult" : "Adults"}</span>
    `;
    btn.addEventListener("click", () => {
      setSelectedAdults(adults, btn);
      btn.setAttribute("aria-pressed", "true");
      grid.querySelectorAll(".adult-count-btn").forEach((other) => {
        if (other !== btn) {
          other.setAttribute("aria-pressed", "false");
        }
      });
    });
    grid.appendChild(btn);
  }

  if (continueBtn) {
    continueBtn.addEventListener("click", (event) => {
      if (!selectedAdults) {
        event.preventDefault();
      }
    });
  }
});
