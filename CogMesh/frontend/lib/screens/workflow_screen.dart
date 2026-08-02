import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/runtime_provider.dart';
import '../widgets/dag_painter.dart';

class WorkflowScreen extends ConsumerStatefulWidget {
  const WorkflowScreen({super.key});

  @override
  ConsumerState<WorkflowScreen> createState() => _WorkflowScreenState();
}

class _WorkflowScreenState extends ConsumerState<WorkflowScreen> {
  late final TextEditingController _promptController;
  late final TextEditingController _filePathController;

  @override
  void initState() {
    super.initState();
    _promptController = TextEditingController(
      text: 'Perform OCR on lecture PDF, summarize text, translate to Spanish and generate MCQs.',
    );
    _filePathController = TextEditingController();
  }

  @override
  void dispose() {
    _promptController.dispose();
    _filePathController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final runtimeState = ref.watch(runtimeProvider);

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
                      controller: _promptController,
                      maxLines: 2,
                      decoration: const InputDecoration(
                        border: OutlineInputBorder(),
                        hintText: 'Enter natural language goal...',
                      ),
                    ),
                    const SizedBox(height: 16),
                    Text('Optional PDF / Image Document File Path', style: Theme.of(context).textTheme.titleMedium),
                    const SizedBox(height: 8),
                    TextField(
                      controller: _filePathController,
                      decoration: const InputDecoration(
                        border: OutlineInputBorder(),
                        hintText: 'e.g. C:/Users/shahe/Desktop/lecture.pdf or notes.png',
                        prefixIcon: Icon(Icons.attach_file, color: Color(0xFF00E5FF)),
                      ),
                    ),
                    const SizedBox(height: 16),
                    ElevatedButton.icon(
                      onPressed: runtimeState.isLoading
                          ? null
                          : () {
                              ref.read(runtimeProvider.notifier).runEndToEndPipeline(
                                    _promptController.text,
                                    filePath: _filePathController.text.trim().isEmpty
                                        ? null
                                        : _filePathController.text.trim(),
                                  );
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

