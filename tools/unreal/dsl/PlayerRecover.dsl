(fn PlayerRecover ()
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Variabili|Predefinito|OttieniPStunned) (Utility|Operatori|Minoreuguale(<=) (Variabili|Predefinito|OttieniPStunUntil) (Utilità|Testo|GetGameTimeinSeconds)))
    (:then
      (Variabili|Predefinito|ImpostaPStunned "false")
      (Input|EnableInput (Gioco|GetPlayerPawn 0) (Gioco|GetPlayerController 0)))))
