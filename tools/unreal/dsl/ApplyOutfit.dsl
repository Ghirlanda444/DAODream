(fn ApplyOutfit (Chest)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utilità|IsValid (Variabili|Predefinito|OttieniLook)) (Matematica|Booleano|NOTBoolean (Utilità|Stringa|IsEmpty Chest)))
    (:then
      (bind _comps (Attore|GetComponentsByClass :self (Variabili|Predefinito|OttieniLook) :ComponentClass "/Script/Engine.SkeletalMeshComponent"))
      (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length _comps) 1)
        (:LoopBody
          (bind _c (Utilità|Casting|CastToSkeletalMeshComponent (Utilità|Array|Ottieni(unacopia) _comps _index)))
          (bind _n (Utilità|GetObjectName _c))
          (Utilità|ControlloDiFlusso|Ramo (Utilità|Stringa|EqualExactly(String) _n "Body")
            (:then
              (Variabili|Predefinito|ImpostaLookName (Utilità|Stringa|Replace (Utilità|Stringa|Replace (Utilità|GetObjectName (Componenti|SkeletalMesh|GetSkeletalMeshAsset _c)) "SKM_MHC_" "") "_BodyMesh" "")))
            (:else
              (Utilità|ControlloDiFlusso|Ramo (Utilità|Stringa|EqualExactly(String) _n "SkeletalMesh")
                (:then (Variabili|Predefinito|ImpostaOutfitComp _c))))))
        (:Completed
          (bind _stem (Utilità|Stringa|Append (Utilità|Stringa|Append (Utilità|Stringa|Append "SKM_" (Variabili|Predefinito|OttieniLookName)) "_") Chest))
          (bind _m (Utilità|Casting|CastToSkeletalMesh (Utilità|LoadAssetBlocking (Utilità|ToSoftObjectReference (Utilità|MakeSoftObjectPath (Utilità|Stringa|Append (Utilità|Stringa|Append (Utilità|Stringa|Append (Utilità|Stringa|Append (Utilità|Stringa|Append "/Game/MetaHumans/MHC_" (Variabili|Predefinito|OttieniLookName)) "/DAO/") _stem) ".") _stem))))))
          (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utilità|IsValid _m) (Utilità|IsValid (Variabili|Predefinito|OttieniOutfitComp)))
            (:then
              (Componenti|SkinnedMesh|SetSkinnedAssetandUpdate (Variabili|Predefinito|OttieniOutfitComp) _m "false")
              (Rendering|Materiale|SetMaterial (Variabili|Predefinito|OttieniOutfitComp) 0 "None")
              (Rendering|Materiale|SetMaterial (Variabili|Predefinito|OttieniOutfitComp) 1 "None")
              (Rendering|Materiale|SetMaterial (Variabili|Predefinito|OttieniOutfitComp) 2 "None")
              (Rendering|Materiale|SetMaterial (Variabili|Predefinito|OttieniOutfitComp) 3 "None"))))))))
