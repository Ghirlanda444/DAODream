(fn FillActs ()
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniStage) 4)
    (:then
      (Utilità|Array|Add (Variabili|Predefinito|OttieniOptIds) -1)
      (Utilità|Array|Add (Variabili|Predefinito|OttieniOptNames) (Variabili|Predefinito|OttieniAttackName))
      (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniTalNames)) 1)
  (:LoopBody
    (Funzionedichiamata|AddActOpt :K _index))))))
