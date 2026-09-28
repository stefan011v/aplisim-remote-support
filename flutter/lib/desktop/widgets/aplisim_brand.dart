import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class AplisimIdentity extends StatelessWidget {
  const AplisimIdentity({super.key});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 20, 12, 14),
      child: Row(
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(9),
            child: Image.asset('assets/icon.png', width: 36, height: 36),
          ),
          const SizedBox(width: 10),
          const Expanded(
            child: Text('aplisim',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.w600,
                    letterSpacing: -0.8)),
          ),
        ],
      ),
    );
  }
}

class AplisimHeader extends StatefulWidget {
  const AplisimHeader({super.key});

  @override
  State<AplisimHeader> createState() => _AplisimHeaderState();
}

class _AplisimHeaderState extends State<AplisimHeader> {
  late final Future<Map<String, dynamic>> _configuration = _loadConfiguration();

  Future<Map<String, dynamic>> _loadConfiguration() async {
    try {
      final value = jsonDecode(await rootBundle.loadString('assets/aplisim-build.json'));
      return value is Map<String, dynamic> ? value : <String, dynamic>{};
    } catch (_) {
      return <String, dynamic>{};
    }
  }

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final accent = dark ? const Color(0xFF64EBD5) : const Color(0xFF087F73);
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.fromLTRB(22, 18, 22, 16),
      decoration: BoxDecoration(
        color: dark ? const Color(0xFF112125) : const Color(0xFFF0F7F5),
        border: Border(bottom: BorderSide(color: accent.withOpacity(0.2))),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('APLISIM · REMOTE SUPPORT',
              style: TextStyle(color: accent, fontSize: 10,
                  fontWeight: FontWeight.w600, letterSpacing: 1.4)),
          const SizedBox(height: 8),
          const Text("We're here, wherever you are.",
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.w600)),
          const SizedBox(height: 8),
          FutureBuilder<Map<String, dynamic>>(
            future: _configuration,
            builder: (context, snapshot) {
              final config = snapshot.data;
              final configured = config?['mode'] == 'configured';
              return Text(
                configured
                    ? 'Your server: ${config?['server'] ?? ''}'
                    : 'Preview build · not connected to a server yet.',
                style: TextStyle(fontSize: 11,
                    color: Theme.of(context).textTheme.bodySmall?.color),
              );
            },
          ),
        ],
      ),
    );
  }
}
