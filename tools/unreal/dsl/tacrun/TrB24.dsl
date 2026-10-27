(fn TrB24 ()
  (Variabili|Predefinito|ImpostaPkN 0)
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniEnL)) 1)
    (:LoopBody
      (Funzionedichiamata|TrCntAtkEnL :K _index))
    (:Completed
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniPkN) (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniEnL)) (Variabili|Predefinito|OttieniPkN)))
    (:then
      (Variabili|Predefinito|ImpostaPkWho (Variabili|Predefinito|OttieniTMe)))))))
