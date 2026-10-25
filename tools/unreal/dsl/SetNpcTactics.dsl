(fn SetNpcTactics (InTactics K)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggioreuguale(>=) (Utilità|Array|Length InTactics) (Utility|Operatori|Moltiplica (Utility|Operatori|Aggiungi K 1) 72))
    (:then
      (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex 71
        (:LoopBody
          (Funzionedichiamata|CopyTactic :InTactics InTactics :I _index :K (Utility|Operatori|Moltiplica K 72)))
        (:Completed
          (Funzionedichiamata|ClearSlots))))))
