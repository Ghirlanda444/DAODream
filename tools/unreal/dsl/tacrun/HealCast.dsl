(fn HealCast (A)
  (bind _n (Utilità|Casting|CastToBP_DlgNPC A))
  (Funzionedichiamata|GainHealth _n :Amount (Variabili|Predefinito|OttieniHealAmt)))
