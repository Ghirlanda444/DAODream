(fn TrBuffOwn ()
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Variabili|Predefinito|OttieniTMeParty) (Utilità|IsValid (Variabili|Predefinito|OttieniTMeTgt)))
    (:then
      (Funzionedichiamata|TrPeek :A (Variabili|Predefinito|OttieniTMeTgt))
      (Funzionedichiamata|TrBuffOf :A (Variabili|Predefinito|OttieniTMeTgt))
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Matematica|Booleano|ANDBoolean (Variabili|Predefinito|OttieniPkAlive) (Matematica|Booleano|ORBoolean (Matematica|Booleano|ANDBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTMeSide) 1) (Matematica|Booleano|ORBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniPkSide) 0) (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniPkSide) 2))) (Matematica|Booleano|ANDBoolean (Matematica|Booleano|ORBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTMeSide) 0) (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTMeSide) 2)) (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniPkSide) 1)))) (Variabili|Predefinito|OttieniPkBuff))
    (:then
      (Variabili|Predefinito|ImpostaPkWho (Variabili|Predefinito|OttieniTMeTgt)))))))
