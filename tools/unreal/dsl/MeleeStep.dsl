(fn MeleeStep (Dt Dist)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) Dist 110.0)
    (:then
      (Funzionedichiamata|ChaseFoe :Dt Dt))
    (:else
      (Funzionedichiamata|FaceToward :Goal (Trasformazione|GetActorLocation (Variabili|Predefinito|OttieniFoe)))
      (Funzionedichiamata|Bite :Dt Dt)
      (Funzionedichiamata|StopChase))))
