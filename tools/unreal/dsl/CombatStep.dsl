(fn CombatStep (Dt Dist)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniFleeUntil) (Utilità|Testo|GetGameTimeinSeconds))
    (:then
      (Funzionedichiamata|FleeStep :Dt Dt))
    (:else
      (Funzionedichiamata|CombatStepOn :Dt Dt :Dist Dist))))
