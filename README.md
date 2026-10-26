# Holdwise – Investment Portfolio Tracker

Holdwise is a Django web application for tracking investment portfolios. You create portfolios, add holdings by ticker symbol, and the app shows what each position is worth today, how much you have gained or lost, and how much cash each portfolio holds. Prices for stocks, ETFs and crypto are fetched from Yahoo Finance via `yfinance`.

Django Basics Regular Exam project @ SoftUni.

---

## Features

- **Dashboard** – net worth (holdings + cash), total profit/loss, cash across all portfolios, best performer, a summary of every portfolio and the latest cash activity.
- **Portfolios** – create, view, edit and delete portfolios, each with a strategy and description.
- **Holdings** – add a holding by entering a ticker, number of shares and buy price. New tickers are looked up on Yahoo Finance automatically.
  - Buying a ticker you already hold in the same portfolio **merges** the positions and recalculates the weighted average buy price.
  - Optionally **pay from the portfolio's cash reserve** (blocked if there is not enough cash).
  - **Sell** part or all of a position; the proceeds are added to the cash reserve and the realised profit/loss is shown.
  - Edit (asset is read-only) or remove a holding.
- **Cash reserve** – deposit and withdraw cash, and see the full cash history (deposits, withdrawals, purchases and sale proceeds).
- **CSV export** – download a portfolio's holdings (shares, average buy price, last price, cost basis, market value, profit/loss and P/L %) plus its cash balance as a CSV file that opens in Excel or Google Sheets.
- **Assets overview** – everything you own combined across all portfolios: total shares, average cost, market value, profit/loss and P/L %, with portfolio-wide totals. Search, filter by type and sort by value or performance.
- **Asset detail** – live price, which portfolios hold the asset and which watchlists it is on.
- **Watchlists** – lists of assets you are keeping an eye on (including ones you do not own). Add assets by ticker and remove them again.
- **Live prices with caching** – prices are refreshed automatically when a page needs them, but only if the stored price is older than one minute. A **Refresh prices** button is available on the dashboard, the Assets page, every portfolio and every watchlist.

---

## Tech stack

| | |
|---|---|
| Language | Python 3.13 |
| Framework | Django 6.1 |
| Database | SQLite |
| Market data | yfinance (Yahoo Finance) |
| Front end | Django Template Engine, Bootstrap 5.3, Bootstrap Icons (loaded from CDN) |

---

## Setup

### Requirements

- Python 3.12 or newer
- Git
- An internet connection (for installing packages, loading Bootstrap from the CDN and fetching prices from Yahoo Finance)

### Installation

```bash
git clone https://github.com/gaydazhiev-aleksander/holdwise.git
cd holdwise
python -m venv .venv
```

Activate the virtual environment:

- **Windows (PowerShell):** `.venv\Scripts\activate`
- **macOS / Linux:** `source .venv/bin/activate`

Then install the dependencies, create the database and start the server:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open **http://127.0.0.1:8000** in your browser.

The application starts with an **empty database**. No fixtures or seed data are needed; everything is created through the interface.

### Environment variables

| Variable | Default | Description |
|---|---|---|
| `DJANGO_DEBUG` | `True` (when not set) | Set to `False` to turn debug mode off, e.g. to see the custom 404 page. |

No API keys or credentials are required. Yahoo Finance is accessed through `yfinance` without an account.

### Viewing the custom 404 page

Django only shows the custom 404 page when debug mode is off. `--insecure` keeps static files (CSS) working without debug mode.

**Windows (PowerShell):**
```powershell
$env:DJANGO_DEBUG="False"
python manage.py runserver --insecure
```

**macOS / Linux:**
```bash
DJANGO_DEBUG=False python manage.py runserver --insecure
```

Then open any unknown URL, e.g. http://127.0.0.1:8000/does-not-exist/. To turn debug mode back on, close the terminal or run `Remove-Item Env:DJANGO_DEBUG` (PowerShell) / `unset DJANGO_DEBUG` (macOS/Linux).

---

## Quick walkthrough

1. **Portfolios → New portfolio** – create e.g. "Long-term".
2. On the portfolio page, **Deposit / withdraw** – deposit some cash.
3. **Add holding** – enter `AAPL`, a number of shares and a buy price. Tick **Pay from cash reserve** to pay with the deposited cash.
4. Add `AAPL` again – the holding is merged and the average buy price recalculated.
5. **Sell** part of the position – the proceeds appear in the cash balance and in the **cash history**.
6. Click **Export CSV** on the portfolio page to download its holdings.
7. Open **Assets** to see everything you own combined, and the **Dashboard** for the overall picture.
8. **Watchlists → New watchlist**, then **Add asset** – e.g. `TSLA` – to watch an asset you do not own.

