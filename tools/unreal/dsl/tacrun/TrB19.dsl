(fn TrB19 ()
  (Variabili|Predefinito|ImpostaPkN 0)
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniEnAll)) 1)
    (:LoopBody
      (Funzionedichiamata|TrCntArmorEnAll :K _index))
    (:Completed
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggioreuguale(>=) (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniPkN) 2) (Utilità|Array|Length (Variabili|Predefinito|OttieniEnAll)))
    (:then
      (Variabili|Predefinito|ImpostaPkWho (Variabili|Predefinito|OttieniTMe)))))))
