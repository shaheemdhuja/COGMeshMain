import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../models/runtime_event.dart';
import 'constants.dart';

class WebSocketClient {
  WebSocketChannel? _channel;
  final _eventController = StreamController<RuntimeEvent>.broadcast();

  Stream<RuntimeEvent> get eventStream => _eventController.stream;

  void connect({String? customUrl}) {
    final url = customUrl ?? AppConstants.wsUrl;
    try {
      _channel = WebSocketChannel.connect(Uri.parse(url));
      _channel!.stream.listen(
        (data) {
          try {
            final jsonMap = jsonDecode(data);
            final event = RuntimeEvent.fromJson(jsonMap);
            _eventController.add(event);
          } catch (_) {}
        },
        onError: (err) {},
        onDone: () {},
      );
    } catch (_) {}
  }

  void disconnect() {
    _channel?.sink.close();
    _channel = null;
  }
}
