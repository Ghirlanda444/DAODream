(fn StrikeNpc (Attacker Target Atk Def DmgMin DmgMax Scale Crit Pen Bonus Flank Armour)
  (Funzionedichiamata|AttackerState :Attacker Attacker)
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniAStunned)
    (:then
      (Variabili|Predefinito|ImpostaLastDamage -1.0))
    (:else
      (Funzionedichiamata|StrikeNpcGo :Attacker Attacker :Target Target :Atk (Utility|Operatori|Sottrai Atk (Variabili|Predefinito|OttieniAPen)) :Def Def :DmgMin DmgMin :DmgMax DmgMax :Scale Scale :Crit Crit :Pen Pen :Bonus Bonus :Flank Flank :Armour Armour))))
