(fn ControlledAct (Dt)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniManualUntil) (Utilità|Testo|GetGameTimeinSeconds))
    (:then
      (Funzionedichiamata|FollowPath :Goal (Utility|Operatori|Aggiungi (Trasformazione|GetActorLocation (Variabili|Ottieniunriferimentoasestesso)) (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniManualDir) (Matematica|Vettore|MakeVector 400.0 400.0 0.0))) :Speed 420.0 :Dt Dt :bJog "true"))
    (:else
      (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniOrderMove)
        (:then
          (Funzionedichiamata|OrderMoveStep :Dt Dt))
        (:else
          (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniTarget))
            (:then
              (Funzionedichiamata|PartyFight :Dt Dt))
            (:else
              (Funzionedichiamata|StopMoving))))))))
