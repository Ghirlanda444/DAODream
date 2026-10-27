(fn TrTryLow (K)
  (Funzionedichiamata|TrPeek :A (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniCL) K))
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Matematica|Booleano|ANDBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTP) 0.0) (Utility|Operatori|Minore(<) (Variabili|Predefinito|OttieniPkHp) (Variabili|Predefinito|OttieniPkBest))) (Matematica|Booleano|ANDBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTP) 1.0) (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniPkHp) (Variabili|Predefinito|OttieniPkBest))))
    (:then
      (Variabili|Predefinito|ImpostaPkBest (Variabili|Predefinito|OttieniPkHp))
      (Variabili|Predefinito|ImpostaPkWho (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniCL) K)))))
