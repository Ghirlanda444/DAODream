(fn TrFoeTest (A)
  (Variabili|Predefinito|ImpostaBFoe "false")
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid A)
    (:then
      (Funzionedichiamata|TrPeek :A A)
      (Variabili|Predefinito|ImpostaBFoe (Matematica|Booleano|ANDBoolean (Variabili|Predefinito|OttieniPkAlive) (Matematica|Booleano|ORBoolean (Matematica|Booleano|ANDBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTMeSide) 1) (Matematica|Booleano|ORBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniPkSide) 0) (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniPkSide) 2))) (Matematica|Booleano|ANDBoolean (Matematica|Booleano|ORBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTMeSide) 0) (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTMeSide) 2)) (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniPkSide) 1))))))))