---

## Project structure

```
holdwise/
├── holdwise/            Project settings and root URL configuration
├── common/              Dashboard, About page and the custom template tag library
│   └── templatetags/holdwise_tags.py
├── assets/              Assets, Yahoo Finance integration, combined holdings overview
├── portfolios/          Portfolios, holdings, buying/selling and the cash reserve
├── watchlists/          Watchlists of assets
├── templates/           All templates (base, partials and one folder per app)
│   └── partials/        Navbar, footer, messages, form fields, refresh button, profit/loss
├── static/css/          Custom styles
├── manage.py
└── requirements.txt
```

### Apps and responsibilities

| App | Responsibility |
|---|---|
| `common` | Dashboard (home), About page, shared template filters and tags |
| `assets` | The `Asset` model, the Yahoo Finance service, price caching, the Assets overview and asset detail pages, the price refresh endpoint |
| `portfolios` | `Portfolio`, `Holding` and `CashMovement`; buying, merging and selling holdings; deposits, withdrawals and cash history |
| `watchlists` | `Watchlist` and adding/removing assets on a watchlist |

---

## Database design

| Model | Key fields | Relationships |
|---|---|---|
| **Asset** | ticker (unique, regex-validated), name, type, sector, currency, last price, price timestamp | — |
| **Portfolio** | name (unique, min. length), description, strategy | — |
| **Holding** | shares, average buy price | **Many-to-one** → Portfolio (cascade), **many-to-one** → Asset (protect) |
| **CashMovement** | type (deposit / withdrawal / purchase / sale proceeds), amount, note | **Many-to-one** → Portfolio (cascade) |
| **Watchlist** | name (unique, min. length), notes | **Many-to-many** ↔ Asset |

Design decisions:

- **One holding per asset per portfolio** is enforced by a `UniqueConstraint`; repeated buys are merged instead of creating duplicates.
- **`PROTECT` on Holding → Asset** prevents deleting an asset that is still held.
- **The cash balance is never stored.** It is calculated from the `CashMovement` ledger, so it can never get out of sync when movements are added. Amounts are always positive; the movement type decides the direction.
- **`DecimalField` is used for all money and share values** – never floats, to avoid rounding errors. Shares support 6 decimal places for fractional shares and crypto.
- **Combined positions are calculated in the database.** A custom `AssetQuerySet` uses `annotate()`, `Sum`, `Count`, `F` and `ExpressionWrapper` to compute total shares, cost, market value and profit/loss per asset across all portfolios.
- Queries use `select_related` and `prefetch_related` to avoid N+1 queries.

---

## Architecture highlights

- **Service layer** – business logic lives outside the views:
  - `MarketDataService` (`assets/services.py`) wraps `yfinance`, maps Yahoo quote types to asset types and converts prices to `Decimal`.
  - `HoldingService` (`portfolios/services.py`) handles buying (with merging and optional cash payment) and selling. Selling updates the holding and records the sale proceeds inside `transaction.atomic()`, so both writes succeed or fail together.
- **Custom exceptions** – `MarketDataError` with the subclasses `TickerNotFoundError` and `MarketDataUnavailableError`. The rest of the app never handles raw `yfinance` errors.
- **Graceful failure** – if Yahoo Finance is unreachable or rate-limiting, the last known price is shown and the page keeps working.
- **Price caching** – `Asset.refresh_price()` only contacts Yahoo Finance when the stored price is older than `PRICE_MAX_AGE` (1 minute), protecting against rate limits.
- **Custom manager and QuerySet** – `Asset.objects.get_or_fetch()`, `owned()`, `with_positions()`, `position_totals()` and `refresh_prices()`.
- **Dependency injection** – `refresh_price()` and `get_or_fetch()` accept an optional service, keeping the model loosely coupled to the data source.
- **Form inheritance** – `TickerLookupForm` holds the shared ticker validation and lookup. `AddHoldingForm` and `AddToWatchlistForm` inherit from it; `AddToWatchlistForm` overrides `clean_ticker()` and calls `super()` to add a duplicate check.
- **Safe redirects** – the refresh endpoint only redirects to URLs on the same host (`url_has_allowed_host_and_scheme`), preventing open redirects.
- **Race-safe asset creation** – if two requests try to create the same ticker at the same moment (e.g. a double-clicked form), `get_or_fetch()` catches the `IntegrityError` inside `transaction.atomic()` and returns the asset created by the other request.
- **CSV export** – `PortfolioExportView` streams the holdings into an `HttpResponse` with Python's `csv` module, using a `Content-Disposition: attachment` header and a `slugify`-based filename.

