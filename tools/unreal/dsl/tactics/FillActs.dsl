(fn FillActs ()
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniStage) 4)
    (:then
        (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utility|Operatori|Dividi (Utilità|Array|Length (Variabili|Predefinito|OttieniTCmds)) (Utility|Operatori|Aggiungi (Utilità|Array|Length (Variabili|Predefinito|OttieniTTargetNames)) 1)) 1)
    (:LoopBody
      (Funzionedichiamata|AddCmdOpts :K _index))))))
