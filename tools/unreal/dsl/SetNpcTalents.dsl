(fn SetNpcTalents (InTalents InTactics K)
  (Utilità|Array|Clear (Variabili|Predefinito|OttieniNTalents))
  (Utilità|Array|Clear (Variabili|Predefinito|OttieniNTactics))
  (Utilità|Array|Clear (Variabili|Predefinito|OttieniNReady))
  (Utilità|Array|Clear (Variabili|Predefinito|OttieniNOn))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggioreuguale(>=) (Utilità|Array|Length InTalents) (Utility|Operatori|Moltiplica (Utility|Operatori|Aggiungi K 1) 108))
    (:then
      (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex 107
        (:LoopBody
          (Funzionedichiamata|CopyTalent :InTalents InTalents :I _index :K (Utility|Operatori|Moltiplica K 108)))
        (:Completed
          (Funzionedichiamata|SetNpcTactics :InTactics InTactics :K K))))))
