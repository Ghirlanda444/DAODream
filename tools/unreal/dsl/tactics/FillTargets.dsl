(fn FillTargets ()
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniStage) 1)
    (:then
      (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniTTargetNames)) 1)
  (:LoopBody
    (Funzionedichiamata|AddTargetOpt :K _index))))))
