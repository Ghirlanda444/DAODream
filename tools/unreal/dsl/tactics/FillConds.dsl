(fn FillConds ()
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniStage) 3)
    (:then
      (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniTCondNames)) 1)
  (:LoopBody
    (Funzionedichiamata|AddCondOpt :K _index))))))
