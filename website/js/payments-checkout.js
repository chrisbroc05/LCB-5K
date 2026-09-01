/**
 * payments-checkout.js — Renders donation tier buttons for selected adult count.
 */

function formatAdultLabel(count) {
  return count === 1 ? "1 Adult" : `${count} Adults`;
}

function formatOptionLabel(donation) {
  if (donation === 0) {
    return "Registration only";
  }
  return `Registration + ${formatMoney(donation)} support`;
}

function getConfirmModal() {
  return document.getElementById("payment-confirm-modal");
}

function openConfirmModal({ adults, entryTotal, donation, stripeUrl }) {
  const modal = getConfirmModal();
  const adultsEl = document.getElementById("confirm-adults");
  const entryEl = document.getElementById("confirm-entry");
  const donationRow = document.getElementById("confirm-donation-row");
  const donationEl = document.getElementById("confirm-donation");
  const totalEl = document.getElementById("confirm-total");
  const payLink = document.getElementById("confirm-pay-link");

  if (!modal || !payLink) return;

  if (adultsEl) adultsEl.textContent = formatAdultLabel(adults);
  if (entryEl) entryEl.textContent = formatMoney(entryTotal);

  if (donationRow && donationEl) {
    if (donation === 0) {
      donationRow.hidden = true;
    } else {
      donationRow.hidden = false;
      donationEl.textContent = formatMoney(donation);
    }
  }

  if (totalEl) {
    totalEl.textContent = formatMoney(entryTotal + donation);
  }

  payLink.href = stripeUrl;

  modal.hidden = false;
  modal.setAttribute("aria-hidden", "false");
  document.body.classList.add("payment-modal-open");
  payLink.focus();
}

function closeConfirmModal() {
  const modal = getConfirmModal();
  if (!modal) return;

  modal.hidden = true;
  modal.setAttribute("aria-hidden", "true");
  document.body.classList.remove("payment-modal-open");
}

function initConfirmModal() {
  const modal = getConfirmModal();
  if (!modal) return;

  modal.addEventListener("click", (event) => {
    if (event.target.closest("[data-dismiss='modal']")) {
      closeConfirmModal();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !modal.hidden) {
      closeConfirmModal();
    }
  });
}

function renderCheckoutPage() {
  const params = new URLSearchParams(window.location.search);
  const adults = parseInt(params.get("adults"), 10);
  const config = window.LCB_PAYMENTS;

  const titleEl = document.getElementById("checkout-title");
  const subtitleEl = document.getElementById("checkout-subtitle");
  const disclaimerEl = document.getElementById("pricing-disclaimer");
  const optionsEl = document.getElementById("payment-options");
  const errorEl = document.getElementById("checkout-error");

  if (!config || !titleEl || !optionsEl) return;

  if (!adults || adults < 1 || adults > 6) {
    if (errorEl) {
      errorEl.textContent = "Please go back and select how many adults you are signing up.";
      errorEl.hidden = false;
    }
    optionsEl.innerHTML = "";
    return;
  }

  const links = config.links[adults];
  const amounts = config.donationAmounts;
  const entryTotal = getEntryFeeTotal(adults, config);

  if (!links || links.length !== amounts.length) {
    if (errorEl) {
      errorEl.textContent = "Payment options are not configured correctly. Please contact the event organizer.";
      errorEl.hidden = false;
    }
    return;
  }

  titleEl.textContent = formatAdultLabel(adults);
  if (subtitleEl) {
    subtitleEl.textContent = `Registration total: ${formatMoney(entryTotal)}`;
  }

  if (disclaimerEl) {
    const fee = formatMoney(config.entryFeePerAdult);
    disclaimerEl.textContent =
      `${adults} ${adults === 1 ? "adult" : "adults"} at ${fee} each. Additional support is optional and added on top of the registration fee.`;
  }

  optionsEl.innerHTML = "";

  amounts.forEach((donation, index) => {
    const link = links[index];
    if (!link || !link.url) return;

    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "payment-option-btn" + (donation === 0 ? " primary" : "");
    btn.textContent = formatOptionLabel(donation);
    btn.addEventListener("click", () => {
      openConfirmModal({
        adults,
        entryTotal,
        donation,
        stripeUrl: link.url,
      });
    });
    optionsEl.appendChild(btn);
  });

  document.title = `Pay for ${formatAdultLabel(adults)} | LCB 5K 2026`;
}

document.addEventListener("DOMContentLoaded", () => {
  initConfirmModal();
  renderCheckoutPage();
});
