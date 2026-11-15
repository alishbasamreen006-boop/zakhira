// Zakhira app, step 1: theme, colours, reusable widgets and a style gallery.
// Single file: put this as lib/main.dart in your Flutter project.
import 'dart:math' as math;
import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';

const kAppName = 'Zakhira'; // change the app name here only

/// Zakhira colour tokens. Never hard-code colours in screens; use these.
class BColors {
  static const emerald = Color(0xFF0B6E4F);
  static const emeraldDark = Color(0xFF064032);
  static const mint = Color(0xFF2FBF9B);
  static const gold = Color(0xFFD4A937);
  static const goldLight = Color(0xFFF0CF70);
  static const champagne = Color(0xFFF3E3B3);
  static const cream = Color(0xFFFBF7EE);
  static const surface = Color(0xFFFFFFFF);
  static const charcoal = Color(0xFF1E2A27);
  static const amber = Color(0xFFF2A541);
  static const coral = Color(0xFFE4572E);
  static const success = mint;
  static const darkBg = Color(0xFF0A1F1A);
  static const darkSurface = Color(0xFF11302A);

  static const headerGradient = LinearGradient(
      colors: [emeraldDark, emerald, mint], begin: Alignment.topLeft, end: Alignment.bottomRight);
  static const goldGradient = LinearGradient(colors: [gold, goldLight]);
  static const heroGradient = LinearGradient(
      colors: [emeraldDark, emerald], begin: Alignment.topLeft, end: Alignment.bottomRight);
}

/// Spacing (4-pt scale), radii and shadows.
class BSpace {
  static const xs = 4.0, sm = 8.0, md = 12.0, lg = 16.0, xl = 24.0, xxl = 32.0;
  static const radiusCard = 22.0, radiusButton = 28.0, radiusField = 18.0;
  static const minTap = 48.0, buttonHeight = 56.0;
}

List<BoxShadow> softShadow(bool dark) => dark
    ? const [BoxShadow(color: Color(0x66000000), blurRadius: 18, offset: Offset(0, 8))]
    : const [
        BoxShadow(color: Color(0x14064032), blurRadius: 6, offset: Offset(0, 2)),
        BoxShadow(color: Color(0x1A064032), blurRadius: 24, offset: Offset(0, 12)),
      ];

/// Poppins for headings and numbers, Inter for body text.
class AppTheme {
  static TextTheme _text(Color c) {
    final body = GoogleFonts.interTextTheme().apply(bodyColor: c, displayColor: c);
    TextStyle? h(TextStyle? s, [FontWeight w = FontWeight.w600]) =>
        GoogleFonts.poppins(textStyle: s, fontWeight: w, color: c);
    return body.copyWith(
      displayLarge: h(body.displayLarge, FontWeight.w700),
      displayMedium: h(body.displayMedium, FontWeight.w700),
      headlineLarge: h(body.headlineLarge),
      headlineMedium: h(body.headlineMedium),
      headlineSmall: h(body.headlineSmall),
      titleLarge: h(body.titleLarge),
      titleMedium: h(body.titleMedium),
    );
  }

  /// Money and counters: Poppins with tabular figures so digits do not jump.
  static TextStyle number(double size, {Color? color, FontWeight w = FontWeight.w700}) =>
      GoogleFonts.poppins(
          fontSize: size, fontWeight: w, color: color, fontFeatures: const [FontFeature.tabularFigures()]);

