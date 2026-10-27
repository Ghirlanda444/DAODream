(fn TrB25 ()
  (Variabili|Predefinito|ImpostaPkN 0)
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniEnAll)) 1)
    (:LoopBody
      (Funzionedichiamata|TrCntAtkEnAll :K _index))
    (:Completed
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniPkN) (Utilità|Array|Length (Variabili|Predefinito|OttieniEnAll)))
    (:then
      (Variabili|Predefinito|ImpostaPkWho (Variabili|Predefinito|OttieniTMe)))))))
