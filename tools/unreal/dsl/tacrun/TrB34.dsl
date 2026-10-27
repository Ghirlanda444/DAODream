(fn TrB34 ()
  (Funzionedichiamata|TrPeek :A (Variabili|Predefinito|OttieniTMe))
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Matematica|Booleano|ORBoolean (Matematica|Booleano|ANDBoolean (Utility|Operatori|Minore(<) (Variabili|Predefinito|OttieniTP) 0.0) (Utility|Operatori|Minore(<) (Variabili|Predefinito|OttieniPkSta) (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniTP) -1.0))) (Matematica|Booleano|ANDBoolean (Utility|Operatori|Maggioreuguale(>=) (Variabili|Predefinito|OttieniTP) 0.0) (Utility|Operatori|Maggioreuguale(>=) (Variabili|Predefinito|OttieniPkSta) (Variabili|Predefinito|OttieniTP)))) (Matematica|Booleano|ORBoolean (Matematica|Booleano|ORBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTT) 2.0) (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTT) 3.0)) (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTT) 7.0)))
    (:then
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Utilità|Array|Length (Variabili|Predefinito|OttieniCL)) 0)
    (:then
      (Variabili|Predefinito|ImpostaPkWho (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniCL) 0)))))))
