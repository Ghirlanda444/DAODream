(fn WhoHealth (Who)
  (Variabili|Predefinito|ImpostaWhoHp 1.0)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) Who (Gioco|GetPlayerPawn 0))
    (:then
      (Variabili|Predefinito|ImpostaWhoHp (Utility|Operatori|Dividi (Classe|BPPlotManager|OttieniPlayerHealth (Variabili|Predefinito|OttieniMgr)) (Matematica|Float|Max(Float) (Classe|BPPlotManager|OttieniPlayerMaxHealth (Variabili|Predefinito|OttieniMgr)) 1.0))))
    (:else
      (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid Who)
        (:then
          (Funzionedichiamata|NpcHealth :Who Who))))))
