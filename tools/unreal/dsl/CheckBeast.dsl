(fn CheckBeast (Who)
  (Variabili|Predefinito|ImpostaBeastFoe "false")
  (bind _npc (Utilità|Casting|CastToBP_DlgNPC Who))
  (Funzionedichiamata|CheckBeastLook :Look (Classe|BPDlgNPC|OttieniLook _npc)))
