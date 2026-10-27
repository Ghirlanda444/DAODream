(fn HealAny (Who)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) Who (Gioco|GetPlayerPawn 0))
    (:then
      (Funzionedichiamata|HealPlayer :Amount (Variabili|Predefinito|OttieniUseAmt)))
    (:else
      (Funzionedichiamata|HealAnyCast :A Who))))
