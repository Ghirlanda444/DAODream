(fn StrikeNpcFoe ()
  (bind _npc (Utilità|Casting|CastToBP_DlgNPC (Variabili|Predefinito|OttieniFoe)))
  (Funzionedichiamata|TakeStrike _npc :Attacker (Variabili|Ottieniunriferimentoasestesso) :InAttack (Variabili|Predefinito|OttieniAttack) :InMin (Variabili|Predefinito|OttieniDmgMin) :InMax (Variabili|Predefinito|OttieniDmgMax) :InScale (Variabili|Predefinito|OttieniDmgScale) :InCrit (Variabili|Predefinito|OttieniCrit) :InPen (Variabili|Predefinito|OttieniPen) :InBonus (Variabili|Predefinito|OttieniDmgBonus) :InFlank (Variabili|Predefinito|OttieniFlank)))
