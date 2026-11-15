import 'dart:convert';
import 'package:crypto/crypto.dart';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() => runApp(const Zakhira());

const em = Color(0xFF0B8A63), deep = Color(0xFF063F2E), gold = Color(0xFFE2B653);
String rs(num n) => 'Rs ${n.round().toString().replaceAllMapped(RegExp(r'(\d)(?=(\d{3})+$)'), (m) => '${m[1]},')}';

class Zakhira extends StatefulWidget {
  const Zakhira({super.key});
  @override
  State<Zakhira> createState() => _ZState();
}

class _ZState extends State<Zakhira> {
  Map<String, dynamic> d = {'user': null, 'assets': [], 'rem': [], 'dark': false, 'gold': 30000.0, 'silver': 350.0, 'zdate': ''};
  bool ready = false;
  late SharedPreferences sp;

  @override
  void initState() {
    super.initState();
    SharedPreferences.getInstance().then((s) {
      sp = s;
      final raw = s.getString('zakhira');
      if (raw != null) d = jsonDecode(raw);
      setState(() => ready = true);
    });
  }

  void save() {
    sp.setString('zakhira', jsonEncode(d));
    setState(() {});
  }

  double val(Map a) => a['amt'] * (a['type'] == 'Gold (g)' ? d['gold'] : a['type'] == 'Silver (g)' ? d['silver'] : 1);
  double get pos => d['assets'].where((a) => a['type'] != 'Debt').fold(0.0, (s, a) => s + val(a));
  double get debt => d['assets'].where((a) => a['type'] == 'Debt').fold(0.0, (s, a) => s + val(a));
  double get nisab => 612.36 * d['silver'];
  double get due => (pos - debt) >= nisab ? (pos - debt) * 0.025 : 0;

