(fn HeroNext (Goal)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Utilità|Array|Length (Variabili|Predefinito|OttieniHeroPath)) 1)
    (:then
      (Variabili|Predefinito|ImpostaNextPoint (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniHeroPath) 1)))
    (:else
      (Variabili|Predefinito|ImpostaNextPoint Goal))))
