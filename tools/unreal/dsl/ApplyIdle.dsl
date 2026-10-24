(fn ApplyIdle (Idle)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|NOTBoolean (Utilità|Stringa|IsEmpty Idle))
    (:then
      (bind _a (Utilità|Casting|CastToAnimationAsset (Utilità|LoadAssetBlocking (Utilità|ToSoftObjectReference (Utilità|MakeSoftObjectPath (Utilità|Stringa|Append (Utilità|Stringa|Append (Utilità|Stringa|Append "/Game/Cousland/Anims/" Idle) ".") Idle))))))
      (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid _a)
        (:then
          (Variabili|Predefinito|ImpostaIdleAnim _a)
          (Componenti|Animazione|PlayAnimation (Variabili|Predefinito|OttieniMesh) _a "true"))))))
