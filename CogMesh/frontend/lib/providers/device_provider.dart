import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../core/api_client.dart';
import '../models/capability.dart';
import '../models/device.dart';

final apiClientProvider = Provider<ApiClient>((ref) => ApiClient());

final devicesProvider = FutureProvider<List<Device>>((ref) async {
  final client = ref.watch(apiClientProvider);
  return await client.fetchDevices();
});

final capabilitiesProvider = FutureProvider<List<Capability>>((ref) async {
  final client = ref.watch(apiClientProvider);
  return await client.fetchCapabilities();
});
