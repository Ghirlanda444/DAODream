(fn OrderAttack ()
  (Funzionedichiamata|FindOrderTarget)
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniBestTarget))
    (:then
      (Classe|BPDlgNPC|OrderAttack (Variabili|Predefinito|OttieniSelected) :Foe (Utilità|Casting|CastToBP_DlgNPC (Variabili|Predefinito|OttieniBestTarget)))
      (Funzionedichiamata|ShowMsg :Txt (Utilità|Stringa|Append (Classe|BPDlgNPC|OttieniDisplayName (Variabili|Predefinito|OttieniSelected)) ": attack")))
    (:else
      (Funzionedichiamata|ShowMsg :Txt "No target in reach"))))
