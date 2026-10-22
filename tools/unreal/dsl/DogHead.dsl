(fn DogHead (A)
  (bind _npc (Utilità|Casting|CastToBP_DlgNPC A))
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid _npc)
    (:then
      (bind _look (Classe|BPDlgNPC|OttieniLook _npc))
      (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid _look)
        (:then
          (Utilità|ControlloDiFlusso|Ramo (Utilità|Stringa|Contains (Utilità|GetClassDisplayName (Utilità|GetClass _look)) "Mabari")
            (:then
              (Variabili|Predefinito|ImpostaTmpHead (Trasformazione|GetSocketLocation (Attore|GetComponentByClass :self _look :ComponentClass "/Script/Engine.SkeletalMeshComponent") "Wolf_-Head")))))))))
