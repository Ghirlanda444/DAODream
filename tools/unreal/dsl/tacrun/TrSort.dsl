(fn TrSort (A)
  (bind _d (Trasformazione|GetHorizontalDistanceTo (Variabili|Predefinito|OttieniTMe) A))
  (Funzionedichiamata|TrInsNear :D _d)
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniPkAlive)
    (:then
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniPkSide) (Variabili|Predefinito|OttieniTMeSide)) (Utility|Operatori|Maggioreuguale(>=) (Variabili|Predefinito|OttieniTMeSide) 0))
    (:then
      (Funzionedichiamata|TrInsAlly :A A :D _d))
    (:else
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Matematica|Booleano|ANDBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTMeSide) 1) (Matematica|Booleano|ORBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniPkSide) 0) (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniPkSide) 2))) (Matematica|Booleano|ANDBoolean (Matematica|Booleano|ORBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTMeSide) 0) (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTMeSide) 2)) (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniPkSide) 1)))
    (:then
      (Funzionedichiamata|TrInsEn :A A :D _d))))))))
