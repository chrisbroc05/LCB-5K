/**
 * payments-pricing.js — Shared pricing helpers for the payment flow.
 */

function formatMoney(amount) {
  return `$${amount.toLocaleString()}`;
}

function getEntryFeeTotal(adults, config) {
  return adults * config.entryFeePerAdult;
}

function getPaymentTotal(adults, donation, config) {
  return getEntryFeeTotal(adults, config) + donation;
}

function formatEntryBreakdown(adults, config) {
  const fee = config.entryFeePerAdult;
  const total = getEntryFeeTotal(adults, config);
  const adultWord = adults === 1 ? "adult" : "adults";
  return `${adults} ${adultWord} × ${formatMoney(fee)} = ${formatMoney(total)} entry fee`;
}
