(fn RangedStep (Dt Dist)
  (Funzionedichiamata|ClearShot)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utility|Operatori|Minoreuguale(<=) Dist (Matematica|Float|Min(Float) (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniNRange) 100.0) 1500.0)) (Variabili|Predefinito|OttieniShotClear))
    (:then
      (Funzionedichiamata|FaceToward :Goal (Trasformazione|GetActorLocation (Variabili|Predefinito|OttieniFoe)))
      (Funzionedichiamata|Bite :Dt Dt)
      (Funzionedichiamata|StopChase))
    (:else
      (Funzionedichiamata|ChaseFoe :Dt Dt))))
