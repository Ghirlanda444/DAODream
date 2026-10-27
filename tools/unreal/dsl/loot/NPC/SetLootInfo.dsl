(fn SetLootInfo (InLoot InBag K)
  (Utilità|Array|Clear (Variabili|Predefinito|OttieniNLoot))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggioreuguale(>=) (Utilità|Array|Length InLoot) (Utility|Operatori|Moltiplica (Utility|Operatori|Aggiungi K 1) 9))
    (:then
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex 8
    (:LoopBody
      (Funzionedichiamata|LootOne :InLoot InLoot :K K :J _index))))))
