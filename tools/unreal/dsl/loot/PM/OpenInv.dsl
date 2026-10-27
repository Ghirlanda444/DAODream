(fn OpenInv ()
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniTalking)
    (:else
      (Funzionedichiamata|InvMake)
      (Interfacciautente|Viewport|AddtoViewport (Variabili|Predefinito|OttieniWInv))
      (Classe|WBPInventory|Open (Variabili|Predefinito|OttieniWInv) :InMgr (Variabili|Ottieniunriferimentoasestesso))
      (Variabili|Predefinito|ImpostaInvOpen "true"))))
