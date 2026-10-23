(fn HideHair ()
  (bind _g (Attore|GetComponentsByClass :self (Variabili|Predefinito|OttieniLook) :ComponentClass "/Script/HairStrandsCore.GroomComponent"))
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length _g) 1)
    (:LoopBody
      (bind _c (Utilità|Casting|CastToGroomComponent (Utilità|Array|Ottieni(unacopia) _g _index)))
      (Utilità|ControlloDiFlusso|Ramo (Utilità|Stringa|EqualExactly(String) (Utilità|GetObjectName _c) "Hair")
        (:then (Rendering|SetVisibility _c "false" "false"))))))
