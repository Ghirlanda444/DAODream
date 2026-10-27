(fn TrB3 ()
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTT) 2.0) (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTT) 3.0))
    (:then
      (Variabili|Predefinito|ImpostaPkBest (Matematica|Float|SelectFloat 1000000000.0 0.0 (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTP) 0.0)))
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniCL)) 1)
    (:LoopBody
      (Funzionedichiamata|TrTryLow :K _index))))))
