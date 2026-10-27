(fn TrEngage ()
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniTMeParty)
    (:then
      (Variabili|Predefinito|ImpostaPkN (Utilità|Array|Length (Variabili|Predefinito|OttieniEnL)))
      (Variabili|Predefinito|ImpostaTReach (Matematica|Float|SelectFloat 3000.0 1500.0 (Variabili|Predefinito|OttieniTMeChase)))
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniEnL)) 1)
    (:LoopBody
      (Funzionedichiamata|TrEngOne :K _index))
    (:Completed
      (Utilità|Array|Resize (Variabili|Predefinito|OttieniEnL) (Variabili|Predefinito|OttieniPkN))
      (Utilità|Array|Resize (Variabili|Predefinito|OttieniEnD) (Variabili|Predefinito|OttieniPkN)))))))
