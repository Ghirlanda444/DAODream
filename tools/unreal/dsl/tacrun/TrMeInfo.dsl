(fn TrMeInfo (A)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) A (Gioco|GetPlayerPawn 0))
    (:then
      (Variabili|Predefinito|ImpostaTMeHated (Variabili|Predefinito|OttieniHeroTarget))
      (Variabili|Predefinito|ImpostaTMeBeh (Variabili|Predefinito|OttieniPBehavior)))
    (:else
      (Funzionedichiamata|TrMeInfoCast :A A))))
