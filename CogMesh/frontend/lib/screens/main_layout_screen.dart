import 'package:flutter/material.dart';
import 'dashboard_screen.dart';
import 'devices_screen.dart';
import 'workflow_screen.dart';
import 'runtime_screen.dart';
import 'results_screen.dart';
import 'metrics_screen.dart';

class MainLayoutScreen extends StatefulWidget {
  const MainLayoutScreen({super.key});

  @override
  State<MainLayoutScreen> createState() => _MainLayoutScreenState();
}

class _MainLayoutScreenState extends State<MainLayoutScreen> {
  int _selectedIndex = 0;

  final List<Widget> _screens = const [
    DashboardScreen(),
    DevicesScreen(),
    WorkflowScreen(),
    RuntimeScreen(),
    ResultsScreen(),
    MetricsScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Row(
        children: [
          NavigationRail(
            selectedIndex: _selectedIndex,
            onDestinationSelected: (index) => setState(() => _selectedIndex = index),
            labelType: NavigationRailLabelType.all,
            backgroundColor: const Color(0xFF0F172A),
            selectedIconTheme: const IconThemeData(color: Color(0xFF00E5FF)),
            selectedLabelTextStyle: const TextStyle(color: Color(0xFF00E5FF), fontWeight: FontWeight.bold),
            unselectedIconTheme: const IconThemeData(color: Color(0xFF64748B)),
            unselectedLabelTextStyle: const TextStyle(color: Color(0xFF64748B)),
            leading: Column(
              children: [
                const SizedBox(height: 16),
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: const Color(0xFF00E5FF).withOpacity(0.2),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(Icons.hub, color: Color(0xFF00E5FF), size: 28),
                ),
                const SizedBox(height: 8),
                const Text('CogMesh', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
                const SizedBox(height: 24),
              ],
            ),
            destinations: const [
              NavigationRailDestination(icon: Icon(Icons.dashboard), label: Text('Dashboard')),
              NavigationRailDestination(icon: Icon(Icons.devices), label: Text('Devices')),
              NavigationRailDestination(icon: Icon(Icons.account_tree), label: Text('Workflow')),
              NavigationRailDestination(icon: Icon(Icons.speed), label: Text('Runtime')),
              NavigationRailDestination(icon: Icon(Icons.analytics), label: Text('Results')),
              NavigationRailDestination(icon: Icon(Icons.insights), label: Text('Metrics')),
            ],
          ),
          const VerticalDivider(thickness: 1, width: 1, color: Color(0xFF1E293B)),
          Expanded(child: _screens[_selectedIndex]),
        ],
      ),
    );
  }
}
