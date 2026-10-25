(fn HateCheck (I)
  (Funzionedichiamata|WhoUp :Who (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniThreatWho) I))
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Variabili|Predefinito|OttieniWhoOk) (Utility|Operatori|Maggiore(>) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniThreatVal) I) (Variabili|Predefinito|OttieniHateBest)))
    (:then
      (Variabili|Predefinito|ImpostaHateBest (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniThreatVal) I))
      (Variabili|Predefinito|ImpostaHated (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniThreatWho) I)))))
