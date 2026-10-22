(fn HeadOf (A)
  (bind _c (Utilità|Casting|CastToCharacter :Object A)
    (:then
      (Variabili|Predefinito|ImpostaTmpHead (Trasformazione|GetSocketLocation (Classe|Personaggio|OttieniMesh _c) "head")))
    (:CastFailed
      (bind _npc (Utilità|Casting|CastToBP_DlgNPC :Object A)
        (:then
          (Variabili|Predefinito|ImpostaTmpHead (Trasformazione|GetSocketLocation (Classe|BPDlgNPC|OttieniMesh _npc) "head"))
          (Funzionedichiamata|DogHead :A A))
        (:CastFailed)))))
