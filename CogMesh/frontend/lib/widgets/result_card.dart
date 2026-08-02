import 'package:flutter/material.dart';

class ResultCard extends StatelessWidget {
  final String title;
  final String content;
  final IconData icon;

  const ResultCard({
    super.key,
    required this.title,
    required this.content,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: const Color(0xFF00E5FF)),
                const SizedBox(width: 12),
                Text(
                  title,
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const Spacer(),
                IconButton(
                  icon: const Icon(Icons.copy, size: 20),
                  onPressed: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Copied $title to clipboard')),
                    );
                  },
                ),
              ],
            ),
            const Divider(color: Color(0xFF334155), height: 24),
            SelectableText(
              content.isEmpty ? 'No output generated.' : content,
              style: const TextStyle(color: Color(0xFFE2E8F0), fontSize: 14, height: 1.5),
            ),
          ],
        ),
      ),
    );
  }
}
