import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../core/api_client.dart';
import '../models/execution_context.dart';
import '../models/runtime_event.dart';
import 'device_provider.dart';

class RuntimeState {
  final bool isLoading;
  final String? goalId;
  final ExecutionContextModel? context;
  final List<RuntimeEvent> events;
  final String? error;

  RuntimeState({
    this.isLoading = false,
    this.goalId,
    this.context,
    this.events = const [],
    this.error,
  });

  RuntimeState copyWith({
    bool? isLoading,
    String? goalId,
    ExecutionContextModel? context,
    List<RuntimeEvent>? events,
    String? error,
  }) {
    return RuntimeState(
      isLoading: isLoading ?? this.isLoading,
      goalId: goalId ?? this.goalId,
      context: context ?? this.context,
      events: events ?? this.events,
      error: error,
    );
  }
}

class RuntimeNotifier extends StateNotifier<RuntimeState> {
  final ApiClient _apiClient;

  RuntimeNotifier(this._apiClient) : super(RuntimeState());

  Future<void> runEndToEndPipeline(String prompt) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final goalData = await _apiClient.parseGoal(prompt);
      final String goalId = goalData['goal_id'];
      
      await _apiClient.generateWorkflow(goalId);
      await _apiClient.generatePlan(goalId);
      final context = await _apiClient.startRuntime(goalId);

      state = state.copyWith(
        isLoading: false,
        goalId: goalId,
        context: context,
      );
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  void addLiveEvent(RuntimeEvent event) {
    state = state.copyWith(events: [...state.events, event]);
  }
}

final runtimeProvider = StateNotifierProvider<RuntimeNotifier, RuntimeState>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return RuntimeNotifier(apiClient);
});
