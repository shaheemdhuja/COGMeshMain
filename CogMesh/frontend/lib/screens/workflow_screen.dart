import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/runtime_provider.dart';
import '../widgets/dag_painter.dart';

class WorkflowScreen extends ConsumerWidget {
  const WorkflowScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final runtimeState = ref.watch(runtimeProvider);
    final promptController = TextEditingController(
      text: 'Perform OCR on lecture PDF, summarize text, translate to Spanish and generate MCQs.',
    );

    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Capability-Constrained Workflow Generator', style: Theme.of(context).textTheme.headlineMedium),
            const SizedBox(height: 24),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Natural Language Goal Input', style: Theme.of(context).textTheme.titleLarge),
                    const SizedBox(height: 12),
                    TextField(
                      controller: promptController,
                      maxLines: 2,
                      decoration: const InputDecoration(
                        border: OutlineInputBorder(),
                        hintText: 'Enter natural language goal...',
                      ),
                    ),
                    const SizedBox(height: 16),
                    ElevatedButton.icon(
                      onPressed: runtimeState.isLoading
                          ? null
                          : () {
                              ref.read(runtimeProvider.notifier).runEndToEndPipeline(promptController.text);
                            },
                      icon: runtimeState.isLoading
                          ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2))
                          : const Icon(Icons.play_arrow),
                      label: Text(runtimeState.isLoading ? 'Executing Pipeline...' : 'Generate & Run Workflow'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF00E5FF),
                        foregroundColor: Colors.black,
                        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
            DagVisualizerWidget(
              taskStates: runtimeState.context?.taskStates ?? {},
            ),
          ],
        ),
      ),
    );
  }
}
