(fn DlgCamOff ()
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utilità|IsValid (Gioco|GetPlayerPawn 0)) (Matematica|Booleano|NOTBoolean (Variabili|Predefinito|OttieniTalking)))
    (:then
      (Partita|Giocatore|SetViewTargetwithBlend (Gioco|GetPlayerController 0) (Gioco|GetPlayerPawn 0) 0.35))))