---

## Forms and validation

| Form | Type | Notable validation |
|---|---|---|
| `PortfolioForm` | ModelForm | Case-insensitive unique name, minimum length |
| `AddHoldingForm` | Form (inherits `TickerLookupForm`) | Ticker format, ticker must exist on Yahoo Finance, positive shares and price, enough cash when paying from the reserve, merged total cannot exceed the share limit |
| `HoldingForm` | ModelForm | **Asset field is disabled (read-only)**; positive shares and price |
| `SellHoldingForm` | Form | Cannot sell more shares than held; sale amount must fit the cash ledger; price pre-filled with the market price |
| `CashMovementForm` | ModelForm | Only deposit/withdrawal selectable; cannot withdraw more than the balance; minimum amount |
| `WatchlistForm` | ModelForm | Case-insensitive unique name, minimum length |
| `AddToWatchlistForm` | Form (inherits `TickerLookupForm`) | Ticker must exist; asset not already on the watchlist |
| `AssetFilterForm` | Form | Search, type filter, whitelisted sort options |

All forms use custom labels, help texts, placeholders and user-friendly error messages. Fields such as `portfolio` and timestamps are excluded from forms. Every delete goes through a confirmation page, and every successful form submission redirects with a success message.

---

## Pages

| URL | Page |
|---|---|
| `/` | Dashboard |
| `/about/` | About |
| `/assets/` | Assets overview (search, filter, sort) |
| `/assets/<ticker>/` | Asset detail |
| `/portfolios/` | Portfolio list |
| `/portfolios/create/` | New portfolio |
| `/portfolios/<id>/` | Portfolio detail |
| `/portfolios/<id>/edit/` | Edit portfolio |
| `/portfolios/<id>/delete/` | Delete portfolio (confirmation) |
| `/portfolios/<id>/export/` | Download holdings as CSV |
| `/portfolios/<id>/holdings/add/` | Add holding |
| `/portfolios/holdings/<id>/edit/` | Edit holding |
| `/portfolios/holdings/<id>/sell/` | Sell holding |
| `/portfolios/holdings/<id>/delete/` | Remove holding (confirmation) |
| `/portfolios/<id>/cash/` | Cash history |
| `/portfolios/<id>/cash/add/` | Deposit or withdraw |
| `/watchlists/` | Watchlist list |
| `/watchlists/create/` | New watchlist |
| `/watchlists/<id>/` | Watchlist detail |
| `/watchlists/<id>/edit/` | Edit watchlist |
| `/watchlists/<id>/delete/` | Delete watchlist (confirmation) |
| `/watchlists/<id>/assets/add/` | Add asset to watchlist |

Every page is reachable through the navigation bar or links on other pages, and every page includes the shared footer.

---

## Templates

- **`base.html`** – shared layout; every page extends it.
- **Partials** (`templates/partials/`) – navbar, footer, messages, form fields, refresh button and profit/loss display, reused across pages.
- **Built-in filters and tags** used include `url`, `include`, `with`, `for … empty`, `querystring`, `csrf_token`, `now`, `pluralize`, `truncatechars`, `default`, `timesince`, `date`, `linebreaksbr`, `floatformat`, `slice` and `length`.
- **Custom filters and tags** (`common/templatetags/holdwise_tags.py`):

| Name | Kind | Example output |
|---|---|---|
| `money` | filter | `$1,234.56`, `-$377.45` |
| `shares` | filter | `0.05` instead of `0.050000` |
| `signed_percent` | filter | `+12.35%` |
| `pl_class` | filter | CSS class for profit, loss or unknown |
| `profit_loss` | inclusion tag | Coloured, signed amount with optional percentage |

---

## Notes

- Market data comes from Yahoo Finance through the unofficial `yfinance` library. Prices may be delayed, and Yahoo occasionally rate-limits requests. When that happens, Holdwise keeps showing the last known price and displays a message instead of failing.
- All values are assumed to be in USD. Assets priced in other currencies (e.g. `SAP.DE` in EUR) are not converted.
- Prices are stored to 4 decimal places, so assets priced below $0.0001 (e.g. some cryptocurrencies) are not supported.
- Holdwise is a tracking tool, not investment advice.