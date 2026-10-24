(fn ShowPartyBar ()
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniInParty)
    (:then
      (Sviluppo|SetHiddenInGame (Variabili|Predefinito|OttieniHealthWidget) "false")
      (Funzionedichiamata|UpdateBar))))
