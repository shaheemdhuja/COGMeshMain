import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/runtime_provider.dart';
import '../widgets/result_card.dart';

class ResultsScreen extends ConsumerWidget {
  const ResultsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final runtimeState = ref.watch(runtimeProvider);
    final results = runtimeState.context?.results ?? {};

    final ocrText = results.values.firstWhere((r) => r is Map && r.containsKey('text'), orElse: () => {})['text'] ?? '';
    final summaryText = results.values.firstWhere((r) => r is Map && r.containsKey('summary'), orElse: () => {})['summary'] ?? '';
    final translationText = results.values.firstWhere((r) => r is Map && r.containsKey('translated_text'), orElse: () => {})['translated_text'] ?? '';
    final mcqsData = results.values.firstWhere((r) => r is Map && r.containsKey('questions'), orElse: () => {})['questions'] ?? [];

    return Scaffold(
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Text('Task Output Artifacts & Results', style: Theme.of(context).textTheme.headlineMedium),
                const Spacer(),
                ElevatedButton.icon(
                  onPressed: results.isEmpty
                      ? null
                      : () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Exported results to demo/ directory')),
                          );
                        },
                  icon: const Icon(Icons.download),
                  label: const Text('Export Artifacts'),
                ),
              ],
            ),
            const SizedBox(height: 24),
            ResultCard(
              title: 'Optical Character Recognition (OCR)',
              content: ocrText.toString(),
              icon: Icons.document_scanner,
            ),
            ResultCard(
              title: 'Gemma Text Summarization',
              content: summaryText.toString(),
              icon: Icons.short_text,
            ),
            ResultCard(
              title: 'Neural Machine Translation',
              content: translationText.toString(),
              icon: Icons.translate,
            ),
            ResultCard(
              title: 'Multiple Choice Questions (MCQs)',
              content: const JsonEncoder.withIndent('  ').convert(mcqsData),
              icon: Icons.quiz,
            ),
          ],
        ),
      ),
    );
  }
}
