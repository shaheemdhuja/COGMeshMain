import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:cogmesh_dashboard/core/api_client.dart';

void main() {
  group('ApiClient REST Tests', () {
    test('fetchDevices returns list of Device models on 200 OK', () async {
      final mockClient = MockClient((request) async {
        return http.Response('''[
          {
            "id": "dev-100",
            "device_name": "Workstation Alpha",
            "device_type": "LAPTOP",
            "ip_address": "192.168.1.10",
            "port": 8000,
            "platform": "windows",
            "status": "ONLINE"
          }
        ]''', 200);
      });

      final apiClient = ApiClient(client: mockClient);
      final devices = await apiClient.fetchDevices();

      expect(devices.length, equals(1));
      expect(devices.first.deviceName, equals('Workstation Alpha'));
      expect(devices.first.deviceType, equals('LAPTOP'));
    });
  });
}
