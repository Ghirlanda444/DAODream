(fn FollowLeader (Dt)
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Classe|BPPlotManager|OttieniSelected (Variabili|Predefinito|OttieniMgr)))
    (:then
      (Funzionedichiamata|FollowTo :Leader (Classe|BPPlotManager|OttieniSelected (Variabili|Predefinito|OttieniMgr)) :Dt Dt))
    (:else
      (Funzionedichiamata|FollowTo :Leader (Gioco|GetPlayerPawn 0) :Dt Dt))))
