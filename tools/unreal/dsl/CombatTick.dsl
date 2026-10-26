(fn CombatTick (Dt)
  (Funzionedichiamata|Recover)
  (Funzionedichiamata|PartyRowsTick)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Variabili|Predefinito|OttieniHostile) (Matematica|Booleano|NOTBoolean (Variabili|Predefinito|OttieniDead)))
    (:then
      (bind _talking (Classe|BPPlotManager|IsTalking (Variabili|Predefinito|OttieniMgr)))
      (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean _talking (Variabili|Rendering|OttieniActorHiddenInGame))
        (:else
          (Funzionedichiamata|HostileTick :Dt Dt))))))
