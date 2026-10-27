(fn CdOne (K Who Ab)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Matematica|Booleano|ANDBoolean (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniCdWho) K) Who) (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniCdAb) K) Ab)) (Utility|Operatori|Maggiore(>) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniCdUntil) K) (Utilità|Testo|GetGameTimeinSeconds)))
    (:then
      (Variabili|Predefinito|ImpostaGBool "false"))))
