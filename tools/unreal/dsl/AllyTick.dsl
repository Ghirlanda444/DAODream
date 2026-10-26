(fn AllyTick (Dt)
  (Variabili|Predefinito|ImpostaAllyOn (Matematica|Booleano|ANDBoolean (Matematica|Booleano|ANDBoolean (Variabili|Predefinito|OttieniAlly) (Matematica|Booleano|NOTBoolean (Variabili|Predefinito|OttieniDead))) (Matematica|Booleano|ANDBoolean (Matematica|Booleano|NOTBoolean (Variabili|Predefinito|OttieniHostile)) (Matematica|Booleano|NOTBoolean (Variabili|Rendering|OttieniActorHiddenInGame)))))
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniAllyOn)
    (:then
      (Utilità|ControlloDiFlusso|Ramo (Classe|BPPlotManager|IsTalking (Variabili|Predefinito|OttieniMgr))
        (:else
          (Variabili|Predefinito|ImpostaRetargetTimer (Utility|Operatori|Sottrai (Variabili|Predefinito|OttieniRetargetTimer) Dt))
          (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniRetargetTimer) 0.0)
            (:then
              (Funzionedichiamata|AllyFight :Dt Dt))
            (:else
              (Variabili|Predefinito|ImpostaRetargetTimer 0.5)
              (Classe|BPPlotManager|AssignTarget (Variabili|Predefinito|OttieniMgr) :Follower (Variabili|Ottieniunriferimentoasestesso))
              (Funzionedichiamata|AllyFight :Dt Dt))))))))
