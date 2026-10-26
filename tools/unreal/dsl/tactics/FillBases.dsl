(fn FillBases ()
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniStage) 2)
    (:then
      (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniTBaseNames)) 1)
  (:LoopBody
    (Funzionedichiamata|AddBaseOpt :K _index))))))
