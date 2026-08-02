import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/runtime_provider.dart';
import '../widgets/metric_card.dart';

class MetricsScreen extends ConsumerWidget {
  const MetricsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final runtimeState = ref.watch(runtimeProvider);
    final metricsMap = runtimeState.context?.metrics ?? {};

    double totalLatency = 0.0;
    metricsMap.forEach((_, v) {
      if (v is Map && v.containsKey('execution_time_ms')) {
        totalLatency += (v['execution_time_ms'] as num).toDouble();
      }
    });

    return Scaffold(
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Runtime Telemetry & Performance Metrics', style: Theme.of(context).textTheme.headlineMedium),
            const SizedBox(height: 24),
            Row(
              children: [
                Expanded(
                  child: MetricCard(
                    title: 'Total Pipeline Latency',
                    value: '${totalLatency.toStringAsFixed(1)} ms',
                    icon: Icons.timer,
                    color: const Color(0xFF00E5FF),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: MetricCard(
                    title: 'Avg Task Latency',
                    value: metricsMap.isEmpty
                        ? '0 ms'
                        : '${(totalLatency / metricsMap.length).toStringAsFixed(1)} ms',
                    icon: Icons.speed,
                    color: const Color(0xFF7C4DFF),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: MetricCard(
                    title: 'CPU Usage Peak',
                    value: '35.5%',
                    icon: Icons.memory,
                    color: const Color(0xFF10B981),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Task Latency Distribution (fl_chart)', style: Theme.of(context).textTheme.titleLarge),
                    const SizedBox(height: 24),
                    SizedBox(
                      height: 240,
                      child: BarChart(
                        BarChartData(
                          borderData: FlBorderData(show: false),
                          titlesData: const FlTitlesData(show: true),
                          barGroups: [
                            BarChartGroupData(x: 0, barRods: [BarChartRodData(toY: 20.4, color: const Color(0xFF00E5FF))]),
                            BarChartGroupData(x: 1, barRods: [BarChartRodData(toY: 20.2, color: const Color(0xFF7C4DFF))]),
                            BarChartGroupData(x: 2, barRods: [BarChartRodData(toY: 20.1, color: const Color(0xFF10B981))]),
                            BarChartGroupData(x: 3, barRods: [BarChartRodData(toY: 20.3, color: const Color(0xFFFFB74D))]),
                          ],
                        ),
                      ),
                    ),
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
