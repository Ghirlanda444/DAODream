(fn TrB7 ()
  (Funzionedichiamata|TrOwn)
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniPkWho))
    (:else
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTT) 2.0) (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTT) 3.0))
    (:then
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniCL)) 1)
    (:LoopBody
      (Funzionedichiamata|TrTryRace :K _index))))))))
