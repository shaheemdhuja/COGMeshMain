class ExecutionContextModel {
  final String contextId;
  final String goalId;
  final String status;
  final Map<String, String> taskStates;
  final Map<String, dynamic> results;
  final Map<String, dynamic> metrics;
  final List<dynamic> events;

  ExecutionContextModel({
    required this.contextId,
    required this.goalId,
    required this.status,
    required this.taskStates,
    required this.results,
    required this.metrics,
    required this.events,
  });

  factory ExecutionContextModel.fromJson(Map<String, dynamic> json) {
    return ExecutionContextModel(
      contextId: json['context_id'] ?? '',
      goalId: json['goal_id'] ?? '',
      status: json['status'] ?? 'RUNNING',
      taskStates: Map<String, String>.from(json['task_states'] ?? {}),
      results: Map<String, dynamic>.from(json['results'] ?? {}),
      metrics: Map<String, dynamic>.from(json['metrics'] ?? {}),
      events: List<dynamic>.from(json['events'] ?? []),
    );
  }
}
