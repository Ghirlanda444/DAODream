(fn TacShow ()
  (Interfacciautente|Viewport|AddtoViewport (Variabili|Predefinito|OttieniTac))
  (Classe|WBPTactics|Open (Variabili|Predefinito|OttieniTac) :InMgr (Variabili|Ottieniunriferimentoasestesso))
  (Variabili|Predefinito|ImpostaTacPaused (Variabili|Predefinito|OttieniPaused))
  (Variabili|Predefinito|ImpostaTacOpen "true")
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniPaused)
    (:else
      (Funzionedichiamata|TogglePause))))
