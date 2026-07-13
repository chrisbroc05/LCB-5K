# LCB 5K Website

Official static website for the LCB 5K charity race, built with HTML5, CSS3, and vanilla JavaScript.

## Project Structure

```
website/
├── index.html          # Home page (hero, countdown, mission, impact, etc.)
├── signup.html         # Registration page (links to Google Form)
├── donate.html         # Donation & sponsorship page
├── faq.html            # FAQ with accordion
├── css/
│   ├── variables.css   # Brand colors, spacing, typography tokens
│   ├── base.css        # Global resets and defaults
│   ├── components.css  # Nav, footer, buttons, cards
│   ├── home.css        # Home page section styles
│   └── pages.css       # Signup, Donate, FAQ page styles
├── js/
│   ├── components.js   # Loads shared nav & footer
│   ├── countdown.js    # Live race-day countdown timer
│   ├── animations.js   # Scroll reveal & stat counters
│   ├── faq.js          # FAQ accordion
│   └── main.js         # Global utilities
├── components/
│   ├── nav.html        # Shared navigation (edit once, updates all pages)
│   └── footer.html     # Shared footer
└── assets/
    └── images/         # Logo, hero photo, social icons
```

## Local Development

Because nav/footer are loaded via JavaScript `fetch()`, you need a local server (not `file://`):

```bash
cd website
python3 -m http.server 8080
```

Then open http://localhost:8080

## Deploy on Render

1. Push this repo to GitHub
2. Create a new **Static Site** on Render
3. Set **Root Directory** to `website`
4. Set **Publish Directory** to `.` (or leave blank)
5. Connect your custom domain in Render settings

A `render.yaml` is included for blueprint-based deployment.

## Updating Each Year

- **Event date**: Update `RACE_DATE` in `js/countdown.js` and event text in `index.html`
- **Registration link**: Replace placeholder in `signup.html`
- **Donation links**: Replace Stripe placeholders in `donate.html`
- **Sponsor logos**: Replace `.sponsor-placeholder` divs in `index.html` with `<img>` tags
- **Impact stats**: Update `data-count` values in the impact section
- **Winners**: Update names in the podium section

## Future Pages (easy to add)

Create a new HTML file following the same pattern as `signup.html`:
- Include shared CSS/JS
- Set `data-page` on `<body>` for active nav highlighting
- Add link in `components/nav.html`

Planned: Memory Wall, Results, Gallery, Volunteer, Course Map

## Hidden Payment Flow (Post-Registration)

After participants complete the Google Form, send them to:

**`/payments/`** (e.g. `https://yourdomain.com/payments/`)

Flow:
1. **Step 1** — Select 1–6 adults (`payments/index.html`)
2. **Step 2** — Choose registration only or add a donation tier (`payments/checkout.html?adults=3`)

This section is **not in the main navigation** (`noindex` for search engines). Share the link in your Google Form confirmation message.

### Adding Stripe Links

Edit **`js/payments-config.js`** if registration payment links change. Each adult count (1–6) has 13 options: entry fee only, plus optional donations of $10, $25, $35, $50, $75, $100, $150, $200, $300, $400, $500, and $1,000.