  @override
  Widget build(BuildContext c) {
    final scheme = (Brightness b) => ColorScheme.fromSeed(seedColor: em, brightness: b, secondary: gold);
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      scaffoldMessengerKey: msg,
      title: 'Zakhira',
      themeMode: d['dark'] ? ThemeMode.dark : ThemeMode.light,
      theme: ThemeData(useMaterial3: true, colorScheme: scheme(Brightness.light), scaffoldBackgroundColor: const Color(0xFFFBF7EA)),
      darkTheme: ThemeData(useMaterial3: true, colorScheme: scheme(Brightness.dark)),
      home: !ready ? const Scaffold(body: Center(child: CircularProgressIndicator())) : d['user'] == null ? auth() : shell(),
    );
  }

  // ---------- Login / Register ----------
  Widget auth() {
    final n = TextEditingController(), e = TextEditingController(), p = TextEditingController();
    bool reg = true;
    return StatefulBuilder(builder: (ctx, set) => Scaffold(
      body: Container(
        decoration: const BoxDecoration(gradient: LinearGradient(colors: [deep, em, gold], begin: Alignment.topLeft, end: Alignment.bottomRight)),
        child: SafeArea(child: Center(child: SingleChildScrollView(padding: const EdgeInsets.all(24), child: Column(children: [
          const Text('🪙', style: TextStyle(fontSize: 64)),
          const Text('Zakhira', style: TextStyle(fontSize: 38, fontWeight: FontWeight.w800, color: Colors.white)),
          const Text('Zakat, sona chandi aur paisa, sab ek jagah', style: TextStyle(color: Colors.white70)),
          const SizedBox(height: 22),
          Card(shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)), child: Padding(padding: const EdgeInsets.all(20), child: Column(children: [
            if (reg) TextField(controller: n, decoration: const InputDecoration(labelText: 'Full name', prefixIcon: Icon(Icons.person))),
            TextField(controller: e, decoration: const InputDecoration(labelText: 'Email', prefixIcon: Icon(Icons.email))),
            TextField(controller: p, obscureText: true, decoration: const InputDecoration(labelText: 'Password', prefixIcon: Icon(Icons.lock))),
            const SizedBox(height: 16),
            FilledButton(
              style: FilledButton.styleFrom(minimumSize: const Size.fromHeight(48)),
              onPressed: () {
                final h = sha256.convert(utf8.encode(p.text)).toString();
                if (reg) {
                  if (n.text.isEmpty || !e.text.contains('@') || p.text.length < 6) return snack('Enter name, valid email and 6+ char password');
                  d['user'] = {'name': n.text, 'email': e.text.toLowerCase(), 'pw': h};
                  d['zdate'] = DateTime.now().toIso8601String().substring(0, 10);
                } else {
                  final u = d['saved'];
                  if (u == null || u['email'] != e.text.toLowerCase() || u['pw'] != h) return snack('Email or password is incorrect');
                  d['user'] = u;
                }
                d['saved'] = d['user'];
                save();
              },
              child: Text(reg ? 'Create account' : 'Log in'),
            ),
            TextButton(onPressed: () => set(() => reg = !reg), child: Text(reg ? 'Have an account? Log in' : 'New here? Create account')),
          ]))),
        ])))),
      ),
    ));
  }

  final msg = GlobalKey<ScaffoldMessengerState>();
  void snack(String m) => msg.currentState?.showSnackBar(SnackBar(content: Text(m)));
  final navKey = GlobalKey();
  int tab = 0;

  // ---------- Main shell ----------
  Widget shell() {
    final pages = [home(), assets(), zakat(), reminders(), profile()];
    return Scaffold(
      key: navKey,
      body: SafeArea(child: pages[tab]),
      bottomNavigationBar: NavigationBar(selectedIndex: tab, onDestinationSelected: (i) => setState(() => tab = i), destinations: const [
        NavigationDestination(icon: Icon(Icons.home_rounded), label: 'Home'),
        NavigationDestination(icon: Icon(Icons.account_balance_wallet), label: 'Assets'),
        NavigationDestination(icon: Icon(Icons.calculate), label: 'Zakat'),
        NavigationDestination(icon: Icon(Icons.alarm), label: 'Reminders'),
        NavigationDestination(icon: Icon(Icons.person), label: 'Profile'),
      ]),
    );
  }

  Widget tile(String t, String v, String emoji, List<Color> g, {Color fg = Colors.white}) => Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(borderRadius: BorderRadius.circular(22), gradient: LinearGradient(colors: g)),
        child: Row(children: [
          Text(emoji, style: const TextStyle(fontSize: 34)),
          const SizedBox(width: 12),
          Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(t, style: TextStyle(color: fg.withOpacity(.85))), Text(v, style: TextStyle(color: fg, fontSize: 22, fontWeight: FontWeight.w800))])),
        ]),
      );

  DateTime nextZakat() {
    var z = DateTime.parse(d['zdate']);
    while (z.isBefore(DateTime.now())) z = z.add(const Duration(days: 354));
    return z;
  }

  Widget home() {
    final days = nextZakat().difference(DateTime.now()).inDays;
    final gs = d['assets'].where((a) => a['type'].toString().contains('(g)')).fold(0.0, (s, a) => s + val(a));
    return ListView(padding: const EdgeInsets.all(16), children: [
      Text('Assalamualaikum, ${d['user']['name'].split(' ')[0]}', style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w800)),
      const SizedBox(height: 14),
      tile('Net worth', rs(pos - debt), '💰', [deep, em]),
      const SizedBox(height: 10),
      tile('Zakat due', rs(due), '🕌', const [Color(0xFF8A6D2F), gold]),
      const SizedBox(height: 10),
      Row(children: [
        Expanded(child: tile('Gold + silver', rs(gs), '🪙', const [Color(0xFF9AA7AE), Color(0xFFEAEFF2)], fg: Colors.black87)),
        const SizedBox(width: 10),
        Expanded(child: tile('Next zakat', '$days days', '⏰', const [Color(0xFF7A2B3A), Color(0xFFE27D60)])),
      ]),
    ]);
  }

  static const types = ['Cash', 'Bank', 'Gold (g)', 'Silver (g)', 'Shares', 'Inventory', 'Receivable', 'Debt'];

  Widget assets() {
    final a = TextEditingController();
    String t = 'Cash';
    return StatefulBuilder(builder: (ctx, set) => ListView(padding: const EdgeInsets.all(16), children: [
      const Text('Assets and debts', style: TextStyle(fontSize: 24, fontWeight: FontWeight.w800)),
      DropdownButtonFormField(value: t, items: types.map((x) => DropdownMenuItem(value: x, child: Text(x))).toList(), onChanged: (v) => set(() => t = v!)),
      TextField(controller: a, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Amount (Rs, or grams)')),
      const SizedBox(height: 10),
      FilledButton(onPressed: () {
        final v = double.tryParse(a.text);
        if (v == null || v <= 0) return snack('Enter an amount above 0');
        d['assets'].add({'type': t, 'amt': v});
        save();
      }, child: const Text('Add')),
      ...List.generate(d['assets'].length, (i) {
        final x = d['assets'][i];
        return ListTile(title: Text(x['type']), subtitle: Text(rs(val(x))), trailing: IconButton(icon: const Icon(Icons.delete_outline), onPressed: () { d['assets'].removeAt(i); save(); }));
      }),
    ]));
  }

  Widget zakat() {
    final g = TextEditingController(text: '${d['gold']}'), s = TextEditingController(text: '${d['silver']}');
    return ListView(padding: const EdgeInsets.all(16), children: [
      const Text('Zakat calculator', style: TextStyle(fontSize: 24, fontWeight: FontWeight.w800)),
      TextField(controller: g, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Gold rate per gram (Rs)')),
      TextField(controller: s, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Silver rate per gram (Rs)')),
      TextButton(onPressed: () { d['gold'] = double.tryParse(g.text) ?? d['gold']; d['silver'] = double.tryParse(s.text) ?? d['silver']; save(); }, child: const Text('Update rates')),
      ListTile(title: const Text('Assets'), trailing: Text(rs(pos))),
      ListTile(title: const Text('Debts'), trailing: Text(rs(debt))),
      ListTile(title: const Text('Nisab (silver)'), trailing: Text(rs(nisab))),
      tile((pos - debt) >= nisab ? 'Zakat is due (2.5%)' : 'Below nisab, no zakat due', rs(due), '🕌', const [Color(0xFF8A6D2F), gold]),
      const Padding(padding: EdgeInsets.all(8), child: Text('This is a guide, not a fatwa. Confirm with your scholar.', style: TextStyle(fontSize: 12))),
    ]);
  }

  Widget reminders() {
    final t = TextEditingController();
    final nz = nextZakat();
    final list = List<Map>.from(d['rem'])..sort((a, b) => a['d'].compareTo(b['d']));
    return ListView(padding: const EdgeInsets.all(16), children: [
      const Text('Reminders', style: TextStyle(fontSize: 24, fontWeight: FontWeight.w800)),
      Card(color: gold.withOpacity(.25), child: ListTile(leading: const Text('🪙', style: TextStyle(fontSize: 26)), title: const Text('Zakat due date'), subtitle: Text('${nz.toString().substring(0, 10)} (${nz.difference(DateTime.now()).inDays} days left)'))),
      TextField(controller: t, decoration: const InputDecoration(labelText: 'New reminder (Fitrana, Qurbani saving...)')),
      FilledButton.icon(icon: const Icon(Icons.event), label: const Text('Pick date and add'), onPressed: () async {
        if (t.text.isEmpty) return snack('Write a title first');
        final p = await showDatePicker(context: navKey.currentContext!, firstDate: DateTime.now(), lastDate: DateTime.now().add(const Duration(days: 1500)), initialDate: DateTime.now());
        if (p != null) { d['rem'].add({'t': t.text, 'd': p.toIso8601String().substring(0, 10)}); save(); }
      }),
      ...list.map((r) {
        final left = DateTime.parse(r['d']).difference(DateTime.now()).inDays + 1;
        return Card(child: ListTile(
          leading: Icon(Icons.alarm, color: left < 0 ? Colors.red : left <= 7 ? Colors.orange : em),
          title: Text(r['t']), subtitle: Text('${r['d']} (${left < 0 ? 'overdue' : '$left days left'})'),
          trailing: IconButton(icon: const Icon(Icons.check_circle_outline), onPressed: () { d['rem'].remove(r); save(); }),
        ));
      }),
    ]);
  }

  Widget profile() => ListView(padding: const EdgeInsets.all(16), children: [
        Center(child: CircleAvatar(radius: 44, backgroundColor: em, child: Text(d['user']['name'][0].toUpperCase(), style: const TextStyle(fontSize: 34, color: Colors.white)))),
        Center(child: Text(d['user']['name'], style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w800))),
        SwitchListTile(title: const Text('Dark mode'), value: d['dark'], onChanged: (v) { d['dark'] = v; save(); }),
        ListTile(leading: const Icon(Icons.logout), title: const Text('Log out'), onTap: () { d['user'] = null; save(); }),
      ]);
}
