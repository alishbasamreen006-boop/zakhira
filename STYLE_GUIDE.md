# Zakhira Style Guide (v1)
Tagline: *Calculate with clarity. Give with confidence. Grow with barakah.*
All UI text is English. Only the logo shows the Urdu word ذخیرہ.

## 1. Colours (use `BColors`, never raw hex)
| Token | Hex | Use |
|---|---|---|
| emerald | #0B6E4F | Primary, links, active icons |
| emeraldDark | #064032 | Header start, text on gold |
| mint | #2FBF9B | Success, gradient end, primary in dark mode |
| gold | #D4A937 | Accent, focus borders, rings |
| goldLight | #F0CF70 | Gold gradient end |
| champagne | #F3E3B3 | Soft highlights, track colour |
| cream | #FBF7EE | Light background |
| surface | #FFFFFF | Cards (dark: #11302A) |
| charcoal | #1E2A27 | Body text |
| amber / coral | #F2A541 / #E4572E | Warning / error |
| darkBg | #0A1F1A | Dark background |

Gradients: header `emeraldDark → emerald → mint`; primary button `gold → goldLight`; hero card emerald gradient + 1px gold border + gold glow.
Contrast rule: text on gold is always emeraldDark. Never put gold text on cream (fails AA); use emerald.

## 2. Typography
- Headings: Poppins SemiBold/Bold. Body: Inter. Money and counters: Poppins with tabular figures (`AppTheme.number`).
- Scale: Display 32 · Headline 24 · Title 18 · Body 15 · Caption 12.
- Urdu calligraphy exists only as a logo SVG/PNG, never as live text.

## 3. Spacing, shape, elevation
- 4-pt scale: 4, 8, 12, 16, 24, 32. Screen padding 20.
- Radius: cards 22, hero 24, fields 18, buttons 28 (height 56), sheets 28.
- Shadows: two layers, emerald-tinted (see `softShadow`). Dark mode uses one deeper black shadow.
- Pattern: 8-point star at 5-8% white on gradients, 4% on empty areas.

## 4. Components (lib/core/widgets/widgets.dart)
`GoldButton` · `AppCard` · `GlassCard` · `GoldSegmented` · `ProgressRing` · `CountUp` · `SkeletonBox` · `EmptyState` · `StaggerIn` · `PatternBackground`.
Forms open in bottom sheets (drag handle). Inline validation under the field in coral. Every list has loading (skeleton), empty (EmptyState) and error states.

## 5. Motion
Page: fade/zoom ≤ 300 ms. Count-up 1000 ms easeOutCubic. Rings 900 ms. List stagger 70 ms per item (max 8). Indicator slide 260 ms. Confetti only for "Zakat paid" and "Goal reached". Light haptic on primary actions. Respect the system "reduce motion" setting.

## 6. Accessibility
Tap targets ≥ 48 px. Large-text mode scales to 1.25×. WCAG AA contrast. Every icon button and ring has a `Semantics` label. Do not rely on colour alone (pair with text/icon).

## 7. Icons and illustrations
- Icons: 2 px line, rounded caps, gold accent on the active detail. Phosphor or Lucide (both permissive licences) as the base set, custom for Gold, Silver, Inventory, Receivables, Debts.
- Illustrations: flat or soft semi-3D, emerald/gold/cream. People are faceless and modest. No real-person photos. No copyrighted logos; charity cards use initials in a coloured circle.
- Export SVG where possible; PNG at 1x/2x/3x otherwise. Keep each file under 150 KB.

## 8. Asset list (put in /assets)
**logo/** `logo_full.svg`, `logo_white.svg`, `logo_gold.svg`, `app_icon_fg.svg` + `app_icon_bg` (adaptive), `splash_logo.svg`
**lottie/** `splash_particles.json`, `confetti.json`, `onboarding_1..3.json` (optional)
**illustrations/** `onboard_assets.svg`, `onboard_calc.svg`, `onboard_path.svg`, `hero_funding.svg`, `hero_investor.svg`, `hero_invest.svg`, `hero_bc.svg`, `hero_goals.svg`, `hero_learn.svg`, `scam_shield.svg`, `empty_assets.svg`, `empty_payments.svg`, `empty_reminders.svg`, `empty_matches.svg`
**icons/** `cash`, `bank`, `gold`, `silver`, `shares`, `property`, `inventory`, `receivables`, `debts` (.svg)
**avatars/** `avatar_01..12.svg` (faceless)
Sources: generate custom, or unDraw / Storyset / LottieFiles (free licence). Record every credit in `docs/CREDITS.md`.

## 9. Build order
1. This style guide + theme + widgets (done).
2. Splash, Onboarding, Login/Register/OTP, Profile setup, Dashboard.
3. Asset Tracker, Gold Converter, Zakat Calculator, Explain.
4. Nisab & Rates, Payments, Reminders, Family, Fitrana.
5. Remaining screens.

## 10. Rules that apply to every screen
Zakat results: "For a final ruling, please confirm with a qualified scholar." Funding/investing: "This is not financial advice. Verify before you decide." The app never holds or moves money. Zakat rules, nisab and rates come from admin-managed tables, not constants. The calculator works offline.
