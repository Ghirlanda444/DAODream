(fn HealAnyCast (A)
  (bind _n (Utilità|Casting|CastToBP_DlgNPC A))
  (Classe|BPDlgNPC|GainHealth _n :Amount (Variabili|Predefinito|OttieniUseAmt)))
