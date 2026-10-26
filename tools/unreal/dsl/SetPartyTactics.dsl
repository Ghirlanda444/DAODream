(fn SetPartyTactics (InTactics K Slots)
  (Variabili|Predefinito|ImpostaTacticSlots Slots)
  (Utilità|Array|Clear (Variabili|Predefinito|OttieniPartyTactics))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggioreuguale(>=) (Utilità|Array|Length InTactics) (Utility|Operatori|Moltiplica (Utility|Operatori|Aggiungi K 1) 240))
    (:then
      (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex 239
        (:LoopBody
          (Funzionedichiamata|CopyPartyTactic :InTactics InTactics :I _index :K (Utility|Operatori|Moltiplica K 240)))))))
