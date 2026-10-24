(fn HurtPlayer (Amount)
  (Variabili|Predefinito|ImpostaPlayerHealth (Matematica|Float|Max(Float) (Utility|Operatori|Sottrai (Variabili|Predefinito|OttieniPlayerHealth) Amount) 0.0))
  (Funzionedichiamata|ShowHealth)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniPlayerHealth) 0.0)
    (:else
      (Funzionedichiamata|PlayerFalls))))
