(fn ApplyCoat (V At)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utilità|IsValid (Variabili|Predefinito|OttieniLook)) (Utility|Operatori|Maggiore(>) (Utilità|Array|Length V) (Utility|Operatori|Aggiungi At 4)))
    (:then
      (bind _comps (Attore|GetComponentsByClass :self (Variabili|Predefinito|OttieniLook) :ComponentClass "/Script/Engine.PrimitiveComponent"))
      (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length _comps) 1)
        (:LoopBody
          (bind _c (Utilità|Casting|CastToPrimitiveComponent (Utilità|Array|Ottieni(unacopia) _comps _index)))
          (Rendering|Materiale|SetCustomPrimitiveDataFloat _c 0 (Utilità|Array|Ottieni(unacopia) V At))
          (Rendering|Materiale|SetCustomPrimitiveDataFloat _c 1 (Utilità|Array|Ottieni(unacopia) V (Utility|Operatori|Aggiungi At 1)))
          (Rendering|Materiale|SetCustomPrimitiveDataFloat _c 2 (Utilità|Array|Ottieni(unacopia) V (Utility|Operatori|Aggiungi At 2)))
          (Rendering|Materiale|SetCustomPrimitiveDataFloat _c 3 (Utilità|Array|Ottieni(unacopia) V (Utility|Operatori|Aggiungi At 3)))
          (Rendering|Materiale|SetCustomPrimitiveDataFloat _c 4 (Utilità|Array|Ottieni(unacopia) V (Utility|Operatori|Aggiungi At 4))))))))
