(fn InitControls ()
  (Classe|PlayerController|ImpostaShowMouseCursor :self (Gioco|GetPlayerController 0) :bShowMouseCursor "true")
  (Input|SetInputModeGameAndUI :PlayerController (Gioco|GetPlayerController 0) :bHideCursorDuringCapture "true"))
