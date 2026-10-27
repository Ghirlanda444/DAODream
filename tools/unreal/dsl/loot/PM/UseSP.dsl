(fn UseSP (Who)
  (Variabili|Predefinito|ImpostaUseSPv (Variabili|Predefinito|OttieniPSpell))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) Who (Gioco|GetPlayerPawn 0))
    (:else
      (Funzionedichiamata|UseSPCast :A Who))))
