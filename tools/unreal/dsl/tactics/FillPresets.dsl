(fn FillPresets ()
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniStage) 5)
    (:then
        (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniTPresetNames)) 1)
    (:LoopBody
      (Funzionedichiamata|AddPresetOpt :K _index))))))
