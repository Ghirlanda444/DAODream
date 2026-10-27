(fn SetTraits (InTraits K)
  (Variabili|Predefinito|ImpostaNIndex K)
  (Utilità|Array|Clear (Variabili|Predefinito|OttieniNTraits))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggioreuguale(>=) (Utilità|Array|Length InTraits) (Utility|Operatori|Moltiplica (Utility|Operatori|Aggiungi K 1) 5))
    (:then
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex 4
    (:LoopBody
      (Funzionedichiamata|TraitOne :InTraits InTraits :I _index :K K))))))
