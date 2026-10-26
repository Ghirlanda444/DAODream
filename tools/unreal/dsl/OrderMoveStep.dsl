(fn OrderMoveStep (Dt)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Minore(<) (Matematica|Vettore|Distance2D(Vector) (Trasformazione|GetActorLocation (Variabili|Ottieniunriferimentoasestesso)) (Variabili|Predefinito|OttieniOrderGoal)) 60.0)
    (:then
      (Variabili|Predefinito|ImpostaOrderMove "false")
      (Funzionedichiamata|StopMoving))
    (:else
      (Funzionedichiamata|FollowPath :Goal (Variabili|Predefinito|OttieniOrderGoal) :Speed 420.0 :Dt Dt :bJog "true"))))
