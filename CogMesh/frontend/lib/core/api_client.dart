import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/capability.dart';
import '../models/device.dart';
import '../models/execution_context.dart';
import 'constants.dart';

class ApiClient {
  final http.Client _client;

  ApiClient({http.Client? client}) : _client = client ?? http.Client();

  // Devices REST API
  Future<List<Device>> fetchDevices() async {
    final response = await _client.get(Uri.parse('${AppConstants.baseUrl}/devices'));
    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => Device.fromJson(json)).toList();
    }
    return [];
  }

  // Capabilities REST API
  Future<List<Capability>> fetchCapabilities() async {
    final response = await _client.get(Uri.parse('${AppConstants.baseUrl}/capabilities'));
    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => Capability.fromJson(json)).toList();
    }
    return [];
  }

  // Parse Natural Language Goal
  Future<Map<String, dynamic>> parseGoal(String goalText) async {
    final response = await _client.post(
      Uri.parse('${AppConstants.baseUrl}/goals/parse'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'goal': goalText}),
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception('Failed to parse goal: ${response.body}');
  }

  // Generate ExecutionDAG
  Future<Map<String, dynamic>> generateWorkflow(String goalId) async {
    final response = await _client.post(
      Uri.parse('${AppConstants.baseUrl}/workflows/generate'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'goal_id': goalId}),
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception('Failed to generate workflow: ${response.body}');
  }

  // Generate ExecutionPlan Scheduler
  Future<Map<String, dynamic>> generatePlan(String goalId) async {
    final response = await _client.post(
      Uri.parse('${AppConstants.baseUrl}/scheduler/plan'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'goal_id': goalId}),
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception('Failed to schedule plan: ${response.body}');
  }

  // Start Runtime Orchestrator
  Future<ExecutionContextModel> startRuntime(String goalId) async {
    final response = await _client.post(
      Uri.parse('${AppConstants.baseUrl}/runtime/start'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'goal_id': goalId}),
    );
    if (response.statusCode == 200) {
      return ExecutionContextModel.fromJson(jsonDecode(response.body));
    }
    throw Exception('Failed to start runtime: ${response.body}');
  }

  // Fetch Task Adapters
  Future<List<Map<String, dynamic>>> fetchAdapters() async {
    final response = await _client.get(Uri.parse('${AppConstants.baseUrl}/tasks'));
    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.cast<Map<String, dynamic>>();
    }
    return [];
  }
}
