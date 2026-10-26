(fn PartyRowsTick ()
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniInParty) (Variabili|Predefinito|OttieniPartyRows))
    (:else
      (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniInParty)
        (:then
          (Funzionedichiamata|JoinRows))
        (:else
          (Funzionedichiamata|LeaveRows))))))
