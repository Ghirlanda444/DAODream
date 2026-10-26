(fn OrderOnTarget ()
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Classe|BPDlgNPC|OttieniOrderTarget (Variabili|Predefinito|OttieniSelected)))
    (:else
      (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniBestTarget))
        (:then
          (Classe|BPDlgNPC|OrderAttack (Variabili|Predefinito|OttieniSelected) :Foe (Utilità|Casting|CastToBP_DlgNPC (Variabili|Predefinito|OttieniBestTarget))))))))
