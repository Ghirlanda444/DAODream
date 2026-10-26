(fn FollowTo (Leader Dt)
  (bind (_lx _ly _lz) (Matematica|Vettore|BreakVector (Trasformazione|GetActorLocation Leader)))
  (bind (_sx _sy _sz) (Matematica|Vettore|BreakVector (Trasformazione|GetActorLocation (Variabili|Ottieniunriferimentoasestesso))))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Trasformazione|GetDistanceTo (Variabili|Ottieniunriferimentoasestesso) Leader) 300.0)
    (:then
      (Funzionedichiamata|FollowPath :Goal (Matematica|Vettore|MakeVector _lx _ly _sz) :Speed 420.0 :Dt Dt :bJog "true"))
    (:else
      (Funzionedichiamata|StopMoving))))
