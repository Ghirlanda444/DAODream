(fn LootAll ()
  (Funzionedichiamata|LootMoney)
  (Variabili|Predefinito|ImpostaGN (Utilità|Array|Length (Classe|BPContainer|OttieniLItems (Variabili|Predefinito|OttieniLootBox))))
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Variabili|Predefinito|OttieniGN) 1)
    (:LoopBody
      (Funzionedichiamata|LootTake :K 0))
    (:Completed
      (Funzionedichiamata|CloseLoot))))
