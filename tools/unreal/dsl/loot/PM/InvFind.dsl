(fn InvFind (Item)
  (Variabili|Predefinito|ImpostaInvAt -1)
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniInv)) 1)
    (:LoopBody
      (Funzionedichiamata|InvFindOne :K _index :Item Item))))