  static ThemeData _base(bool dark) {
    final bg = dark ? BColors.darkBg : BColors.cream;
    final surf = dark ? BColors.darkSurface : BColors.surface;
    final ink = dark ? const Color(0xFFEAF3EF) : BColors.charcoal;
    final scheme = ColorScheme.fromSeed(
            seedColor: BColors.emerald, brightness: dark ? Brightness.dark : Brightness.light)
        .copyWith(primary: dark ? BColors.mint : BColors.emerald, secondary: BColors.gold,
            surface: surf, error: BColors.coral);
    OutlineInputBorder border(Color c, [double w = 1]) => OutlineInputBorder(
        borderRadius: BorderRadius.circular(BSpace.radiusField), borderSide: BorderSide(color: c, width: w));
    return ThemeData(
      useMaterial3: true,
      colorScheme: scheme,
      scaffoldBackgroundColor: bg,
      textTheme: _text(ink),
      appBarTheme: AppBarTheme(
          backgroundColor: Colors.transparent, elevation: 0, foregroundColor: ink, centerTitle: false),
      cardTheme: CardThemeData(
          color: surf, elevation: 0,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(BSpace.radiusCard))),
      inputDecorationTheme: InputDecorationTheme(
        filled: true, fillColor: surf,
        contentPadding: const EdgeInsets.symmetric(horizontal: 18, vertical: 18),
        border: border(Colors.transparent),
        enabledBorder: border(dark ? const Color(0xFF1F4A41) : const Color(0xFFE6DFC9)),
        focusedBorder: border(BColors.gold, 1.6),
        errorBorder: border(BColors.coral),
        focusedErrorBorder: border(BColors.coral, 1.6),
      ),
      bottomSheetTheme: BottomSheetThemeData(
          backgroundColor: surf, showDragHandle: true,
          shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(28)))),
      navigationBarTheme: NavigationBarThemeData(
          backgroundColor: surf, indicatorColor: BColors.champagne.withOpacity(dark ? .2 : .8), height: 68),
      snackBarTheme: SnackBarThemeData(
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16))),
      pageTransitionsTheme: const PageTransitionsTheme(builders: {
        TargetPlatform.android: ZoomPageTransitionsBuilder(),
        TargetPlatform.iOS: CupertinoPageTransitionsBuilder(),
      }),
    );
  }

  static final light = _base(false);
  static final dark = _base(true);
}

import 'dart:math' as math;

bool _dark(BuildContext c) => Theme.of(c).brightness == Brightness.dark;

/// Faint 8-point-star Islamic geometric pattern (use at 5-8% opacity).
class PatternPainter extends CustomPainter {
  final Color color;
  const PatternPainter(this.color);
  @override
  void paint(Canvas canvas, Size size) {
    final p = Paint()..color = color..style = PaintingStyle.stroke..strokeWidth = 1;
    const step = 44.0;
    final r = Rect.fromCenter(center: Offset.zero, width: 22, height: 22);
    for (double y = 0; y < size.height + step; y += step) {
      for (double x = 0; x < size.width + step; x += step) {
        canvas.save();
        canvas.translate(x, y);
        canvas.drawRect(r, p);
        canvas.rotate(math.pi / 4);
        canvas.drawRect(r, p);
        canvas.restore();
      }
    }
  }
  @override
  bool shouldRepaint(covariant PatternPainter old) => old.color != color;
}

class PatternBackground extends StatelessWidget {
  final Widget child;
  final Gradient? gradient;
  final double opacity;
  const PatternBackground({super.key, required this.child, this.gradient, this.opacity = .07});
  @override
  Widget build(BuildContext context) => DecoratedBox(
        decoration: BoxDecoration(gradient: gradient ?? BColors.headerGradient),
        child: CustomPaint(painter: PatternPainter(Colors.white.withOpacity(opacity)), child: child),
      );
}

/// Layered-shadow rounded card.
class AppCard extends StatelessWidget {
  final Widget child;
  final EdgeInsets padding;
  final VoidCallback? onTap;
  const AppCard({super.key, required this.child, this.padding = const EdgeInsets.all(16), this.onTap});
  @override
  Widget build(BuildContext context) {
    final d = _dark(context);
    return Container(
      decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.surface,
          borderRadius: BorderRadius.circular(BSpace.radiusCard),
          boxShadow: softShadow(d)),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
            borderRadius: BorderRadius.circular(BSpace.radiusCard),
            onTap: onTap,
            child: Padding(padding: padding, child: child)),
      ),
    );
  }
}

/// Glass hero card: emerald gradient, blur, thin gold glow border.
class GlassCard extends StatelessWidget {
  final Widget child;
  final EdgeInsets padding;
  const GlassCard({super.key, required this.child, this.padding = const EdgeInsets.all(20)});
  @override
  Widget build(BuildContext context) => Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(24),
          boxShadow: [BoxShadow(color: BColors.gold.withOpacity(.35), blurRadius: 22, spreadRadius: -4)],
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(24),
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 12, sigmaY: 12),
            child: Container(
              padding: padding,
              decoration: BoxDecoration(
                gradient: LinearGradient(colors: [
                  BColors.emerald.withOpacity(.92),
                  BColors.emeraldDark.withOpacity(.88),
                ], begin: Alignment.topLeft, end: Alignment.bottomRight),
                border: Border.all(color: BColors.gold.withOpacity(.6), width: 1),
                borderRadius: BorderRadius.circular(24),
              ),
              child: child,
            ),
          ),
        ),
      );
}

