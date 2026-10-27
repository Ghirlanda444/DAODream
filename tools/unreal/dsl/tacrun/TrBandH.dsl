(fn TrBandH ()
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniTMeHated))
    (:then
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Matematica|Booleano|ORBoolean (Matematica|Booleano|ANDBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTP) 1.0) (Utility|Operatori|Minoreuguale(<=) (Trasformazione|GetHorizontalDistanceTo (Variabili|Predefinito|OttieniTMe) (Variabili|Predefinito|OttieniTMeHated)) 350.0)) (Matematica|Booleano|ANDBoolean (Matematica|Booleano|ANDBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTP) 2.0) (Utility|Operatori|Maggiore(>) (Trasformazione|GetHorizontalDistanceTo (Variabili|Predefinito|OttieniTMe) (Variabili|Predefinito|OttieniTMeHated)) 350.0)) (Utility|Operatori|Minoreuguale(<=) (Trasformazione|GetHorizontalDistanceTo (Variabili|Predefinito|OttieniTMe) (Variabili|Predefinito|OttieniTMeHated)) 1200.0))) (Matematica|Booleano|ANDBoolean (Matematica|Booleano|ANDBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTP) 3.0) (Utility|Operatori|Maggiore(>) (Trasformazione|GetHorizontalDistanceTo (Variabili|Predefinito|OttieniTMe) (Variabili|Predefinito|OttieniTMeHated)) 1200.0)) (Utility|Operatori|Minoreuguale(<=) (Trasformazione|GetHorizontalDistanceTo (Variabili|Predefinito|OttieniTMe) (Variabili|Predefinito|OttieniTMeHated)) 8000.0)))
    (:then
      (Variabili|Predefinito|ImpostaPkWho (Variabili|Predefinito|OttieniTMeHated))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTT) 1.0)
    (:then
      (Variabili|Predefinito|ImpostaPkWho (Variabili|Predefinito|OttieniTMe)))))))))
