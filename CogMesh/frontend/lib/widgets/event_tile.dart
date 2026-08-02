import 'package:flutter/material.dart';
import '../models/runtime_event.dart';

class EventTile extends StatelessWidget {
  final RuntimeEvent event;

  const EventTile({super.key, required this.event});

  Color _getEventColor(String type) {
    switch (type.toUpperCase()) {
      case 'PLAN_STARTED':
      case 'TASK_STARTED':
        return Colors.blueAccent;
      case 'TASK_COMPLETED':
      case 'PLAN_COMPLETED':
        return Colors.greenAccent;
      case 'TASK_FAILED':
        return Colors.redAccent;
      default:
        return Colors.orangeAccent;
    }
  }

  @override
  Widget build(BuildContext context) {
    final color = _getEventColor(event.eventType);

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(8),
        border: Border(left: BorderSide(color: color, width: 4)),
      ),
      child: Row(
        children: [
          Icon(Icons.bolt, color: color, size: 20),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  event.message,
                  style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w500),
                ),
                if (event.nodeId != null)
                  Text(
                    'Node: ${event.nodeId} | Device: ${event.deviceId ?? "Local"}',
                    style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 12),
                  ),
              ],
            ),
          ),
          Text(
            event.timestamp.split('T').last.split('.').first,
            style: const TextStyle(color: Color(0xFF64748B), fontSize: 12),
          ),
        ],
      ),
    );
  }
}
