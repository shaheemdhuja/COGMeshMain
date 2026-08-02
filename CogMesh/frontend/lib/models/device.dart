class Device {
  final String id;
  final String deviceName;
  final String deviceType;
  final String ipAddress;
  final int port;
  final String platform;
  final String status;
  final String? registeredAt;

  Device({
    required this.id,
    required this.deviceName,
    required this.deviceType,
    required this.ipAddress,
    required this.port,
    required this.platform,
    required this.status,
    this.registeredAt,
  });

  factory Device.fromJson(Map<String, dynamic> json) {
    return Device(
      id: json['id'] ?? json['device_id'] ?? '',
      deviceName: json['device_name'] ?? 'Unknown Device',
      deviceType: json['device_type'] ?? 'LAPTOP',
      ipAddress: json['ip_address'] ?? '127.0.0.1',
      port: json['port'] ?? 8000,
      platform: json['platform'] ?? 'unknown',
      status: json['status'] ?? 'ONLINE',
      registeredAt: json['registered_at'],
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'device_name': deviceName,
        'device_type': deviceType,
        'ip_address': ipAddress,
        'port': port,
        'platform': platform,
        'status': status,
        'registered_at': registeredAt,
      };
}
