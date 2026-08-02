import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/runtime_provider.dart';
import '../widgets/event_tile.dart';

class RuntimeScreen extends ConsumerWidget {
  const RuntimeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final runtimeState = ref.watch(runtimeProvider);
    final contextModel = runtimeState.context;

    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Runtime Orchestrator Execution State', style: Theme.of(context).textTheme.headlineMedium),
            const SizedBox(height: 24),
            Row(
              children: [
                Expanded(
                  child: Card(
                    child: Padding(
                      padding: const EdgeInsets.all(20),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Execution Context ID', style: Theme.of(context).textTheme.titleLarge),
                          const SizedBox(height: 8),
                          SelectableText(
                            contextModel?.contextId ?? 'No active context',
                            style: const TextStyle(color: Color(0xFF00E5FF), fontFamily: 'monospace'),
                          ),
                          const SizedBox(height: 12),
                          Text('Status: ${contextModel?.status ?? "IDLE"}',
                              style: const TextStyle(fontWeight: FontWeight.bold)),
                        ],
                      ),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),
            Text('Live Event Timeline Stream', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 12),
            Expanded(
              child: Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: runtimeState.events.isEmpty
                      ? const Center(child: Text('Waiting for runtime events...'))
                      : ListView.builder(
                          itemCount: runtimeState.events.length,
                          itemBuilder: (context, index) {
                            return EventTile(event: runtimeState.events[index]);
                          },
                        ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
