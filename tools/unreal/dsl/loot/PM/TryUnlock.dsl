(fn TryUnlock (Box)
  (Variabili|Predefinito|ImpostaGBool "false")
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniInv)) 1)
    (:LoopBody
      (Funzionedichiamata|KeyOne :K _index :Box Box))
    (:Completed
      (Funzionedichiamata|TryUnlock2 :Box Box))))
