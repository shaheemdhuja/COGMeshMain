import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/device_provider.dart';
import '../providers/runtime_provider.dart';
import '../widgets/dag_painter.dart';
import '../widgets/event_tile.dart';
import '../widgets/metric_card.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final devicesAsync = ref.watch(devicesProvider);
    final runtimeState = ref.watch(runtimeProvider);

    return Scaffold(
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'System Overview & Live Runtime Dashboard',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: 24),

            // Top Metric Cards Row
            Row(
              children: [
                Expanded(
                  child: MetricCard(
                    title: 'Active Nodes',
                    value: '${devicesAsync.value?.length ?? 0}',
                    icon: Icons.devices,
                    color: const Color(0xFF00E5FF),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: MetricCard(
                    title: 'Runtime Status',
                    value: runtimeState.context?.status ?? 'IDLE',
                    icon: Icons.speed,
                    color: const Color(0xFF7C4DFF),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: MetricCard(
                    title: 'Completed Tasks',
                    value: '${runtimeState.context?.results.length ?? 0}',
                    icon: Icons.check_circle,
                    color: const Color(0xFF10B981),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // DAG Pipeline State
            DagVisualizerWidget(
              taskStates: runtimeState.context?.taskStates ?? {},
            ),
            const SizedBox(height: 24),

            // Event Log Stream
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Recent Runtime Events', style: Theme.of(context).textTheme.titleLarge),
                    const SizedBox(height: 16),
                    if (runtimeState.events.isEmpty)
                      const Text('No recent events recorded.', style: TextStyle(color: Color(0xFF64748B)))
                    else
                      ...runtimeState.events.reversed.take(5).map((e) => EventTile(event: e)),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
