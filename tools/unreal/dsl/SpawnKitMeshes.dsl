(fn SpawnKitMeshes ()
  (Funzionedichiamata|CreateKitISMs)
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utility|Operatori|Dividi (Utilità|Array|Length (Variabili|Predefinito|OttieniKitPlaced)) 13) 1)
    (:LoopBody
      (Funzionedichiamata|PlaceKitPiece :B (Utility|Operatori|Moltiplica _index 13)))))
