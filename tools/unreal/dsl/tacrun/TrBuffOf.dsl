(fn TrBuffOf (A)
  (Variabili|Predefinito|ImpostaPkBuff "false")
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) A (Gioco|GetPlayerPawn 0))
    (:then
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniTalentNames)) 1)
    (:LoopBody
      (Funzionedichiamata|TrBuffP :K _index))))
    (:else
      (Funzionedichiamata|TrBuffCast :A A))))
