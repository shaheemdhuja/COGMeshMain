import 'package:flutter/material.dart';
import '../core/constants.dart';

class DagVisualizerWidget extends StatelessWidget {
  final Map<String, String> taskStates;

  const DagVisualizerWidget({super.key, required this.taskStates});

  Color _getNodeColor(String nodeName) {
    final state = taskStates[nodeName] ?? taskStates.values.firstWhere((s) => true, orElse: () => 'PENDING');
    switch (state.toUpperCase()) {
      case 'READY':
        return AppConstants.taskReady;
      case 'RUNNING':
        return AppConstants.taskRunning;
      case 'COMPLETED':
        return AppConstants.taskCompleted;
      case 'FAILED':
        return AppConstants.taskFailed;
      default:
        return AppConstants.taskPending;
    }
  }

  @override
  Widget build(BuildContext context) {
    final nodes = [
      {'name': 'OCR Task', 'key': 'node-1'},
      {'name': 'Summarization', 'key': 'node-2'},
      {'name': 'Translation', 'key': 'node-3'},
      {'name': 'MCQ Generation', 'key': 'node-4'},
    ];

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: AppConstants.cardDark,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF334155)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Live ExecutionDAG Pipeline',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 24),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: nodes.map((n) {
              final color = _getNodeColor(n['key']!);
              return Container(
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: color, width: 2),
                ),
                child: Row(
                  children: [
                    Icon(Icons.hub, color: color, size: 20),
                    const SizedBox(width: 8),
                    Text(
                      n['name']!,
                      style: TextStyle(color: color, fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }
}
