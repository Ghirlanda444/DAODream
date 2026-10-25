(fn ToggleHold ()
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniSelected))
    (:then
      (Classe|BPDlgNPC|SetHold (Variabili|Predefinito|OttieniSelected) :bOn (Matematica|Booleano|NOTBoolean (Classe|BPDlgNPC|OttieniHold (Variabili|Predefinito|OttieniSelected))))
      (Classe|BPDlgNPC|MakeOrderLine (Variabili|Predefinito|OttieniSelected))
      (Variabili|Predefinito|ImpostaSelLine (Classe|BPDlgNPC|OttieniOrderLine (Variabili|Predefinito|OttieniSelected)))
      (Funzionedichiamata|ShowTalents))
    (:else
      (Variabili|Predefinito|ImpostaHoldAll (Matematica|Booleano|NOTBoolean (Variabili|Predefinito|OttieniHoldAll)))
      (bind _all (Attore|GetAllActorsOfClass "/Game/Cousland/Dialogue/BP_DlgNPC.BP_DlgNPC_C"))
      (for _a _all
        (Classe|BPDlgNPC|SetHold _a :bOn (Variabili|Predefinito|OttieniHoldAll)))
      (Funzionedichiamata|ShowMsg :Txt (Utilità|Stringa|SelectString "Party: hold position" "Party: follow" (Variabili|Predefinito|OttieniHoldAll))))))