/// Primary gold gradient button (56 high) with haptics and loading state.
class GoldButton extends StatelessWidget {
  final String label;
  final VoidCallback? onPressed;
  final bool loading;
  final IconData? icon;
  const GoldButton({super.key, required this.label, this.onPressed, this.loading = false, this.icon});
  @override
  Widget build(BuildContext context) {
    final enabled = onPressed != null && !loading;
    return Semantics(
      button: true, label: label, enabled: enabled,
      child: Opacity(
        opacity: enabled ? 1 : .55,
        child: Container(
          height: BSpace.buttonHeight,
          decoration: BoxDecoration(
              gradient: BColors.goldGradient,
              borderRadius: BorderRadius.circular(BSpace.radiusButton),
              boxShadow: [BoxShadow(color: BColors.gold.withOpacity(.4), blurRadius: 16, offset: const Offset(0, 6))]),
          child: Material(
            color: Colors.transparent,
            child: InkWell(
              borderRadius: BorderRadius.circular(BSpace.radiusButton),
              onTap: enabled ? () { HapticFeedback.lightImpact(); onPressed!(); } : null,
              child: Center(
                child: loading
                    ? const SizedBox(width: 24, height: 24, child: CircularProgressIndicator(strokeWidth: 2.4, color: BColors.emeraldDark))
                    : Row(mainAxisSize: MainAxisSize.min, children: [
                        if (icon != null) ...[Icon(icon, color: BColors.emeraldDark), const SizedBox(width: 8)],
                        Text(label, style: const TextStyle(color: BColors.emeraldDark, fontWeight: FontWeight.w700, fontSize: 16)),
                      ]),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

/// Animated count-up for money and counters.
class CountUp extends StatelessWidget {
  final double value;
  final String prefix;
  final TextStyle? style;
  const CountUp({super.key, required this.value, this.prefix = 'Rs. ', this.style});
  static String fmt(double v) =>
      v.round().toString().replaceAllMapped(RegExp(r'(\d)(?=(\d{3})+$)'), (m) => '${m[1]},');
  @override
  Widget build(BuildContext context) => TweenAnimationBuilder<double>(
        tween: Tween(begin: 0, end: value),
        duration: const Duration(milliseconds: 1000),
        curve: Curves.easeOutCubic,
        builder: (_, v, __) => Text('$prefix${fmt(v)}', style: style ?? AppTheme.number(32, color: Colors.white)),
      );
}

/// Animated gold progress ring with optional centre widget.
class ProgressRing extends StatelessWidget {
  final double value; // 0..1
  final double size;
  final Widget? child;
  const ProgressRing({super.key, required this.value, this.size = 120, this.child});
  @override
  Widget build(BuildContext context) {
    final track = _dark(context) ? const Color(0xFF1F4A41) : BColors.champagne.withOpacity(.6);
    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0, end: value.clamp(0, 1)),
      duration: const Duration(milliseconds: 900),
      curve: Curves.easeOutCubic,
      builder: (_, v, __) => Semantics(
        label: 'Progress ${(v * 100).round()} percent',
        child: SizedBox(width: size, height: size,
            child: CustomPaint(painter: _RingPainter(v, track), child: Center(child: child))),
      ),
    );
  }
}

class _RingPainter extends CustomPainter {
  final double v;
  final Color track;
  _RingPainter(this.v, this.track);
  @override
  void paint(Canvas c, Size s) {
    final rect = (Offset.zero & s).deflate(9);
    final base = Paint()..style = PaintingStyle.stroke..strokeWidth = 14..strokeCap = StrokeCap.round;
    c.drawArc(rect, 0, math.pi * 2, false, base..color = track);
    final arc = Paint()
      ..style = PaintingStyle.stroke..strokeWidth = 14..strokeCap = StrokeCap.round
      ..shader = const SweepGradient(colors: [BColors.gold, BColors.goldLight], transform: GradientRotation(-math.pi / 2))
          .createShader(rect);
    c.drawArc(rect, -math.pi / 2, math.pi * 2 * v, false, arc);
  }
  @override
  bool shouldRepaint(covariant _RingPainter o) => o.v != v || o.track != track;
}

/// Segmented switch with a sliding gold indicator (2 or more labels).
class GoldSegmented extends StatelessWidget {
  final List<String> labels;
  final int index;
  final ValueChanged<int> onChanged;
  const GoldSegmented({super.key, required this.labels, required this.index, required this.onChanged});
  @override
  Widget build(BuildContext context) {
    final n = labels.length;
    return Container(
      height: 52,
      padding: const EdgeInsets.all(4),
      decoration: BoxDecoration(
          color: BColors.champagne.withOpacity(_dark(context) ? .12 : .55), borderRadius: BorderRadius.circular(26)),
      child: Stack(children: [
        AnimatedAlign(
          duration: const Duration(milliseconds: 260), curve: Curves.easeOutCubic,
          alignment: Alignment(n == 1 ? 0 : -1 + 2 * index / (n - 1), 0),
          child: FractionallySizedBox(
              widthFactor: 1 / n,
              child: Container(decoration: BoxDecoration(gradient: BColors.goldGradient, borderRadius: BorderRadius.circular(22)))),
        ),
        Row(children: [
          for (var i = 0; i < n; i++)
            Expanded(
              child: Semantics(
                button: true, selected: i == index, label: labels[i],
                child: GestureDetector(
                  behavior: HitTestBehavior.opaque,
                  onTap: () { HapticFeedback.selectionClick(); onChanged(i); },
                  child: Center(child: Text(labels[i], style: TextStyle(fontWeight: FontWeight.w600,
                      color: i == index ? BColors.emeraldDark : Theme.of(context).textTheme.bodyMedium?.color))),
                ),
              ),
            ),
        ]),
      ]),
    );
  }
}

/// Shimmer placeholder for loading states (no extra package needed).
class SkeletonBox extends StatefulWidget {
  final double? width;
  final double height;
  final double radius;
  const SkeletonBox({super.key, this.width, this.height = 16, this.radius = 12});
  @override
  State<SkeletonBox> createState() => _SkeletonState();
}

class _SkeletonState extends State<SkeletonBox> with SingleTickerProviderStateMixin {
  late final AnimationController _c = AnimationController(vsync: this, duration: const Duration(milliseconds: 1300))..repeat();
  @override
  void dispose() { _c.dispose(); super.dispose(); }
  @override
  Widget build(BuildContext context) {
    final base = _dark(context) ? const Color(0xFF173B33) : const Color(0xFFEFE8D4);
    final hi = _dark(context) ? const Color(0xFF21564A) : const Color(0xFFFBF7EE);
    return AnimatedBuilder(
      animation: _c,
      builder: (_, __) => Container(
        width: widget.width, height: widget.height,
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(widget.radius),
          gradient: LinearGradient(colors: [base, hi, base], stops: const [.1, .5, .9],
              begin: Alignment(-1 + 2 * _c.value, 0), end: Alignment(1 + 2 * _c.value, 0)),
        ),
      ),
    );
  }
}

/// Friendly empty state: illustration (or icon fallback), one line, one action.
class EmptyState extends StatelessWidget {
  final String title, message;
  final String? actionLabel, illustrationAsset; // e.g. assets/illustrations/empty_assets.svg
  final VoidCallback? onAction;
  final IconData icon;
  const EmptyState({super.key, required this.title, required this.message, this.actionLabel, this.onAction,
      this.illustrationAsset, this.icon = Icons.spa_outlined});
  @override
  Widget build(BuildContext context) => Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(mainAxisSize: MainAxisSize.min, children: [
            // When assets exist, swap this for SvgPicture.asset(illustrationAsset!, height: 160).
            Container(
              width: 120, height: 120,
              decoration: BoxDecoration(shape: BoxShape.circle, color: BColors.champagne.withOpacity(.5)),
              child: Icon(icon, size: 56, color: BColors.gold),
            ),
            const SizedBox(height: 20),
            Text(title, style: Theme.of(context).textTheme.titleLarge, textAlign: TextAlign.center),
            const SizedBox(height: 8),
            Text(message, textAlign: TextAlign.center, style: Theme.of(context).textTheme.bodyMedium),
            if (actionLabel != null) ...[const SizedBox(height: 24), SizedBox(width: 220, child: GoldButton(label: actionLabel!, onPressed: onAction))],
          ]),
        ),
      );
}

/// Staggered entrance for list items: wrap each item with its index.
class StaggerIn extends StatelessWidget {
  final int index;
  final Widget child;
  const StaggerIn({super.key, required this.index, required this.child});
  @override
  Widget build(BuildContext context) => TweenAnimationBuilder<double>(
        tween: Tween(begin: 0, end: 1),
        duration: Duration(milliseconds: 350 + 70 * math.min(index, 8)),
        curve: Curves.easeOutCubic,
        builder: (_, v, c) => Opacity(opacity: v, child: Transform.translate(offset: Offset(0, 24 * (1 - v)), child: c)),
        child: child,
      );
}

void main() => runApp(const ZakhiraApp());

class ZakhiraApp extends StatefulWidget {
  const ZakhiraApp({super.key});
  @override
  State<ZakhiraApp> createState() => _ZakhiraAppState();
}

class _ZakhiraAppState extends State<ZakhiraApp> {
  bool dark = false, largeText = false;
  @override
  Widget build(BuildContext context) => MaterialApp(
        title: kAppName,
        debugShowCheckedModeBanner: false,
        theme: AppTheme.light,
        darkTheme: AppTheme.dark,
        themeMode: dark ? ThemeMode.dark : ThemeMode.light,
        // Large-text accessibility mode applies app-wide.
        builder: (c, w) => MediaQuery(
            data: MediaQuery.of(c).copyWith(textScaler: TextScaler.linear(largeText ? 1.25 : 1.0)), child: w!),
        home: StyleGallery(
            dark: dark, largeText: largeText,
            onDark: (v) => setState(() => dark = v), onLarge: (v) => setState(() => largeText = v)),
      );
}

/// Preview of every component. Delete before release.
class StyleGallery extends StatefulWidget {
  final bool dark, largeText;
  final ValueChanged<bool> onDark, onLarge;
  const StyleGallery({super.key, required this.dark, required this.largeText, required this.onDark, required this.onLarge});
  @override
  State<StyleGallery> createState() => _GalleryState();
}

class _GalleryState extends State<StyleGallery> {
  int seg = 0;
  @override
  Widget build(BuildContext context) {
    final t = Theme.of(context).textTheme;
    return Scaffold(
      body: ListView(padding: EdgeInsets.zero, children: [
        PatternBackground(
          child: SafeArea(
            bottom: false,
            child: Padding(
              padding: const EdgeInsets.fromLTRB(20, 12, 20, 40),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text('Assalamu Alaikum', style: t.bodyMedium?.copyWith(color: Colors.white70)),
                Text('Welcome to $kAppName', style: t.headlineMedium?.copyWith(color: Colors.white)),
                const SizedBox(height: 18),
                GlassCard(
                  child: Row(children: [
                    Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                      Text('Zakat due', style: t.bodyMedium?.copyWith(color: Colors.white70)),
                      const CountUp(value: 187500),
                      const SizedBox(height: 6),
                      Text('Above nisab · 42 days left', style: t.bodySmall?.copyWith(color: BColors.champagne)),
                    ])),
                    const ProgressRing(value: .62, size: 92, child: Text('62%', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w700))),
                  ]),
                ),
              ]),
            ),
          ),
        ),
        Padding(
          padding: const EdgeInsets.all(20),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            GoldSegmented(labels: const ['Login', 'Register'], index: seg, onChanged: (i) => setState(() => seg = i)),
            const SizedBox(height: 16),
            const TextField(decoration: InputDecoration(labelText: 'Phone or email', prefixIcon: Icon(Icons.phone_outlined))),
            const SizedBox(height: 16),
            GoldButton(label: 'Continue', onPressed: () {}),
            const SizedBox(height: 16),
            AppCard(child: Row(children: [
              const SkeletonBox(width: 48, height: 48, radius: 24), const SizedBox(width: 12),
              const Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [SkeletonBox(height: 14), SizedBox(height: 8), SkeletonBox(width: 120, height: 12)])),
            ])),
            const SizedBox(height: 8),
            SwitchListTile(title: const Text('Dark mode'), value: widget.dark, onChanged: widget.onDark),
            SwitchListTile(title: const Text('Large text'), value: widget.largeText, onChanged: widget.onLarge),
            const EmptyState(title: 'No assets yet', message: 'Add your first asset to see your zakat.', actionLabel: 'Add asset'),
          ]),
        ),
      ]),
    );
  }
}
