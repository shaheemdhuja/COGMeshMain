import 'package:flutter/material.dart';

class AppConstants {
  static const String appName = 'CogMesh Runtime Dashboard';
  static const String baseUrl = 'http://127.0.0.1:8000/api/v1';
  static const String wsUrl = 'ws://127.0.0.1:8000/api/v1/communication/ws/dashboard';

  // Status Colors
  static const Color primaryCyan = Color(0xFF00E5FF);
  static const Color accentPurple = Color(0xFF7C4DFF);
  static const Color bgDark = Color(0xFF0F172A);
  static const Color cardDark = Color(0xFF1E293B);
  static const Color surfaceDark = Color(0xFF334155);

  static const Color statusOnline = Color(0xFF10B981);
  static const Color statusOffline = Color(0xFFEF4444);
  static const Color statusStale = Color(0xFFF59E0B);

  static const Color taskPending = Color(0xFF64748B);
  static const Color taskReady = Color(0xFF3B82F6);
  static const Color taskRunning = Color(0xFF8B5CF6);
  static const Color taskCompleted = Color(0xFF10B981);
  static const Color taskFailed = Color(0xFFEF4444);
}
