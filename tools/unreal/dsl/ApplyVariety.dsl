(fn ApplyVariety (V At)
  (bind _cls (Utilità|GetClassDisplayName (Utilità|GetClass (Variabili|Predefinito|OttieniLook))))
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Matematica|Booleano|ANDBoolean (Utilità|IsValid (Variabili|Predefinito|OttieniLook)) (Utility|Operatori|Maggiore(>) (Utilità|Array|Length V) (Utility|Operatori|Aggiungi At 10))) (Matematica|Booleano|ORBoolean (Utilità|Stringa|Contains _cls "MHC_Crowd") (Utilità|Stringa|Contains _cls "MHC_HoweSoldier")))
    (:then
      (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Utilità|Array|Ottieni(unacopia) V At) 0.0)
        (:then
          (bind _comps (Attore|GetComponentsByClass :self (Variabili|Predefinito|OttieniLook) :ComponentClass "/Script/Engine.MeshComponent"))
          (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length _comps) 1)
            (:LoopBody
              (bind _c (Utilità|Casting|CastToMeshComponent (Utilità|Array|Ottieni(unacopia) _comps _index)))
              (bind _n (Utilità|GetObjectName _c))
              (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Utilità|Stringa|EqualExactly(String) _n "Face") (Utilità|Stringa|EqualExactly(String) _n "Body"))
                (:then
                  (Rendering|Materiale|SetVectorParameterValueonMaterials _c "Basecolor Global Multiply Post-Bake" (Matematica|Vettore|MakeVector (Utilità|Array|Ottieni(unacopia) V At) (Utilità|Array|Ottieni(unacopia) V (Utility|Operatori|Aggiungi At 1)) (Utilità|Array|Ottieni(unacopia) V (Utility|Operatori|Aggiungi At 2)))))
                (:else
                  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Utilità|Casting|CastToGroomComponent _c))
                    (:then
                      (Rendering|Materiale|SetScalarParameterValueonMaterials _c "hairMelanin" (Utilità|Array|Ottieni(unacopia) V (Utility|Operatori|Aggiungi At 3)))
                      (Rendering|Materiale|SetScalarParameterValueonMaterials _c "hairRedness" (Utilità|Array|Ottieni(unacopia) V (Utility|Operatori|Aggiungi At 4))))))))
            (:Completed
              (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Utilità|Array|Ottieni(unacopia) V (Utility|Operatori|Aggiungi At 5)) 0.0)
                (:then
                  (Funzionedichiamata|DyeSlot :Slot "Main" :V V :At (Utility|Operatori|Aggiungi At 5))
                  (Funzionedichiamata|DyeSlot :Slot "Second" :V V :At (Utility|Operatori|Aggiungi At 8)))))))))))
