class Capability {
  final String deviceId;
  final int cpuCores;
  final double ramGb;
  final double batteryLevel;
  final String networkQuality;
  final List<String> supportedTasks;

  Capability({
    required this.deviceId,
    required this.cpuCores,
    required this.ramGb,
    required this.batteryLevel,
    required this.networkQuality,
    required this.supportedTasks,
  });

  factory Capability.fromJson(Map<String, dynamic> json) {
    return Capability(
      deviceId: json['device_id'] ?? '',
      cpuCores: json['cpu_cores'] ?? 4,
      ramGb: (json['ram_gb'] as num?)?.toDouble() ?? 8.0,
      batteryLevel: (json['battery_level'] as num?)?.toDouble() ?? 100.0,
      networkQuality: json['network_quality'] ?? 'EXCELLENT',
      supportedTasks: List<String>.from(json['supported_tasks'] ?? []),
    );
  }
}
