(fn Wounded ()
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniHealth) 0.0)
    (:then
      (Funzionedichiamata|ShowPartyBar))
    (:else
      (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniInParty)
        (:then
          (Funzionedichiamata|KnockOut))
        (:else
          (Funzionedichiamata|Die))))))
