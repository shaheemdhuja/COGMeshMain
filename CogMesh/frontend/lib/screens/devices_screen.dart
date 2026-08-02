import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/device_provider.dart';

class DevicesScreen extends ConsumerWidget {
  const DevicesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final devicesAsync = ref.watch(devicesProvider);
    final capabilitiesAsync = ref.watch(capabilitiesProvider);

    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Registered Edge Devices', style: Theme.of(context).textTheme.headlineMedium),
            const SizedBox(height: 24),
            Expanded(
              child: devicesAsync.when(
                data: (devices) {
                  if (devices.isEmpty) {
                    return const Center(child: Text('No registered edge devices found.'));
                  }
                  return ListView.builder(
                    itemCount: devices.length,
                    itemBuilder: (context, index) {
                      final device = devices[index];
                      final cap = capabilitiesAsync.value?.firstWhere(
                        (c) => c.deviceId == device.id,
                        orElse: () => capabilitiesAsync.value?.first ?? capabilitiesAsync.value![0],
                      );

                      return Card(
                        margin: const EdgeInsets.only(bottom: 16),
                        child: Padding(
                          padding: const EdgeInsets.all(20),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  Icon(
                                    device.deviceType == 'LAPTOP' ? Icons.laptop : Icons.phone_android,
                                    color: const Color(0xFF00E5FF),
                                    size: 28,
                                  ),
                                  const SizedBox(width: 12),
                                  Text(device.deviceName, style: Theme.of(context).textTheme.titleLarge),
                                  const Spacer(),
                                  Chip(
                                    label: Text(device.status),
                                    backgroundColor: device.status == 'ONLINE'
                                        ? const Color(0xFF10B981).withOpacity(0.2)
                                        : Colors.redAccent.withOpacity(0.2),
                                    side: BorderSide(
                                      color: device.status == 'ONLINE' ? const Color(0xFF10B981) : Colors.redAccent,
                                    ),
                                  ),
                                ],
                              ),
                              const Divider(height: 24, color: Color(0xFF334155)),
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Text('IP: ${device.ipAddress}:${device.port}'),
                                  Text('Platform: ${device.platform}'),
                                  Text('CPU: ${cap?.cpuCores ?? 8} Cores'),
                                  Text('RAM: ${cap?.ramGb ?? 16.0} GB'),
                                  Text('Battery: ${cap?.batteryLevel ?? 100}%'),
                                ],
                              ),
                              if (cap != null) ...[
                                const SizedBox(height: 12),
                                Wrap(
                                  spacing: 8,
                                  children: cap.supportedTasks
                                      .map((task) => Chip(
                                            label: Text(task, style: const TextStyle(fontSize: 11)),
                                            backgroundColor: const Color(0xFF1E293B),
                                          ))
                                      .toList(),
                                ),
                              ],
                            ],
                          ),
                        ),
                      );
                    },
                  );
                },
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (err, stack) => Center(child: Text('Error: $err')),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
