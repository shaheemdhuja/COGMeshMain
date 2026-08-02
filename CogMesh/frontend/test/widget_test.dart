import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:cogmesh_dashboard/main.dart';

void main() {
  testWidgets('Dashboard renders main layout navigation rail and titles', (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: CogMeshDashboardApp(),
      ),
    );

    expect(find.text('CogMesh'), findsOneWidget);
    expect(find.text('Dashboard'), findsOneWidget);
    expect(find.text('Devices'), findsOneWidget);
    expect(find.text('Workflow'), findsOneWidget);
    expect(find.text('Runtime'), findsOneWidget);
    expect(find.text('Results'), findsOneWidget);
    expect(find.text('Metrics'), findsOneWidget);
  });
}
