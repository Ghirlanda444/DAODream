(fn TrAtkEn (K)
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniPkWho))
    (:else
      (Variabili|Predefinito|ImpostaPkMem (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniEnL) K))
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniAllyL)) 1)
    (:LoopBody
      (Funzionedichiamata|TrAtkEnA :K _index))))))
