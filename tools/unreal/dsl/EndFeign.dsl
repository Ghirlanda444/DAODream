(fn EndFeign ()
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniFeign)
    (:then
      (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniTalentNames)) 1)
        (:LoopBody
          (Funzionedichiamata|EndFeignSlot :Slot _index))))))
