(fn WhoUp (Who)
  (Variabili|Predefinito|ImpostaWhoOk "false")
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) Who (Gioco|GetPlayerPawn 0))
    (:then
      (Variabili|Predefinito|ImpostaWhoOk (Matematica|Booleano|NOTBoolean (Matematica|Booleano|ORBoolean (Classe|BPPlotManager|OttieniPlayerDown (Variabili|Predefinito|OttieniMgr)) (Classe|BPPlotManager|OttieniFeign (Variabili|Predefinito|OttieniMgr))))))
    (:else
      (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid Who)
        (:then
          (Funzionedichiamata|NpcUp :Who Who))))))
