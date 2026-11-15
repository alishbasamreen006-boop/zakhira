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

## Flutter app
```
flutter create zakhira && cd zakhira
flutter pub add google_fonts flutter_svg lottie fl_chart hijri flutter_riverpod go_router local_auth flutter_secure_storage pdf printing
```
Copy `zakhira_app_main.dart` over `lib/main.dart`, then `flutter run`. (Flutter 3.27+.)
For the small prototype instead: `flutter pub add shared_preferences crypto` and copy `zakhira_prototype_main.dart` over `lib/main.dart`.

## Disclaimer
A calculation guide, not a fatwa. Confirm the final ruling with a qualified scholar. Investing and funding tools are educational, not financial advice.
