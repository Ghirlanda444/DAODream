(fn TrB6 ()
  (Funzionedichiamata|TrOwn)
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniPkWho))
    (:else
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Matematica|Booleano|ANDBoolean (Matematica|Booleano|ORBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTT) 2.0) (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTT) 3.0)) (Utility|Operatori|Maggioreuguale(>=) (Variabili|Predefinito|OttieniTP) 1.0)) (Utility|Operatori|Minoreuguale(<=) (Variabili|Predefinito|OttieniTP) (Matematica|Conversioni|ToFloat(Integer) (Utilità|Array|Length (Variabili|Predefinito|OttieniCL)))))
    (:then
      (Variabili|Predefinito|ImpostaPkWho (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniCL) (Utility|Operatori|Sottrai (Matematica|Float|Truncate (Variabili|Predefinito|OttieniTP)) 1))))))))
