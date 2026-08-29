# Celestial Calculus

**Celestial Calculus** is a private, local-first Vedic astrology research workstation designed to run from one responsive web application across Windows and Android.

## Cross-device architecture

- **GitHub Pages** hosts the responsive/PWA frontend.
- **Supabase** provides optional account authentication and private cross-device synchronization for horoscope profiles.
- **Python + Swiss Ephemeris** provides the authoritative astronomical calculation API.
- **Indexed/local browser storage** keeps a device cache so recent records remain usable offline.
- The same account on phone and laptop sees the same synchronized profiles.

GitHub is the source/deployment layer, **not** the horoscope database. Horoscope data belongs in the protected Supabase database with Row Level Security.

## Implemented calculation/workstation features

- Swiss Ephemeris planetary calculations via pyswisseph
- Lahiri/Raman/Krishnamurti ayanamsa selection
- Sidereal Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu and Ketu
- Ascendant and whole-sign Vedic houses
- Planetary longitude, sign, degree, speed and retrograde status
- Nakshatra, pada, lord, Nadi, Gana, Yoni and related classifications
- Vedic aspects and conservative transparent yoga rules
- Vimshottari Mahadasha timeline
- D1 and configurable Varga calculations
- Profile database/cache and search
- Responsive chart dashboard and PWA shell
- PDF report generation
- JSON export
- Cross-device Supabase synchronization
- GitHub Pages deployment workflow
- Docker deployment for calculation API
- Automated engine/database smoke tests

## Local Windows development

```bash
pip install -r requirements.txt
python -m app.server
```

Open `http://127.0.0.1:8765`.

## Cloud deployment

Read `DEPLOYMENT.md` and run `supabase_schema.sql` in your Supabase SQL Editor. Configure the GitHub Actions secrets:

- `CC_API_BASE_URL`
- `CC_SUPABASE_URL`
- `CC_SUPABASE_ANON_KEY`

Then push to the `main` branch. The GitHub Pages workflow publishes the `web/` directory.

## Android

Open the published GitHub Pages URL in Chrome and install it from the browser menu using **Add to Home screen / Install app**. Sign in with the same account used on Windows. The PWA uses the same synchronized cloud records.

## Important security note

The calculation API receives birth data whenever a chart is calculated. For a truly private production deployment, serve the API over HTTPS and put it behind authenticated access (for example, a private network/VPN or a JWT-verifying gateway). Do not expose the development HTTP server directly to the public internet.

## Accuracy notes

Swiss Ephemeris is used for astronomical positions. The default Vedic house model is whole-sign; Swiss Ephemeris house data is retained as reference metadata. Advanced Nadi traditions, some Varga traditions, and some Yoga definitions have multiple competing rules, so these areas must remain modular and explicitly configurable rather than silently mixing traditions.
