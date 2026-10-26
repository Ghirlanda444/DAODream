(fn FleeStep (Dt)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Minore(<) (Matematica|Vettore|Distance2D(Vector) (Trasformazione|GetActorLocation (Variabili|Ottieniunriferimentoasestesso)) (Variabili|Predefinito|OttieniFleeGoal)) 80.0)
    (:then
      (Variabili|Predefinito|ImpostaFleeUntil 0.0)
      (Funzionedichiamata|StopMoving))
    (:else
      (Funzionedichiamata|FollowPath :Goal (Variabili|Predefinito|OttieniFleeGoal) :Speed 300.0 :Dt Dt :bJog "true"))))
