class RuntimeEvent {
  final String eventId;
  final String eventType;
  final String message;
  final String? nodeId;
  final String? deviceId;
  final String timestamp;
  final Map<String, dynamic>? payload;

  RuntimeEvent({
    required this.eventId,
    required this.eventType,
    required this.message,
    this.nodeId,
    this.deviceId,
    required this.timestamp,
    this.payload,
  });

  factory RuntimeEvent.fromJson(Map<String, dynamic> json) {
    return RuntimeEvent(
      eventId: json['event_id'] ?? '',
      eventType: json['event_type'] ?? 'INFO',
      message: json['message'] ?? '',
      nodeId: json['node_id'],
      deviceId: json['device_id'],
      timestamp: json['timestamp'] ?? DateTime.now().toIso8601String(),
      payload: json['payload'],
    );
  }
}
