(fn ReadFoe ()
  (Variabili|Predefinito|ImpostaFoeHp 100.0)
  (Variabili|Predefinito|ImpostaFoeSta 100.0)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniFoe) (Gioco|GetPlayerPawn 0))
    (:then
      (Variabili|Predefinito|ImpostaFoeHp (Utility|Operatori|Moltiplica (Utility|Operatori|Dividi (Classe|BPPlotManager|OttieniPlayerHealth (Variabili|Predefinito|OttieniMgr)) (Matematica|Float|Max(Float) (Classe|BPPlotManager|OttieniPlayerMaxHealth (Variabili|Predefinito|OttieniMgr)) 1.0)) 100.0))
      (Variabili|Predefinito|ImpostaFoeSta (Utility|Operatori|Moltiplica (Utility|Operatori|Dividi (Classe|BPPlotManager|OttieniPStamina (Variabili|Predefinito|OttieniMgr)) (Matematica|Float|Max(Float) (Classe|BPPlotManager|OttieniPPool (Variabili|Predefinito|OttieniMgr)) 1.0)) 100.0)))
    (:else
      (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniFoe))
        (:then
          (Funzionedichiamata|WhoHealth :Who (Variabili|Predefinito|OttieniFoe))
          (Variabili|Predefinito|ImpostaFoeHp (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniWhoHp) 100.0)))))))
