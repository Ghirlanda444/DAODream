(fn FillBehavs ()
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniStage) 6)
    (:then
        (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniTBehavNames)) 1)
    (:LoopBody
      (Funzionedichiamata|AddBehavOpt :K _index))))))
