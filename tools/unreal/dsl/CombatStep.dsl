(fn CombatStep (Dt Dist)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) Dist 1500.0)
    (:else
      (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniNRange) 0.0)
        (:then
          (Funzionedichiamata|RangedStep :Dt Dt :Dist Dist))
        (:else
          (Funzionedichiamata|MeleeStep :Dt Dt :Dist Dist))))))
