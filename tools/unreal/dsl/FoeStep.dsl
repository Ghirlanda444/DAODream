(fn FoeStep (Dt)
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniFoe))
    (:then
      (Funzionedichiamata|CombatStep :Dt Dt :Dist (Trasformazione|GetHorizontalDistanceTo (Variabili|Ottieniunriferimentoasestesso) (Variabili|Predefinito|OttieniFoe))))
    (:else
      (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniChasing)
        (:then
          (Variabili|Predefinito|ImpostaChasing "false")
          (Funzionedichiamata|StopMoving))))))
