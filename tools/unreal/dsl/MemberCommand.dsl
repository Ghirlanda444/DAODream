(fn MemberCommand (Where)
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniPickNpc))
    (:then
      (Utilità|ControlloDiFlusso|Ramo (Classe|BPDlgNPC|OttieniHostile (Variabili|Predefinito|OttieniPickNpc))
        (:then
          (Classe|BPDlgNPC|OrderAttack (Variabili|Predefinito|OttieniSelected) :Foe (Variabili|Predefinito|OttieniPickNpc))
          (Funzionedichiamata|ShowMsg :Txt (Utilità|Stringa|Append "Attack: " (Classe|BPDlgNPC|OttieniDisplayName (Variabili|Predefinito|OttieniPickNpc)))))
        (:else
          (Classe|BPDlgNPC|OrderMoveTo (Variabili|Predefinito|OttieniSelected) :Goal Where))))
    (:else
      (Classe|BPDlgNPC|OrderMoveTo (Variabili|Predefinito|OttieniSelected) :Goal Where))))
