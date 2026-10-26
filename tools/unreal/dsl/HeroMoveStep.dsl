(fn HeroMoveStep (Dt)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Minore(<) (Matematica|Vettore|Distance2D(Vector) (Trasformazione|GetActorLocation (Gioco|GetPlayerPawn 0)) (Variabili|Predefinito|OttieniMoveGoal)) 60.0)
    (:then
      (Variabili|Predefinito|ImpostaMoving "false"))
    (:else
      (Funzionedichiamata|HeroWalk :Goal (Variabili|Predefinito|OttieniMoveGoal) :Dt Dt))))
