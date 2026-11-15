# 🪙 Zakhira

Zakat, savings and halal growth companion. Calculate with clarity. Give with confidence. Grow with barakah.
Zakhira calculates, tracks and guides. It never holds or moves user money.

## Files in this repository
- `app.py`, `requirements.txt`, `config.toml`: Streamlit website
- `zakhira_app_main.dart`, `pubspec.yaml`: Flutter app (theme, widgets, style gallery)
- `zakhira_prototype_main.dart`: small working Flutter prototype
- `STYLE_GUIDE.md`: design system and asset list

## Website
```
pip install -r requirements.txt
streamlit run app.py
```
Optional theme: create a folder named `.streamlit` and put `config.toml` inside it.
Deploy on share.streamlit.io with main file `app.py`.

## Optional artwork (makes the website look like the mockup)
Put these image files next to `app.py` (or in an `assets` folder). PNG, JPG or WEBP all work. If a file is missing, a built-in drawing is used.
- `hero_bg`: wide green banner background (mosque skyline)
- `login_art`: square illustration for the login page
- `tile_e` (net worth), `tile_g` (zakat due), `tile_s` (gold + silver), `tile_b` (saved), `tile_r` (given): small transparent PNG icons

## Flutter app
```
flutter create zakhira && cd zakhira
flutter pub add google_fonts flutter_svg lottie fl_chart hijri flutter_riverpod go_router local_auth flutter_secure_storage pdf printing
```
Copy `zakhira_app_main.dart` over `lib/main.dart`, then `flutter run`. (Flutter 3.27+.)
For the small prototype instead: `flutter pub add shared_preferences crypto` and copy `zakhira_prototype_main.dart` over `lib/main.dart`.

## Disclaimer
A calculation guide, not a fatwa. Confirm the final ruling with a qualified scholar. Investing and funding tools are educational, not financial advice.
