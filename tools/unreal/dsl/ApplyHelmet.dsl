(fn ApplyHelmet (Helmet)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utilità|IsValid (Variabili|Predefinito|OttieniLook)) (Matematica|Booleano|NOTBoolean (Utilità|Stringa|IsEmpty Helmet)))
    (:then
      (bind _kind (Utilità|Stringa|SelectString "med_hel" Helmet (Utilità|Stringa|EqualExactly(String) Helmet "hvy_exc")))
      (bind _stem (Utilità|Stringa|Append "SM_Helmet_" _kind))
      (bind _m (Utilità|Casting|CastToStaticMesh (Utilità|LoadAssetBlocking (Utilità|ToSoftObjectReference (Utilità|MakeSoftObjectPath (Utilità|Stringa|Append (Utilità|Stringa|Append (Utilità|Stringa|Append "/Game/Cousland/Outfits/Helmets/" _stem) ".") _stem))))))
      (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid _m)
        (:then
          (bind _comps (Attore|GetComponentsByClass :self (Variabili|Predefinito|OttieniLook) :ComponentClass "/Script/Engine.SkeletalMeshComponent"))
          (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length _comps) 1)
            (:LoopBody
              (bind _c (Utilità|Casting|CastToSkeletalMeshComponent (Utilità|Array|Ottieni(unacopia) _comps _index)))
              (Utilità|ControlloDiFlusso|Ramo (Utilità|Stringa|EqualExactly(String) (Utilità|GetObjectName _c) "Face")
                (:then (Funzionedichiamata|AttachHelmet :Face _c :Mesh _m))))
            (:Completed (Funzionedichiamata|HideHair))))))))
