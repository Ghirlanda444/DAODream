(fn TrB22 ()
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTT) 1.0)
    (:then
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniEnL)) 1)
    (:LoopBody
      (Funzionedichiamata|TrAtkSelf :K _index))))
    (:else
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTT) 3.0)
    (:then
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniEnL)) 1)
    (:LoopBody
      (Funzionedichiamata|TrAtkEn :K _index))))
    (:else
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTT) 2.0)
    (:then
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniAllyL)) 1)
    (:LoopBody
      (Funzionedichiamata|TrAtkAl :K _index))))
    (:else
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTT) 7.0)
    (:then
      (Funzionedichiamata|TrAtkHated))
    (:else
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Utilità|Array|Length (Variabili|Predefinito|OttieniCL)) 0)
    (:then
      (Variabili|Predefinito|ImpostaPkMem (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniCL) 0))
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniEnL)) 1)
    (:LoopBody
      (Funzionedichiamata|TrAtkMem :K _index))))))))))))))
