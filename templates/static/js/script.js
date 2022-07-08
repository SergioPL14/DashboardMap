$( document ).ready(function() {
  let sessionId = '';

  // 1. Request the session ID from Vault
  $(window).on('load', function() {
    var readyMessage = JSON.stringify({'message_id': 'ready', 'data': {}});
    window.parent.postMessage(readyMessage, '*');
  });

  // 2. Listen for a message event from Vault
  $(window).on('message', function(e) {
    var message = JSON.parse(e.originalEvent.data);
    if (message['message_id'] == 'session_id') {
      sessionId = message['data']['session_id'];
    $.post( "/postmethod", {
      key : sessionId
    });
    }
  });
});